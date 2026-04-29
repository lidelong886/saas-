"""
从高德地图 POI 搜索导入指定城市的换电站点。

用法示例：
  set AMAP_WEB_KEY=你的高德Web服务Key
  python scripts/import_amap_stations.py --city 石家庄 --limit 30 --commit
"""
import argparse
import hashlib
import os
import sys
from datetime import datetime

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Station


AMAP_TEXT_SEARCH_URL = 'https://restapi.amap.com/v3/place/text'
DEFAULT_KEYWORDS = [
    '换电站',
    '电动车换电',
    '电瓶车换电',
    '铁塔换电',
    'e换电',
    '哈啰换电',
    '小哈换电',
    '中国铁塔换电',
]


def parse_args():
    parser = argparse.ArgumentParser(description='导入高德地图 POI 换电站点')
    parser.add_argument('--key', default=os.getenv('AMAP_WEB_KEY'), help='高德 Web 服务 API Key，也可用 AMAP_WEB_KEY 环境变量')
    parser.add_argument('--city', default='石家庄', help='城市名称/citycode/adcode，默认：石家庄')
    parser.add_argument('--tenant-id', type=int, default=1, help='导入到哪个租户，默认：1')
    parser.add_argument('--limit', type=int, default=50, help='最多导入多少个去重后的站点，默认：50')
    parser.add_argument('--offset', type=int, default=20, help='每页条数，建议不超过 25，默认：20')
    parser.add_argument('--pages', type=int, default=5, help='每个关键词最多翻几页，默认：5')
    parser.add_argument('--keywords', default=','.join(DEFAULT_KEYWORDS), help='逗号分隔的搜索关键词')
    parser.add_argument('--commit', action='store_true', help='真正写入数据库；不加则只预览')
    return parser.parse_args()


def normalize_value(value):
    if isinstance(value, list):
        return value[0] if value else ''
    return value or ''


def station_code_from_poi(poi_id, name, location):
    raw = poi_id or f'{name}:{location}'
    digest = hashlib.md5(raw.encode('utf-8')).hexdigest()[:10].upper()
    return f'SJZ{digest}'


def parse_location(location):
    lng, lat = str(location).split(',', 1)
    return float(lat), float(lng)


def fetch_pois(key, city, keyword, pages, offset):
    pois = []
    for page in range(1, pages + 1):
        params = {
            'key': key,
            'keywords': keyword,
            'city': city,
            'citylimit': 'true',
            'children': 1,
            'offset': min(max(offset, 1), 25),
            'page': page,
            'extensions': 'all',
            'output': 'json',
        }
        response = requests.get(AMAP_TEXT_SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        if payload.get('status') != '1':
            raise RuntimeError(f"高德请求失败 keyword={keyword} page={page}: {payload.get('info')} {payload.get('infocode')}")
        page_pois = payload.get('pois') or []
        if not page_pois:
            break
        pois.extend(page_pois)
        if len(page_pois) < params['offset']:
            break
    return pois


def build_station_data(poi, tenant_id):
    name = normalize_value(poi.get('name')).strip()
    address = normalize_value(poi.get('address')).strip() or name
    location = normalize_value(poi.get('location')).strip()
    if not name or not location or ',' not in location:
        return None

    latitude, longitude = parse_location(location)
    business_area = normalize_value(poi.get('business_area')).strip()
    city = normalize_value(poi.get('cityname')).strip() or '石家庄'
    district = normalize_value(poi.get('adname')).strip()
    phone = normalize_value(poi.get('tel')).split(';')[0].strip()[:20]

    return {
        'station_code': station_code_from_poi(normalize_value(poi.get('id')), name, location),
        'name': name,
        'type': 'street',
        'status': 'active',
        'latitude': latitude,
        'longitude': longitude,
        'address': address if not business_area else f'{address}（{business_area}）',
        'city': city,
        'district': district,
        'phone': phone or None,
        'business_hours': '以实际营业时间为准',
        'is_24_hour': False,
        'total_cabinets': 1,
        'total_slots': 12,
        'available_slots': 8,
        'total_batteries': 8,
        'available_batteries': 6,
        'charging_batteries': 2,
        'network_status': True,
        'last_heartbeat': datetime.now(),
        'firmware_version': 'imported-amap',
        'images': [],
        'tenant_id': tenant_id,
    }


def find_existing_station(data):
    return Station.query.filter(
        Station.tenant_id == data['tenant_id'],
        Station.is_deleted == False,
        (
            (Station.station_code == data['station_code']) |
            ((Station.name == data['name']) & (Station.address == data['address']))
        )
    ).first()


def import_stations(args):
    if not args.key:
        raise SystemExit('缺少高德 Web 服务 Key：请设置 AMAP_WEB_KEY 或传 --key')

    keywords = [item.strip() for item in args.keywords.split(',') if item.strip()]
    app = create_app()

    with app.app_context():
        collected = {}
        for keyword in keywords:
            pois = fetch_pois(args.key, args.city, keyword, args.pages, args.offset)
            print(f'关键词「{keyword}」抓到 {len(pois)} 条')
            for poi in pois:
                data = build_station_data(poi, args.tenant_id)
                if not data:
                    continue
                dedupe_key = f"{data['name']}|{round(float(data['latitude']), 6)}|{round(float(data['longitude']), 6)}"
                collected.setdefault(dedupe_key, data)
                if len(collected) >= args.limit:
                    break
            if len(collected) >= args.limit:
                break

        created = 0
        skipped = 0
        for data in collected.values():
            if find_existing_station(data):
                skipped += 1
                print(f"跳过已存在：{data['name']} - {data['address']}")
                continue
            print(f"待导入：{data['name']} | {data['district']} | {data['address']} | {data['longitude']},{data['latitude']}")
            if args.commit:
                db.session.add(Station(**data))
            created += 1

        if args.commit:
            db.session.commit()
            print(f'导入完成：新增 {created} 个，跳过 {skipped} 个')
        else:
            db.session.rollback()
            print(f'预览完成：将新增 {created} 个，跳过 {skipped} 个。确认无误后加 --commit 写入数据库。')


if __name__ == '__main__':
    import_stations(parse_args())

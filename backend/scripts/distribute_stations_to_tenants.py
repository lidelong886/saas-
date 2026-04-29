"""
将现有站点均匀分配到所有启用租户，并保证每个站点至少有若干可用电池。

用法：
  python scripts/distribute_stations_to_tenants.py --min-batteries 3 --commit
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Battery, Station, Tenant


def parse_args():
    parser = argparse.ArgumentParser(description='均分站点到租户并补齐站点电池')
    parser.add_argument('--tenant-ids', default='', help='逗号分隔租户ID；默认使用所有启用租户')
    parser.add_argument('--min-batteries', type=int, default=3, help='每个站点至少保留几块可用公用电池，默认 3')
    parser.add_argument('--commit', action='store_true', help='真正写入数据库；不加仅预览')
    return parser.parse_args()


def get_tenants(args):
    query = Tenant.query.filter_by(status='active', is_deleted=False).order_by(Tenant.id.asc())
    if args.tenant_ids.strip():
      tenant_ids = [int(item.strip()) for item in args.tenant_ids.split(',') if item.strip()]
      query = query.filter(Tenant.id.in_(tenant_ids))
    return query.all()


def battery_code(station_id, index):
    return f'STZ{station_id:04d}{index:03d}'


def ensure_station_batteries(station, min_batteries):
    batteries = Battery.query.filter_by(current_station_id=station.id, is_deleted=False).order_by(Battery.id.asc()).all()
    reusable = [b for b in batteries if b.current_user_id is None and b.owner_id is None]

    changed = 0
    for battery in reusable[:min_batteries]:
        battery.tenant_id = station.tenant_id
        battery.status = 'available'
        battery.power_level = max(int(battery.power_level or 0), 80)
        changed += 1

    next_index = 1
    while len(reusable) < min_batteries:
        code = battery_code(station.id, next_index)
        next_index += 1
        if Battery.query.filter_by(battery_code=code, is_deleted=False).first():
            continue
        battery = Battery(
            battery_code=code,
            model='60V20Ah 标准电池',
            capacity=20000,
            voltage_type='60V',
            status='available',
            power_level=90,
            voltage=60.8,
            temperature=30.5,
            current_station_id=station.id,
            rental_price_per_hour=0.50,
            deposit_amount=50.00,
            tenant_id=station.tenant_id,
        )
        db.session.add(battery)
        reusable.append(battery)
        changed += 1

    total = Battery.query.filter_by(current_station_id=station.id, is_deleted=False).count()
    available = Battery.query.filter_by(
        current_station_id=station.id,
        status='available',
        owner_id=None,
        current_user_id=None,
        is_deleted=False,
    ).count()
    station.total_batteries = total
    station.available_batteries = available
    station.charging_batteries = max(0, total - available)
    station.total_cabinets = max(station.total_cabinets or 0, 1)
    station.total_slots = max(station.total_slots or 0, max(total + 4, 12))
    station.available_slots = max(station.available_slots or 0, max(station.total_slots - total, 0))
    return changed


def distribute(args):
    app = create_app()
    with app.app_context():
        tenants = get_tenants(args)
        if not tenants:
            raise SystemExit('没有可用租户')

        stations = Station.query.filter_by(is_deleted=False).order_by(Station.id.asc()).all()
        if not stations:
            raise SystemExit('没有可用站点')

        tenant_names = ', '.join([f'{t.id}:{t.name}' for t in tenants])
        print(f'参与分配租户：{tenant_names}')
        print(f'待分配站点：{len(stations)} 个，每站至少 {args.min_batteries} 块可用电池')

        touched_batteries = 0
        for index, station in enumerate(stations):
            tenant = tenants[index % len(tenants)]
            old_tenant_id = station.tenant_id
            station.tenant_id = tenant.id
            touched_batteries += ensure_station_batteries(station, args.min_batteries)

            station_batteries = Battery.query.filter_by(current_station_id=station.id, is_deleted=False).all()
            for battery in station_batteries:
                if battery.current_user_id is None and battery.owner_id is None:
                    battery.tenant_id = tenant.id

            print(f'站点 #{station.id} {station.name}: 租户 {old_tenant_id} -> {tenant.id}')

        if args.commit:
            db.session.commit()
            print(f'完成：已均分 {len(stations)} 个站点，新增/调整电池 {touched_batteries} 条')
        else:
            db.session.rollback()
            print('预览完成：未写入数据库。确认无误后加 --commit')


if __name__ == '__main__':
    distribute(parse_args())

"""
高德地图API工具
"""
import requests
import json


class AMapService:
    """高德地图服务"""

    @staticmethod
    def get_api_key():
        """获取API密钥（直接从 config 读取）"""
        from flask import current_app
        return current_app.config.get('AMAP_KEY', '')

    @staticmethod
    def search_places(keyword, city=None, page_size=20, page_num=1):
        """
        地点搜索
        """
        try:
            url = 'https://restapi.amap.com/v3/place/text'
            params = {
                'key': AMapService.get_api_key(),
                'keywords': keyword,
                'city': city,
                'page_size': page_size,
                'page_num': page_num,
                'output': 'json'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('status') == '1':
                return {
                    'success': True,
                    'data': data.get('pois', []),
                    'total': int(data.get('count', 0))
                }
            else:
                return {
                    'success': False,
                    'message': data.get('info', '搜索失败')
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'搜索失败: {str(e)}'
            }

    @staticmethod
    def get_place_detail(poi_id):
        """
        获取地点详情
        """
        try:
            url = 'https://restapi.amap.com/v3/place/detail'
            params = {
                'key': AMapService.get_api_key(),
                'id': poi_id,
                'output': 'json'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('status') == '1' and data.get('pois'):
                return {
                    'success': True,
                    'data': data['pois'][0]
                }
            else:
                return {
                    'success': False,
                    'message': data.get('info', '获取详情失败')
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'获取详情失败: {str(e)}'
            }

    @staticmethod
    def geocode(address, city=None):
        """
        地理编码（地址转坐标）
        """
        try:
            url = 'https://restapi.amap.com/v3/geocode/geo'
            params = {
                'key': AMapService.get_api_key(),
                'address': address,
                'city': city,
                'output': 'json'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('status') == '1' and data.get('geocodes'):
                geocode = data['geocodes'][0]
                location = geocode.get('location', '').split(',')
                return {
                    'success': True,
                    'data': {
                        'longitude': float(location[0]) if len(location) > 0 else 0,
                        'latitude': float(location[1]) if len(location) > 1 else 0,
                        'address': geocode.get('formatted_address', ''),
                        'province': geocode.get('province', ''),
                        'city': geocode.get('city', ''),
                        'district': geocode.get('district', '')
                    }
                }
            else:
                return {
                    'success': False,
                    'message': data.get('info', '地理编码失败')
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'地理编码失败: {str(e)}'
            }

    @staticmethod
    def reverse_geocode(longitude, latitude):
        """
        逆地理编码（坐标转地址）
        """
        try:
            url = 'https://restapi.amap.com/v3/geocode/regeo'
            params = {
                'key': AMapService.get_api_key(),
                'location': f'{longitude},{latitude}',
                'output': 'json'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('status') == '1' and data.get('regeocode'):
                regeocode = data['regeocode']
                return {
                    'success': True,
                    'data': {
                        'address': regeocode.get('formatted_address', ''),
                        'province': regeocode.get('addressComponent', {}).get('province', ''),
                        'city': regeocode.get('addressComponent', {}).get('city', ''),
                        'district': regeocode.get('addressComponent', {}).get('district', ''),
                        'township': regeocode.get('addressComponent', {}).get('township', '')
                    }
                }
            else:
                return {
                    'success': False,
                    'message': data.get('info', '逆地理编码失败')
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'逆地理编码失败: {str(e)}'
            }

    @staticmethod
    def calculate_distance(origin_lng, origin_lat, destination_lng, destination_lat):
        """
        计算两点间距离（直线距离）
        """
        try:
            # 使用Haversine公式计算球面距离
            import math

            R = 6371000  # 地球半径（米）

            # 转换为弧度
            lat1_rad = math.radians(origin_lat)
            lng1_rad = math.radians(origin_lng)
            lat2_rad = math.radians(destination_lat)
            lng2_rad = math.radians(destination_lng)

            dlat = lat2_rad - lat1_rad
            dlng = lng2_rad - lng1_rad

            a = (math.sin(dlat/2)**2 +
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

            distance = R * c

            return {
                'success': True,
                'distance': round(distance, 2),  # 米
                'distance_km': round(distance / 1000, 2)  # 公里
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'距离计算失败: {str(e)}'
            }

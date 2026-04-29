"""
站点服务
"""
from datetime import datetime
from flask import g
from ..models import Station, Cabinet, Battery
from .. import db
from sqlalchemy import func, case
import math

class StationService:
    """站点服务类"""

    @staticmethod
    def create_station(name, address, latitude, longitude, phone=None, business_hours=None, capacity=None):
        """
        创建站点
        
        Args:
            name: 站点名称
            address: 站点地址
            latitude: 纬度
            longitude: 经度
            phone: 联系电话
            business_hours: 营业时间
            capacity: 容量
        
        Returns:
            (success, result/error_message)
        """
        try:
            # 检查站点是否已存在
            existing = Station.query.filter_by(
                name=name,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).first()
            
            if existing:
                return False, "站点名称已存在"

            station = Station(
                name=name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                business_hours=business_hours,
                capacity=capacity,
                tenant_id=g.tenant_id
            )

            db.session.add(station)
            db.session.commit()

            return True, station.to_dict()

        except Exception as e:
            db.session.rollback()
            return False, f"创建站点失败: {str(e)}"

    @staticmethod
    def _format_distance(distance_km):
        meters = int(round(distance_km * 1000))
        if meters < 1000:
            return f'{meters}m'
        return f'{distance_km:.1f}km'

    @staticmethod
    def get_station_list(limit=80):
        try:
            stations = Station.query.filter(
                Station.tenant_id == g.tenant_id,
                Station.is_deleted == False
            ).order_by(Station.status.asc(), Station.created_at.desc()).limit(limit).all()
            if not stations:
                return []

            station_ids = [s.id for s in stations]
            battery_stats = db.session.query(
                Battery.current_station_id,
                Battery.voltage_type,
                func.count(Battery.id).label('total'),
                func.sum(case((Battery.status == 'available', 1), else_=0)).label('available')
            ).filter(
                Battery.current_station_id.in_(station_ids),
                Battery.is_deleted == False,
                Battery.tenant_id == g.tenant_id
            ).group_by(Battery.current_station_id, Battery.voltage_type).all()

            stats_map = {}
            for stat in battery_stats:
                station_id = stat.current_station_id
                voltage_type = stat.voltage_type or '60V'
                if station_id not in stats_map:
                    stats_map[station_id] = {'total': 0, 'available': 0, '60V_total': 0, '60V_available': 0, '72V_total': 0, '72V_available': 0}
                stats_map[station_id]['total'] += stat.total or 0
                stats_map[station_id]['available'] += int(stat.available or 0)
                if voltage_type == '60V':
                    stats_map[station_id]['60V_total'] = stat.total or 0
                    stats_map[station_id]['60V_available'] = int(stat.available or 0)
                elif voltage_type == '72V':
                    stats_map[station_id]['72V_total'] = stat.total or 0
                    stats_map[station_id]['72V_available'] = int(stat.available or 0)

            result = []
            for station in stations:
                station_data = station.to_dict()
                stat = stats_map.get(station.id, {'total': 0, 'available': 0, '60V_total': 0, '60V_available': 0, '72V_total': 0, '72V_available': 0})
                available_count = stat['available']
                station_data['available_batteries'] = available_count
                station_data['total_batteries'] = stat['total']
                station_data['battery_60V'] = {'total': stat['60V_total'], 'available': stat['60V_available']}
                station_data['battery_72V'] = {'total': stat['72V_total'], 'available': stat['72V_available']}
                if station.status != 'active':
                    station_data['health_status'] = 'maintenance'
                    station_data['health_label'] = '维护中'
                elif available_count == 0:
                    station_data['health_status'] = 'empty'
                    station_data['health_label'] = '暂无电池'
                elif available_count <= 2:
                    station_data['health_status'] = 'low'
                    station_data['health_label'] = '电池紧张'
                else:
                    station_data['health_status'] = 'good'
                    station_data['health_label'] = '电池充足'
                station_data['recommend_score'] = round(min(available_count / 5, 1) * 0.8 + (1 if station.status == 'active' else 0.25) * 0.2, 3)
                result.append(station_data)
            return result
        except Exception:
            return []

    @staticmethod
    def get_nearby_stations(latitude, longitude, radius_km=5):
        """
        获取附近站点（增强版：包含可用电池数和健康状态）

        Args:
            latitude: 用户纬度
            longitude: 用户经度
            radius_km: 搜索半径（公里）

        Returns:
            站点列表（含 available_batteries, total_batteries, health_status, recommend_score）
        """
        try:
            lat_range = radius_km / 111.0
            lng_range = radius_km / (111.0 * math.cos(math.radians(latitude))) if latitude != 0 else radius_km / 111.0

            stations = Station.query.filter(
                Station.tenant_id == g.tenant_id,
                Station.is_deleted == False,
                Station.latitude.between(latitude - lat_range, latitude + lat_range),
                Station.longitude.between(longitude - lng_range, longitude + lng_range)
            ).all()

            if not stations:
                return []

            # 步骤9：批量查询所有站点的电池统计（避免 N+1 问题）
            station_ids = [s.id for s in stations]
            battery_stats = db.session.query(
                Battery.current_station_id,
                Battery.voltage_type,
                func.count(Battery.id).label('total'),
                func.sum(case((Battery.status == 'available', 1), else_=0)).label('available')
            ).filter(
                Battery.current_station_id.in_(station_ids),
                Battery.is_deleted == False,
                Battery.tenant_id == g.tenant_id
            ).group_by(Battery.current_station_id, Battery.voltage_type).all()

            stats_map = {}
            for stat in battery_stats:
                station_id = stat.current_station_id
                voltage_type = stat.voltage_type or '60V'

                if station_id not in stats_map:
                    stats_map[station_id] = {
                        'total': 0,
                        'available': 0,
                        '60V_total': 0,
                        '60V_available': 0,
                        '72V_total': 0,
                        '72V_available': 0
                    }

                stats_map[station_id]['total'] += stat.total or 0
                stats_map[station_id]['available'] += int(stat.available or 0)

                if voltage_type == '60V':
                    stats_map[station_id]['60V_total'] = stat.total or 0
                    stats_map[station_id]['60V_available'] = int(stat.available or 0)
                elif voltage_type == '72V':
                    stats_map[station_id]['72V_total'] = stat.total or 0
                    stats_map[station_id]['72V_available'] = int(stat.available or 0)

            # 构建结果
            result = []
            for station in stations:
                distance = StationService._calculate_distance(
                    latitude, longitude,
                    float(station.latitude), float(station.longitude)
                )
                station_data = station.to_dict()
                station_data['distance'] = round(distance, 2)
                station_data['distance_meters'] = int(round(distance * 1000))
                station_data['distance_text'] = StationService._format_distance(distance)

                # 电池统计
                stat = stats_map.get(station.id, {
                    'total': 0, 'available': 0,
                    '60V_total': 0, '60V_available': 0,
                    '72V_total': 0, '72V_available': 0
                })
                available_count = stat['available']
                station_data['available_batteries'] = available_count
                station_data['total_batteries'] = stat['total']
                station_data['battery_60V'] = {
                    'total': stat['60V_total'],
                    'available': stat['60V_available']
                }
                station_data['battery_72V'] = {
                    'total': stat['72V_total'],
                    'available': stat['72V_available']
                }

                # 健康状态
                if station.status != 'active':
                    station_data['health_status'] = 'maintenance'
                    station_data['health_label'] = '维护中'
                elif available_count == 0:
                    station_data['health_status'] = 'empty'
                    station_data['health_label'] = '暂无电池'
                elif available_count <= 2:
                    station_data['health_status'] = 'low'
                    station_data['health_label'] = '电池紧张'
                else:
                    station_data['health_status'] = 'good'
                    station_data['health_label'] = '电池充足'

                # 后端推荐评分
                dist_score = max(0, 1 - distance / radius_km)
                avail_score = min(available_count / 5, 1) if available_count > 0 else 0
                status_score = 1 if station.status == 'active' else 0.25
                station_data['recommend_score'] = round(
                    dist_score * 0.45 + avail_score * 0.45 + status_score * 0.1,
                    3
                )

                result.append(station_data)

            # 按推荐评分排序（降序）
            result.sort(key=lambda x: x.get('recommend_score', 0), reverse=True)

            return result

        except Exception as e:
            print(f"获取附近站点失败: {str(e)}")
            return []

    @staticmethod
    def get_station_detail(station_id):
        """
        获取站点详情（包括可用电池数）
        
        Args:
            station_id: 站点ID
        
        Returns:
            站点详情
        """
        try:
            station = Station.query.filter_by(
                id=station_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).first()

            if not station:
                return None

            # 获取可用电池数（按电压类型分类）
            battery_stats = db.session.query(
                Battery.voltage_type,
                func.count(Battery.id).label('total'),
                func.sum(case((Battery.status == 'available', 1), else_=0)).label('available')
            ).filter(
                Battery.current_station_id == station_id,
                Battery.tenant_id == g.tenant_id,
                Battery.is_deleted == False
            ).group_by(Battery.voltage_type).all()

            # 统计电池数据
            total_batteries = 0
            available_batteries = 0
            battery_60V = {'total': 0, 'available': 0}
            battery_72V = {'total': 0, 'available': 0}

            for stat in battery_stats:
                voltage_type = stat.voltage_type or '60V'
                total = stat.total or 0
                available = int(stat.available or 0)

                total_batteries += total
                available_batteries += available

                if voltage_type == '60V':
                    battery_60V = {'total': total, 'available': available}
                elif voltage_type == '72V':
                    battery_72V = {'total': total, 'available': available}

            # 获取柜子数
            cabinets = Cabinet.query.filter_by(
                station_id=station_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).count()

            station_data = station.to_dict()
            station_data['available_batteries'] = available_batteries
            station_data['total_batteries'] = total_batteries
            station_data['battery_60V'] = battery_60V
            station_data['battery_72V'] = battery_72V
            station_data['total_cabinets'] = cabinets

            return station_data

        except Exception as e:
            print(f"获取站点详情失败: {str(e)}")
            return None

    @staticmethod
    def get_station_statistics():
        """
        获取站点统计信息
        
        Returns:
            统计数据
        """
        try:
            total_stations = Station.query.filter_by(
                tenant_id=g.tenant_id,
                is_deleted=False
            ).count()

            total_batteries = Battery.query.filter_by(
                tenant_id=g.tenant_id,
                is_deleted=False
            ).count()

            available_batteries = Battery.query.filter_by(
                status='available',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).count()

            rented_batteries = Battery.query.filter_by(
                status='rented',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).count()

            return {
                'total_stations': total_stations,
                'total_batteries': total_batteries,
                'available_batteries': available_batteries,
                'rented_batteries': rented_batteries,
                'utilization_rate': round(rented_batteries / total_batteries * 100, 2) if total_batteries > 0 else 0
            }

        except Exception as e:
            return {
                'total_stations': 0,
                'total_batteries': 0,
                'available_batteries': 0,
                'rented_batteries': 0,
                'utilization_rate': 0,
                'error': str(e)
            }

    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        """
        计算两点之间的距离（Haversine公式）
        
        Args:
            lat1, lon1: 点1的纬度和经度
            lat2, lon2: 点2的纬度和经度
        
        Returns:
            距离（公里）
        """
        R = 6371  # 地球半径（公里）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

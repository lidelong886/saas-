"""
骑手服务
"""
from datetime import datetime, timedelta
from flask import g
from sqlalchemy import and_, or_
from ..models import Station, Battery, RiderReservation, UserPackage, Package, UserBehaviorLog
from .. import db


class RiderService:
    """骑手服务类"""

    @staticmethod
    def get_nearby_stations_with_availability(latitude, longitude, radius_km=5, limit=20):
        """
        获取附近站点及可用电池数

        Args:
            latitude: 纬度
            longitude: 经度
            radius_km: 搜索半径（公里）
            limit: 返回数量限制

        Returns:
            (success, result/error_message)
        """
        try:
            # 使用Station模型的find_nearby_stations方法
            nearby_stations = Station.find_nearby_stations(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                limit=limit
            )

            # 为每个站点添加可用电池详情
            for station in nearby_stations:
                station_id = station['id']

                # 查询该站点的可用电池
                available_batteries = Battery.query.filter_by(
                    current_station_id=station_id,
                    status='available',
                    tenant_id=g.tenant_id,
                    is_deleted=False
                ).filter(
                    Battery.power_level >= 20
                ).count()

                station['available_batteries'] = available_batteries
                station['has_available'] = available_batteries > 0

            return True, nearby_stations

        except Exception as e:
            return False, f"获取附近站点失败: {str(e)}"

    @staticmethod
    def create_reservation(user_id, station_id, duration_minutes=30):
        """
        创建电池预约

        Args:
            user_id: 用户ID
            station_id: 站点ID
            duration_minutes: 预约时长（分钟）

        Returns:
            (success, result/error_message)
        """
        try:
            # 检查用户是否有未完成的预约
            existing_reservation = RiderReservation.query.filter(
                RiderReservation.user_id == user_id,
                RiderReservation.status.in_(['pending', 'confirmed']),
                RiderReservation.tenant_id == g.tenant_id,
                RiderReservation.is_deleted == False
            ).first()

            if existing_reservation:
                return False, "您已有进行中的预约，请先完成或取消"

            # 检查站点是否存在且有可用电池
            station = Station.query.filter_by(
                id=station_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).first()

            if not station:
                return False, "站点不存在"

            if station.status != 'active':
                return False, "站点当前不可用"

            # 检查可用电池数量（加锁防止并发）
            available_battery = Battery.query.filter_by(
                current_station_id=station_id,
                status='available',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).filter(
                Battery.power_level >= 20
            ).with_for_update().first()

            if not available_battery:
                return False, "该站点暂无可用电池"

            # 创建预约
            now = datetime.now()
            expires_at = now + timedelta(minutes=duration_minutes)

            reservation = RiderReservation(
                user_id=user_id,
                station_id=station_id,
                battery_id=available_battery.id,
                reserved_at=now,
                expires_at=expires_at,
                status='confirmed',
                tenant_id=g.tenant_id
            )

            db.session.add(reservation)
            db.session.commit()

            # 记录用户行为（异步，不阻塞）
            try:
                UserBehaviorLog.log_action(
                    user_id=user_id,
                    action_type='reserve',
                    station_id=station_id,
                    metadata={
                        'reservation_id': reservation.id,
                        'battery_id': available_battery.id,
                        'duration_minutes': duration_minutes
                    }
                )
            except:
                pass

            return True, {
                'reservation_id': reservation.id,
                'station_id': station_id,
                'station_name': station.name,
                'station_address': station.address,
                'battery_id': available_battery.id,
                'battery_code': available_battery.battery_code,
                'battery_power_level': available_battery.power_level,
                'reserved_at': reservation.reserved_at.strftime('%Y-%m-%d %H:%M:%S'),
                'expires_at': reservation.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': reservation.status
            }

        except Exception as e:
            db.session.rollback()
            return False, f"创建预约失败: {str(e)}"

    @staticmethod
    def cancel_reservation(reservation_id, user_id):
        """
        取消预约

        Args:
            reservation_id: 预约ID
            user_id: 用户ID

        Returns:
            (success, result/error_message)
        """
        try:
            reservation = RiderReservation.query.filter_by(
                id=reservation_id,
                user_id=user_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).first()

            if not reservation:
                return False, "预约不存在"

            if not reservation.can_cancel():
                return False, f"预约状态为{reservation.status}，无法取消"

            reservation.status = 'cancelled'
            db.session.commit()

            # 记录用户行为
            try:
                UserBehaviorLog.log_action(
                    user_id=user_id,
                    action_type='cancel_reserve',
                    station_id=reservation.station_id,
                    metadata={'reservation_id': reservation_id}
                )
            except:
                pass

            return True, {'reservation_id': reservation_id, 'status': 'cancelled'}

        except Exception as e:
            db.session.rollback()
            return False, f"取消预约失败: {str(e)}"

    @staticmethod
    def get_user_reservations(user_id, page=1, per_page=20, status=None):
        """
        获取用户的预约列表

        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            status: 状态筛选

        Returns:
            分页结果
        """
        try:
            query = RiderReservation.query.filter_by(
                user_id=user_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            )

            if status:
                query = query.filter_by(status=status)

            pagination = query.order_by(
                RiderReservation.created_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)

            return {
                'items': [reservation.to_dict() for reservation in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }

        except Exception as e:
            return {
                'items': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0,
                'error': str(e)
            }

    @staticmethod
    def check_reservation_timeout():
        """
        检查并处理超时的预约（定时任务调用）

        Returns:
            处理的预约数量
        """
        try:
            now = datetime.now()

            # 查找所有超时的预约
            timeout_reservations = RiderReservation.query.filter(
                RiderReservation.status.in_(['pending', 'confirmed']),
                RiderReservation.expires_at < now,
                RiderReservation.is_deleted == False
            ).all()

            count = 0
            for reservation in timeout_reservations:
                reservation.status = 'timeout'
                count += 1

            if count > 0:
                db.session.commit()

            return count

        except Exception as e:
            db.session.rollback()
            print(f"检查预约超时失败: {str(e)}")
            return 0

    @staticmethod
    def get_rider_packages(user_id=None):
        """
        获取骑手专属套餐列表

        Args:
            user_id: 用户ID（可选，用于检查用户已购买的套餐）

        Returns:
            (success, result/error_message)
        """
        try:
            # 查询骑手专属套餐
            packages = Package.query.filter_by(
                rider_exclusive=True,
                is_active=True,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).order_by(Package.validity_days.asc()).all()

            result = []
            for package in packages:
                package_dict = package.to_dict()

                # 如果提供了用户ID，检查用户是否已购买
                if user_id:
                    user_package = UserPackage.query.filter_by(
                        user_id=user_id,
                        package_id=package.id,
                        status='active',
                        tenant_id=g.tenant_id,
                        is_deleted=False
                    ).first()

                    package_dict['is_purchased'] = user_package is not None
                    if user_package:
                        package_dict['expires_at'] = user_package.expires_at.strftime('%Y-%m-%d %H:%M:%S') if user_package.expires_at else None
                else:
                    package_dict['is_purchased'] = False

                result.append(package_dict)

            return True, result

        except Exception as e:
            return False, f"获取骑手套餐失败: {str(e)}"

    @staticmethod
    def check_user_has_active_rider_package(user_id):
        """
        检查用户是否有有效的骑手套餐

        Args:
            user_id: 用户ID

        Returns:
            (has_package, package_info)
        """
        try:
            now = datetime.now()

            # 查找用户的有效骑手套餐
            user_package = UserPackage.query.join(
                Package, UserPackage.package_id == Package.id
            ).filter(
                UserPackage.user_id == user_id,
                UserPackage.status == 'active',
                Package.rider_exclusive == True,
                UserPackage.tenant_id == g.tenant_id,
                UserPackage.is_deleted == False
            ).filter(
                or_(
                    UserPackage.expires_at == None,
                    UserPackage.expires_at > now
                )
            ).first()

            if user_package:
                return True, {
                    'package_id': user_package.package_id,
                    'package_name': user_package.package_name,
                    'expires_at': user_package.expires_at.strftime('%Y-%m-%d %H:%M:%S') if user_package.expires_at else None
                }

            return False, None

        except Exception as e:
            print(f"检查骑手套餐失败: {str(e)}")
            return False, None

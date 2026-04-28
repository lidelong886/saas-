"""
电池服务
"""
from datetime import datetime, timedelta
from flask import g, current_app
from ..models import Battery, Station, Cabinet, Order
from ..models import UserPackage, Package
from .. import db


class BatteryService:
    """电池服务类"""

    @staticmethod
    def rent_battery(user_id, battery_id, hours=24, station_id=None, cabinet_id=None):
        """创建租赁订单

        有套餐: 0元自动完成租赁
        无套餐: 正常创建待支付订单
        """
        try:
            battery = Battery.query.filter_by(
                id=battery_id, tenant_id=g.tenant_id, is_deleted=False
            ).first()
            if not battery:
                return False, "电池不存在"
            if not battery.is_available():
                return False, "电池不可用"

            # 检查是否已有租用中的电池
            active_batteries = Battery.query.filter_by(
                current_user_id=user_id,
                status='rented',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).count()
            if active_batteries >= 1:
                return False, "每个人在租用中的电池只能有一块，请先归还当前持有的电池。"

            # 检查是否有未完成的租电订单
            pending_rental_order = Order.query.filter(
                Order.user_id == user_id,
                Order.tenant_id == g.tenant_id,
                Order.order_type == 'rental',
                Order.status.in_(['pending', 'paid']),
                Order.is_deleted == False
            ).order_by(Order.id.desc()).first()
            if pending_rental_order:
                return False, "您有未完成的租电订单，请先完成支付、使用或取消后再租电"

            # 检查用户是否有有效的套餐
            active_package = UserPackage.query.filter(
                UserPackage.user_id == user_id,
                UserPackage.tenant_id == g.tenant_id,
                UserPackage.status.in_(['active', 'unused']),
                UserPackage.is_deleted == False
            ).first()

            # 如果套餐状态是未使用，激活它
            if active_package and active_package.status == 'unused':
                active_package.status = 'active'
                active_package.activated_at = datetime.now()
                pkg = Package.query.get(active_package.package_id)
                if pkg and pkg.package_type == 'time':
                    active_package.expires_at = datetime.now() + timedelta(days=30)
                elif pkg and pkg.package_type == 'count':
                    active_package.expires_at = datetime.now() + timedelta(days=365)
                db.session.commit()

            order_station_id = station_id if station_id is not None else getattr(battery, 'current_station_id', None)
            order_cabinet_id = cabinet_id if cabinet_id is not None else getattr(battery, 'current_cabinet_id', None)

            if active_package:
                # ===== 有套餐：0元租电，自动完成 =====
                order = Order(
                    order_type='rental',
                    user_id=user_id,
                    battery_id=battery_id,
                    package_id=active_package.package_id,
                    station_id=order_station_id,
                    cabinet_id=order_cabinet_id,
                    rental_hours=hours,
                    rental_fee=0,
                    deposit_fee=0,
                    total_amount=0,
                    source='miniapp',
                    timeout_cancel_at=datetime.now() + timedelta(minutes=15)
                )
                db.session.add(order)
                db.session.commit()

                # 直接完成支付流程：占用电池
                success, message = battery.rent_to_user(user_id, hours)
                if not success:
                    db.session.rollback()
                    return False, message

                ok, msg = order.transition_status('rented')
                if not ok:
                    db.session.rollback()
                    return False, msg

                order.payment_method = 'package_free'
                order.payment_time = datetime.now()
                order.transaction_id = f"PKG{datetime.now().strftime('%Y%m%d%H%M%S')}"
                db.session.commit()

                return True, {
                    'order_no': order.order_no,
                    'order_type': order.order_type,
                    'total_amount': 0,
                    'order_id': order.id,
                    'status': order.status,
                    'package_id': active_package.package_id
                }
            else:
                # ===== 无套餐：正常创建待支付订单 =====
                rental_fee = float(battery.rental_price_per_hour) * hours
                deposit_fee = float(battery.deposit_amount)

                order = Order(
                    order_type='rental',
                    user_id=user_id,
                    battery_id=battery_id,
                    station_id=order_station_id,
                    cabinet_id=order_cabinet_id,
                    rental_hours=hours,
                    unit_price=battery.rental_price_per_hour,
                    rental_fee=rental_fee,
                    deposit_fee=deposit_fee,
                    total_amount=rental_fee + deposit_fee,
                    source='miniapp',
                    timeout_cancel_at=datetime.now() + timedelta(minutes=15),
                    pricing_snapshot={
                        'battery_id': battery_id,
                        'hours': hours,
                        'rental_fee': rental_fee,
                        'deposit_fee': deposit_fee
                    }
                )
                db.session.add(order)
                db.session.commit()

                return True, {
                    'order_no': order.order_no,
                    'order_type': 'rental',
                    'total_amount': float(order.total_amount),
                    'order_id': order.id
                }

        except Exception as e:
            db.session.rollback()
            return False, f"租用电池失败: {str(e)}"

    @staticmethod
    def return_battery(battery_id, station_id=None, cabinet_id=None, latitude=None, longitude=None):
        """归还电池"""
        try:
            battery = Battery.query.filter_by(id=battery_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not battery:
                return False, "电池不存在"

            order = Order.query.filter_by(
                battery_id=battery_id,
                user_id=battery.current_user_id,
                status='rented',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).first()
            if not order:
                return False, "未找到对应的租用订单"

            success, message = battery.return_battery(station_id, cabinet_id)
            if not success:
                return False, message

            ok, msg = order.transition_status('completed')
            if not ok:
                db.session.rollback()
                return False, f"归还电池失败：{msg}"
            order.actual_return_time = datetime.now()
            order.return_latitude = latitude
            order.return_longitude = longitude
            db.session.commit()

            # 订单完成通知
            try:
                from ..services.notification_service import NotificationService
                NotificationService.on_order_completed(order.user_id, order.order_no)
            except Exception:
                pass

            return True, order.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"归还电池失败: {str(e)}"

    @staticmethod
    def get_battery_statistics():
        """获取电池统计信息"""
        try:
            total = Battery.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).count()
            available = Battery.query.filter_by(tenant_id=g.tenant_id, status='available', is_deleted=False).count()
            in_use = Battery.query.filter_by(tenant_id=g.tenant_id, status='rented', is_deleted=False).count()
            charging = Battery.query.filter_by(tenant_id=g.tenant_id, status='charging', is_deleted=False).count()

            return {
                'total_batteries': total,
                'available_batteries': available,
                'in_use_batteries': in_use,
                'charging_batteries': charging,
                'occupancy_rate': (in_use / total * 100) if total > 0 else 0
            }, "获取电池统计信息成功"
        except Exception as e:
            return None, f"获取电池统计信息失败: {str(e)}"

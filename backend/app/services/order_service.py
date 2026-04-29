"""
订单服务
"""
from datetime import datetime, timedelta
from flask import g, current_app
from ..models import Order, Battery, User, Package, UserPackage
from ..models.payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from .. import db
from .tenant_config_service import TenantConfigService

# 模块级常量，避免在静态方法中引用类名自身
PENDING_TIMEOUT_MINUTES = 15

class OrderService:
    """订单服务类"""

    PENDING_TIMEOUT_MINUTES = PENDING_TIMEOUT_MINUTES

    @staticmethod
    def create_order(user_id, order_type, battery_id=None, hours=24, package_id=None, station_id=None, cabinet_id=None, source='miniapp'):
        """创建订单"""
        try:
            user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not user:
                return False, "用户不存在"

            pkg = None
            if package_id:
                pkg = Package.query.filter_by(id=package_id, tenant_id=g.tenant_id, is_deleted=False).first()

            order = Order(
                order_type=order_type,
                user_id=user_id,
                package_id=package_id,
                station_id=station_id,
                cabinet_id=cabinet_id,
                source=source,
                timeout_cancel_at=datetime.now() + timedelta(
                    minutes=TenantConfigService.get_value(g.tenant_id, 'order_timeout_minutes')
                )
            )

            if order_type == 'rental':
                # 检查用户是否已经有租用的电池
                # 检查用户当前名下持有的真实电池数（不限于订单状态，而是真实状态）
                from ..models import Battery
                active_batteries = Battery.query.filter_by(
                    current_user_id=user_id,
                    status='rented', owner_id=None,
                    tenant_id=g.tenant_id,
                    is_deleted=False
                ).count()
                
                if active_batteries >= 1:
                    return False, "每个人在租用中的电池只能有一块，请先归还当前持有的电池。" 

                if not battery_id:
                    return False, "租用订单必须指定电池"
                battery = Battery.query.filter_by(id=battery_id, tenant_id=g.tenant_id, is_deleted=False).first()
                if not battery:
                    return False, "电池不存在"
                if not battery.is_available():
                    return False, "电池不可用"

                order.battery_id = battery_id
                use_hours = pkg.hours if pkg and pkg.hours else hours
                order.rental_hours = use_hours
                order.unit_price = pkg.price if pkg else battery.rental_price_per_hour
                
                # 如果用户是使用已有套餐租电(传入了package_id)，因为他们已经购买了套餐，所以本次租金应为0
                if package_id:
                    rental_fee = 0.0
                    deposit_fee = 0.0 # 押金通常在买套餐时付过了
                    # Note: order is saved as 'pending' by default in __init__, but we will auto-pay it later
                else:
                    unit_price = float(battery.rental_price_per_hour or TenantConfigService.get_value(g.tenant_id, 'rental_price_per_hour'))
                    rental_fee = unit_price * use_hours
                    deposit_fee = float(battery.deposit_amount or TenantConfigService.get_value(g.tenant_id, 'deposit_amount'))
                    order.unit_price = unit_price
                
                order.rental_fee = rental_fee
                order.deposit_fee = deposit_fee
                order.total_amount = rental_fee + deposit_fee
                order.pricing_snapshot = {
                    'battery_id': battery_id,
                    'hours': use_hours,
                    'package_id': package_id,
                    'rental_fee': rental_fee,
                    'deposit_fee': deposit_fee
                }
            elif order_type == 'exchange':
                if package_id and not pkg:
                    return False, '套餐不存在'
                exchange_fee = float(pkg.exchange_fee) if pkg else TenantConfigService.get_value(g.tenant_id, 'exchange_fee')
                order.exchange_fee = exchange_fee
                order.total_amount = exchange_fee
                order.pricing_snapshot = {
                    'package_id': package_id,
                    'exchange_fee': exchange_fee
                }
            elif order_type == 'purchase':
                # Can be a battery purchase or a package purchase
                if not battery_id and not package_id:
                    return False, '购买订单必须指定电池或套餐'
                
                amount = 0
                if battery_id:
                    battery = Battery.query.filter_by(id=battery_id, tenant_id=g.tenant_id, is_deleted=False).first()
                    if not battery:
                        return False, '电池不存在'
                    amount = float(battery.deposit_amount or 0)
                    order.battery_id = battery_id
                    order.pricing_snapshot = {
                        'battery_id': battery_id,
                        'purchase_amount': amount
                    }
                elif package_id:
                    if not pkg:
                        return False, '套餐不存在'
                    amount = float(pkg.price)
                    order.pricing_snapshot = {
                        'package_id': package_id,
                        'purchase_amount': amount
                    }
                
                order.total_amount = amount
            else:
                return False, "不支持的订单类型"

            db.session.add(order)
            db.session.commit()
            return True, {'order_no': order.order_no, 'order_type': order_type, 'total_amount': float(order.total_amount), 'order_id': order.id}
        except Exception as e:
            db.session.rollback()
            return False, f"创建订单失败: {str(e)}"

    @staticmethod
    def pay_order(order_id, payment_method='wechat'):
        """支付订单"""
        try:
            order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not order:
                return False, "订单不存在"
            if not order.can_transition_to('paid') and not order.can_transition_to('rented'):
                return False, "订单状态不允许支付"

            # 模拟支付成功：租赁订单支付后进入租用中并占用电池
            if order.order_type == 'rental':
                battery = Battery.query.filter_by(id=order.battery_id, tenant_id=g.tenant_id, is_deleted=False).first()
                if not battery:
                    return False, "电池不存在"
                if not battery.is_available():
                    return False, "电池不可用"
                success, message = battery.rent_to_user(order.user_id, order.rental_hours or 24)
                if not success:
                    return False, message
                success, message = order.transition_status('rented')
                if not success:
                    return False, message
            else:
                success, message = order.transition_status('paid')
                if not success:
                    return False, message
                # 如果是换电订单金额为0，自动完成
                if order.order_type == 'exchange' and float(order.total_amount or 0) == 0:
                    ok2, _ = order.transition_status('completed')
                    if not ok2:
                        return False, "零元换电订单状态变更失败"
                
                # 如果是套餐购买，也直接标记为已完成
                if order.order_type == 'purchase' and order.package_id and not order.battery_id:
                    ok3, _ = order.transition_status('completed')
                    if not ok3:
                        return False, "套餐购买订单状态变更失败"
                    
                    # 生成一张卡券 (unused 状态)
                    pkg = Package.query.get(order.package_id)
                    user_pkg = UserPackage(
                        user_id=order.user_id,
                        package_id=order.package_id,
                        order_id=order.id,
                        status='unused',
                        package_name=pkg.name,
                        package_type=pkg.package_type,
                        total_hours=pkg.hours,
                        tenant_id=g.tenant_id
                    )
                    db.session.add(user_pkg)
                
                # 如果是购买电池，将电池所有权转移给用户，状态变为 owned (私有)，然后完成订单
                if order.order_type == 'purchase' and order.battery_id:
                    battery = Battery.query.get(order.battery_id)
                    if battery:
                        battery.owner_id = order.user_id
                        battery.current_user_id = order.user_id
                        battery.status = 'owned'  # 新增私有状态
                        db.session.add(battery)
                    
                    ok3, _ = order.transition_status('completed')
                    if not ok3:
                        return False, "电池购买订单状态变更失败"

            order.payment_method = payment_method
            order.payment_time = datetime.now()
            order.transaction_id = f"TX{datetime.now().strftime('%Y%m%d%H%M%S')}"
            db.session.commit()

            # 订单完成时创建通知
            if order.status == 'completed':
                try:
                    from ..services.notification_service import NotificationService
                    NotificationService.on_order_completed(order.user_id, order.order_no)
                except Exception:
                    pass

            return True, {'order_no': order.order_no, 'amount': float(order.total_amount), 'payment_method': payment_method}
        except Exception as e:
            db.session.rollback()
            return False, f"支付失败: {str(e)}"

    @staticmethod
    def cancel_expired_pending_orders(timeout_minutes=None):
        """
        取消超时未支付订单
        """
        timeout_minutes = timeout_minutes or PENDING_TIMEOUT_MINUTES
        expire_before = datetime.now() - timedelta(minutes=timeout_minutes)

        expired_orders = Order.query.filter(
            Order.status == 'pending',
            Order.is_deleted == False,
            Order.timeout_cancel_at <= datetime.now()
        ).all()

        cancelled_count = 0
        for order in expired_orders:
            success, _ = order.transition_status('cancelled', reason='订单超时自动取消')
            if success:
                cancelled_count += 1

        if cancelled_count > 0:
            db.session.commit()

        return cancelled_count

    @staticmethod
    def request_refund(user_id, order_no):
        """申请退款逻辑"""
        try:
            order = Order.query.filter_by(
                order_no=order_no,
                user_id=user_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).first()

            if not order:
                return False, "订单不存在"

            # 允许退款的状态：已支付、已归还、已完成
            if order.status not in ['paid', 'returned', 'completed']:
                return False, f"当前订单状态({order.status})不支持退款"

            # 走状态机更新状态
            ok, msg = order.transition_status('refunded')
            if not ok:
                return False, msg
            db.session.commit()

            return True, "退款申请已处理"
        except Exception as e:
            db.session.rollback()
            return False, f"退款处理异常: {str(e)}"

    @staticmethod
    def get_order_statistics():
        """获取订单统计信息"""
        try:
            today = datetime.now().date()
            total = Order.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).count()
            today_orders = Order.query.filter(Order.tenant_id == g.tenant_id, Order.created_at >= today, Order.is_deleted == False).count()
            completed = Order.query.filter_by(tenant_id=g.tenant_id, status='completed', is_deleted=False).count()
            return {'total_orders': total, 'today_orders': today_orders, 'completed_orders': completed}
        except:
            return {'total_orders': 0, 'today_orders': 0, 'completed_orders': 0}

"""
支付服务（毕设演示模式：余额即时扣款；第三方支付保留预支付与回调扩展点）
"""
from datetime import datetime
import json
import uuid
from flask import g

from ..models import Order, User, Battery
from ..models.payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from .. import db
from .order_service import OrderService
from .wallet_service import WalletService
from ..utils.wechat_pay import WeChatPayService


class PaymentService:
    """支付服务类"""

    @staticmethod
    def _payment_method_enum(name):
        name = (name or 'wechat').lower()
        mapping = {
            'wechat': PaymentMethod.WECHAT,
            'alipay': PaymentMethod.ALIPAY,
            'balance': PaymentMethod.BALANCE,
        }
        return mapping.get(name, PaymentMethod.WECHAT)

    @staticmethod
    def create_payment(user_id, order_id, amount, payment_method='wechat'):
        """创建支付记录（底层）"""
        try:
            pm = PaymentService._payment_method_enum(payment_method)
            payment = Payment(
                payment_type=PaymentType.ORDER_PAYMENT,
                payment_method=pm,
                status=PaymentStatus.PENDING,
                user_id=user_id,
                order_id=order_id,
                amount=amount,
                tenant_id=g.tenant_id
            )
            db.session.add(payment)
            db.session.commit()
            return True, payment
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def create_payment_order(order_id, payment_method='wechat'):
        """
        创建支付订单：余额则直接扣款并完成订单；微信/支付宝生成待支付记录并返回演示预支付参数。
        """
        try:
            order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not order:
                return False, "订单不存在"
            if order.status != 'pending':
                return False, "订单状态不允许支付"

            pm = (payment_method or 'wechat').lower()

            if pm == 'balance':
                user = User.query.filter_by(id=order.user_id, tenant_id=g.tenant_id, is_deleted=False).first()
                if not user:
                    return False, "用户不存在"
                need = float(order.total_amount or 0)
                if float(user.balance or 0) < need:
                    return False, "余额不足"

                ok, pay = PaymentService.create_payment(order.user_id, order.id, order.total_amount, 'balance')
                if not ok:
                    return False, pay
                payment = pay
                ok_wallet, wallet_result = WalletService.consume(
                    order.user_id,
                    need,
                    order_id=order.id,
                    payment_id=payment.id,
                    remarks=f'订单 {order.order_no} 余额支付'
                )
                if not ok_wallet:
                    db.session.rollback()
                    return False, wallet_result
                payment.status = PaymentStatus.SUCCESS
                payment.payment_time = datetime.now()
                payment.transaction_id = f"BL{datetime.now().strftime('%Y%m%d%H%M%S')}"
                db.session.commit()

                ok2, result = OrderService.pay_order(order.id, 'balance')
                if not ok2:
                    db.session.rollback()
                    return False, result
                return True, {
                    'order_no': order.order_no,
                    'payment_no': payment.payment_no,
                    'paid': True,
                    'payment_method': 'balance',
                    'data': result
                }

            pm_enum = PaymentService._payment_method_enum(pm)
            payment = Payment(
                payment_type=PaymentType.ORDER_PAYMENT,
                payment_method=pm_enum,
                status=PaymentStatus.PENDING,
                user_id=order.user_id,
                order_id=order.id,
                amount=order.total_amount,
                tenant_id=g.tenant_id
            )
            db.session.add(payment)
            db.session.commit()

            ts = str(int(datetime.now().timestamp()))
            nonce = uuid.uuid4().hex[:16]
            return True, {
                'payment_no': payment.payment_no,
                'order_no': order.order_no,
                'amount': float(order.total_amount or 0),
                'payment_method': pm,
                'mock': True,
                'wx_pay_params': {
                    'timeStamp': ts,
                    'nonceStr': nonce,
                    'package': 'prepay_id=wx_mock_prepay',
                    'signType': 'RSA',
                    'paySign': 'MOCK_SIGN_FOR_DEV'
                }
            }
        except Exception as e:
            db.session.rollback()
            return False, f"创建支付订单失败: {str(e)}"

    @staticmethod
    def pay_order(order_id, payment_method='wechat'):
        """
        毕设演示模式支付成功回调：走订单支付逻辑，真实微信支付可替换为商户回调。
        """
        return OrderService.pay_order(order_id, payment_method)

    @staticmethod
    def process_payment(payment_id):
        """处理单笔支付记录为成功（内部）"""
        try:
            payment = Payment.query.filter_by(id=payment_id, tenant_id=g.tenant_id).first()
            if not payment:
                return False, "支付记录不存在"

            payment.status = PaymentStatus.SUCCESS
            payment.payment_time = datetime.now()
            payment.transaction_id = f"TX{datetime.now().strftime('%Y%m%d%H%M%S')}"

            if payment.order_id:
                order = Order.query.filter_by(id=payment.order_id, tenant_id=g.tenant_id, is_deleted=False).first()
                if order and order.status == 'pending':
                    ok, _ = order.transition_status('paid')
                    if not ok:
                        current_app.logger.warning(f"[PaymentService] process_payment: order {order.id} transition to paid failed, current status={order.status}, skipping")
                    order.payment_time = datetime.now()
                    order.payment_method = getattr(payment.payment_method, 'value', None) or str(payment.payment_method)

            db.session.commit()
            return True, "支付成功"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def handle_payment_notify(headers, body):
        """
        微信支付回调处理。
        """
        try:
            verify_result = WeChatPayService.verify_notification_signature(headers, body)
            if not verify_result.get('success'):
                return False, verify_result.get('message', '签名验证失败')
            return True, json.dumps({"code": "SUCCESS", "message": "成功"})
        except Exception as e:
            return False, str(e)

    @staticmethod
    def create_recharge_order(user_id, amount, payment_method='wechat'):
        try:
            user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not user:
                return False, '用户不存在'

            amt = float(amount or 0)
            if amt <= 0:
                return False, '充值金额必须大于0'

            payment = Payment.create_recharge(user_id, amt, PaymentService._payment_method_enum(payment_method))
            payment.tenant_id = g.tenant_id
            payment.status = PaymentStatus.PENDING
            payment.save()

            if payment_method == 'balance':
                return False, '充值不支持余额支付'

            return True, {
                'payment_no': payment.payment_no,
                'amount': amt,
                'payment_method': payment_method,
                'mock': True,
                'wx_pay_params': {
                    'timeStamp': str(int(datetime.now().timestamp())),
                    'nonceStr': uuid.uuid4().hex[:16],
                    'package': 'prepay_id=wx_recharge_mock',
                    'signType': 'RSA',
                    'paySign': 'MOCK_SIGN_FOR_RECHARGE'
                }
            }
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def complete_recharge(payment_no):
        try:
            payment = Payment.query.filter_by(payment_no=payment_no, tenant_id=g.tenant_id, is_deleted=False).first()
            if not payment:
                return False, '充值记录不存在'
            if payment.payment_type != PaymentType.RECHARGE:
                return False, '支付类型不正确'
            if payment.status == PaymentStatus.SUCCESS:
                return True, payment.to_dict()

            payment.status = PaymentStatus.SUCCESS
            payment.payment_time = datetime.now()
            payment.transaction_id = f"RC{datetime.now().strftime('%Y%m%d%H%M%S')}"
            ok, tx = WalletService.recharge(
                payment.user_id,
                payment.amount,
                payment_id=payment.id,
                remarks=f'充值单 {payment.payment_no}'
            )
            if not ok:
                db.session.rollback()
                return False, tx
            payment.save()
            return True, {
                'payment': payment.to_dict(),
                'wallet_transaction_id': tx.id
            }
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def refund_order(order_id, refund_amount, reason):
        """申请退款：走状态机 + 退还电池（若租用中）"""
        try:
            order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not order:
                return False, "订单不存在"
            amt = float(refund_amount)
            if amt <= 0:
                return False, "退款金额无效"
            if amt > float(order.total_amount or 0):
                return False, "退款金额超过订单金额"

            # 1. 归还电池（如有租用中电池）
            if order.battery_id and order.status in ('rented', 'paid', 'returned'):
                battery = Battery.query.filter_by(id=order.battery_id, tenant_id=g.tenant_id, is_deleted=False).first()
                if battery:
                    battery.status = 'available'
                    battery.current_user_id = None
                    battery.save()

            # 2. 记录退款字段
            order.refund_amount = amt
            order.refund_reason = (reason or '')[:200]
            order.refund_time = datetime.now()
            order.refund_status = 'completed'

            # 3. 余额退款（如用余额支付）
            latest_payment = Payment.query.filter_by(order_id=order.id, tenant_id=g.tenant_id, is_deleted=False).order_by(Payment.id.desc()).first()
            if latest_payment:
                latest_payment.refund_status = 'completed'
                latest_payment.refund_amount = amt
                latest_payment.refund_time = datetime.now()
                if latest_payment.payment_method == PaymentMethod.BALANCE:
                    ok, tx = WalletService.refund(
                        order.user_id,
                        amt,
                        order_id=order.id,
                        payment_id=latest_payment.id,
                        remarks=f'订单 {order.order_no} 退款'
                    )
                    if not ok:
                        db.session.rollback()
                        return False, tx

            # 4. 走状态机，不接受直接覆盖
            ok, _ = order.transition_status('refunded')
            if not ok:
                db.session.rollback()
                return False, f"订单状态不允许退款（当前状态：{order.status}）"

            db.session.commit()
            return True, {'order_no': order.order_no, 'status': order.status}
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def query_payment_status(order_id):
        """查询订单关联的最新支付状态"""
        try:
            order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not order:
                return False, "订单不存在"
            pay = Payment.query.filter_by(order_id=order_id, tenant_id=g.tenant_id).order_by(Payment.id.desc()).first()
            return True, {
                'order_no': order.order_no,
                'order_status': order.status,
                'payment_status': getattr(pay.status, 'value', None) if pay else None,
                'payment_no': pay.payment_no if pay else None
            }
        except Exception as e:
            return False, str(e)

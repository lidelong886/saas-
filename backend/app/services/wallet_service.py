"""
钱包服务
"""
from decimal import Decimal
from flask import g

from .. import db
from ..models import User, WalletTransaction, Payment


class WalletService:
    """钱包服务"""

    @staticmethod
    def _to_decimal(amount):
        return Decimal(str(amount or 0))

    @staticmethod
    def create_transaction(user, amount, transaction_type, direction, order_id=None, payment_id=None, remarks=None):
        amount_dec = WalletService._to_decimal(amount)
        before = WalletService._to_decimal(user.balance)
        if direction == 'income':
            after = before + amount_dec
        else:
            after = before - amount_dec

        tx = WalletTransaction(
            user_id=user.id,
            order_id=order_id,
            payment_id=payment_id,
            transaction_type=transaction_type,
            direction=direction,
            amount=amount_dec,
            balance_before=before,
            balance_after=after,
            remarks=remarks,
            tenant_id=g.tenant_id
        )
        db.session.add(tx)
        return tx

    @staticmethod
    def recharge(user_id, amount, payment_id=None, remarks='钱包充值'):
        user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not user:
            return False, '用户不存在'

        amount_dec = WalletService._to_decimal(amount)
        if amount_dec <= 0:
            return False, '充值金额必须大于0'

        tx = WalletService.create_transaction(
            user,
            amount_dec,
            'recharge',
            'income',
            payment_id=payment_id,
            remarks=remarks
        )
        user.balance = tx.balance_after
        db.session.commit()
        return True, tx

    @staticmethod
    def consume(user_id, amount, order_id=None, payment_id=None, remarks='余额支付'):
        user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not user:
            return False, '用户不存在'

        amount_dec = WalletService._to_decimal(amount)
        if amount_dec <= 0:
            return False, '扣款金额必须大于0'
        if WalletService._to_decimal(user.balance) < amount_dec:
            return False, '余额不足'

        tx = WalletService.create_transaction(
            user,
            amount_dec,
            'pay',
            'expense',
            order_id=order_id,
            payment_id=payment_id,
            remarks=remarks
        )
        user.balance = tx.balance_after
        db.session.commit()
        return True, tx

    @staticmethod
    def refund(user_id, amount, order_id=None, payment_id=None, remarks='订单退款'):
        return WalletService.recharge(user_id, amount, payment_id=payment_id, remarks=remarks)

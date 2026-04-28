"""
钱包流水模型
"""
from .base import BaseModel
from .. import db


class WalletTransaction(BaseModel):
    """钱包流水"""
    __tablename__ = 'wallet_transactions'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), comment='订单ID')
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), comment='支付记录ID')
    transaction_type = db.Column(db.String(20), nullable=False, comment='流水类型 recharge/pay/refund/adjustment')
    direction = db.Column(db.String(10), nullable=False, comment='方向 income/expense')
    amount = db.Column(db.Numeric(10, 2), nullable=False, comment='金额')
    balance_before = db.Column(db.Numeric(10, 2), default=0.00, comment='变更前余额')
    balance_after = db.Column(db.Numeric(10, 2), default=0.00, comment='变更后余额')
    status = db.Column(db.String(20), default='success', comment='状态')
    remarks = db.Column(db.String(255), comment='备注')

    user = db.relationship('User', backref='wallet_transactions')
    order = db.relationship('Order', backref='wallet_transactions')
    payment = db.relationship('Payment', backref='wallet_transactions')

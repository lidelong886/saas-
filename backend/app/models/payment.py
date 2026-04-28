"""
支付模型
"""
from enum import Enum
from datetime import datetime
from .base import BaseModel
from .. import db

class PaymentType(Enum):
    """支付类型枚举"""
    ORDER_PAYMENT = 'order_payment'    # 订单支付
    DEPOSIT_REFUND = 'deposit_refund'  # 押金退款
    PENALTY = 'penalty'               # 违约金
    RECHARGE = 'recharge'             # 余额充值

class PaymentMethod(Enum):
    """支付方式枚举"""
    WECHAT = 'wechat'        # 微信支付
    ALIPAY = 'alipay'        # 支付宝
    BALANCE = 'balance'      # 余额支付
    CARD = 'card'           # 银行卡

class PaymentStatus(Enum):
    """支付状态枚举"""
    PENDING = 'pending'     # 待支付
    SUCCESS = 'success'     # 支付成功
    FAILED = 'failed'       # 支付失败
    REFUNDED = 'refunded'   # 已退款
    CANCELLED = 'cancelled' # 已取消

class Payment(BaseModel):
    """
    支付记录模型
    """
    __tablename__ = 'payments'

    # 基本信息
    payment_no = db.Column(db.String(50), unique=True, nullable=False, comment='支付单号')
    payment_type = db.Column(db.Enum(PaymentType), nullable=False, comment='支付类型')
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False, comment='支付方式')
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, comment='支付状态')

    # 关联信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), comment='订单ID')

    # 金额信息
    amount = db.Column(db.Numeric(10, 2), nullable=False, comment='支付金额')
    refund_amount = db.Column(db.Numeric(10, 2), default=0.00, comment='退款金额')

    # 支付信息
    transaction_id = db.Column(db.String(100), comment='第三方交易号')
    out_trade_no = db.Column(db.String(100), comment='商户订单号')
    prepay_id = db.Column(db.String(100), comment='预支付ID')
    callback_time = db.Column(db.DateTime, comment='回调时间')
    refund_status = db.Column(db.String(20), default='none', comment='退款状态')

    # 时间信息
    payment_time = db.Column(db.DateTime, comment='支付完成时间')
    refund_time = db.Column(db.DateTime, comment='退款时间')

    # 支付参数
    payment_params = db.Column(db.JSON, comment='支付参数')
    callback_data = db.Column(db.JSON, comment='回调数据')

    # 备注
    remarks = db.Column(db.String(500), comment='备注')
    error_message = db.Column(db.String(500), comment='错误信息')

    # 关联对象
    user = db.relationship('User', backref='payments')
    order = db.relationship('Order', backref='payments')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.payment_no:
            self.payment_no = self.generate_payment_no()

    @staticmethod
    def generate_payment_no():
        """
        生成支付单号
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = __import__('random').randint(1000, 9999)
        return f"PAY{timestamp}{random_str}"

    def mark_success(self, transaction_id=None, payment_time=None):
        """
        标记支付成功
        """
        self.status = PaymentStatus.SUCCESS
        self.transaction_id = transaction_id
        self.payment_time = payment_time or datetime.now()
        self.save()

        # 更新用户余额（如果是余额支付）
        if self.payment_method == PaymentMethod.BALANCE:
            self.user.deduct_balance(float(self.amount))

        # 如果是充值，增加用户余额
        elif self.payment_type == PaymentType.RECHARGE:
            self.user.add_balance(float(self.amount))

    def mark_failed(self, error_message=None):
        """
        标记支付失败
        """
        self.status = PaymentStatus.FAILED
        self.error_message = error_message
        self.save()

    def refund(self, refund_amount=None, refund_time=None, remarks=None):
        """
        退款
        """
        if refund_amount is None:
            refund_amount = self.amount

        self.status = PaymentStatus.REFUNDED
        self.refund_amount = refund_amount
        self.refund_time = refund_time or datetime.now()
        if remarks:
            self.remarks = remarks
        self.save()

        # 退还用户余额
        if self.payment_method == PaymentMethod.BALANCE:
            self.user.add_balance(float(refund_amount))

    def cancel(self):
        """
        取消支付
        """
        self.status = PaymentStatus.CANCELLED
        self.save()

    def to_dict(self):
        """
        转换为字典
        """
        data = super().to_dict()
        data['payment_type'] = self.payment_type.value if self.payment_type else None
        data['payment_method'] = self.payment_method.value if self.payment_method else None
        data['status'] = self.status.value if self.status else None
        return data

    @classmethod
    def create_order_payment(cls, user_id, order_id, amount, payment_method=PaymentMethod.WECHAT):
        """
        创建订单支付记录
        """
        payment = cls(
            payment_type=PaymentType.ORDER_PAYMENT,
            payment_method=payment_method,
            user_id=user_id,
            order_id=order_id,
            amount=amount
        )
        payment.save()
        return payment

    @classmethod
    def create_deposit_refund(cls, user_id, order_id, amount):
        """
        创建押金退款记录
        """
        payment = cls(
            payment_type=PaymentType.DEPOSIT_REFUND,
            payment_method=PaymentMethod.BALANCE,
            user_id=user_id,
            order_id=order_id,
            amount=amount
        )
        payment.save()
        return payment

    @classmethod
    def create_recharge(cls, user_id, amount, payment_method=PaymentMethod.WECHAT):
        """
        创建充值记录
        """
        payment = cls(
            payment_type=PaymentType.RECHARGE,
            payment_method=payment_method,
            user_id=user_id,
            amount=amount
        )
        payment.save()
        return payment

    @classmethod
    def get_user_payments(cls, user_id, page=1, per_page=20, payment_type=None):
        """
        获取用户支付记录
        """
        tenant_id = getattr(__import__('flask').g, 'tenant_id', 1)
        query = cls.query.filter_by(
            user_id=user_id,
            tenant_id=tenant_id,
            is_deleted=False
        )

        if payment_type:
            query = query.filter_by(payment_type=payment_type)

        return query.order_by(cls.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @classmethod
    def get_by_payment_no(cls, payment_no):
        """
        根据支付单号获取支付记录
        """
        tenant_id = getattr(__import__('flask').g, 'tenant_id', 1)
        return cls.query.filter_by(
            payment_no=payment_no,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()


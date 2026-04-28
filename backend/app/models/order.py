"""
订单模型
"""
from datetime import datetime, timedelta
import random
import json
from .base import BaseModel
from .. import db

class Order(BaseModel):
    """订单模型"""
    __tablename__ = 'orders'

    # 基本信息
    order_no = db.Column(db.String(50), unique=True, nullable=False, comment='订单号')
    order_type = db.Column(db.String(20), nullable=False, default='rental', comment='订单类型')  # rental/purchase/exchange
    status = db.Column(db.String(20), default='pending', comment='订单状态')  # pending/paid/rented/returned/completed/cancelled/refunded
    source = db.Column(db.String(20), default='miniapp', comment='订单来源')

    # 关联信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    battery_id = db.Column(db.Integer, db.ForeignKey('batteries.id'), comment='电池ID')
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='站点ID')
    cabinet_id = db.Column(db.Integer, db.ForeignKey('cabinets.id'), comment='柜子ID')
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), comment='套餐ID')

    # 时间信息
    rental_start_time = db.Column(db.DateTime, comment='租用开始时间')
    rental_end_time = db.Column(db.DateTime, comment='租用结束时间')
    expected_return_time = db.Column(db.DateTime, comment='预计归还时间')
    actual_return_time = db.Column(db.DateTime, comment='实际归还时间')
    timeout_cancel_at = db.Column(db.DateTime, comment='超时取消时间')

    # 费用信息
    rental_hours = db.Column(db.Integer, default=24, comment='租用时长(小时)')
    unit_price = db.Column(db.Numeric(8, 2), comment='单价(元/小时)')
    rental_fee = db.Column(db.Numeric(8, 2), default=0.00, comment='租用费用')
    deposit_fee = db.Column(db.Numeric(8, 2), default=0.00, comment='押金费用')
    total_amount = db.Column(db.Numeric(8, 2), default=0.00, comment='总金额')
    exchange_fee = db.Column(db.Numeric(8, 2), default=0.00, comment='换电费用')
    pricing_snapshot = db.Column(db.JSON, comment='计费快照')

    # 支付信息
    payment_method = db.Column(db.String(20), comment='支付方式')
    payment_time = db.Column(db.DateTime, comment='支付时间')
    transaction_id = db.Column(db.String(100), comment='交易号')
    refund_status = db.Column(db.String(20), default='none', comment='退款状态')

    # 退款信息
    refund_amount = db.Column(db.Numeric(8, 2), default=0.00, comment='退款金额')
    refund_time = db.Column(db.DateTime, comment='退款时间')
    refund_reason = db.Column(db.String(200), comment='退款原因')

    # 位置信息
    pickup_location = db.Column(db.String(500), comment='取电地点')
    return_location = db.Column(db.String(500), comment='还电地点')
    pickup_latitude = db.Column(db.Numeric(10, 7), comment='取电纬度')
    pickup_longitude = db.Column(db.Numeric(10, 7), comment='取电经度')
    return_latitude = db.Column(db.Numeric(10, 7), comment='还电纬度')
    return_longitude = db.Column(db.Numeric(10, 7), comment='还电经度')

    # 备注信息
    remarks = db.Column(db.Text, comment='备注')
    cancel_reason = db.Column(db.String(200), comment='取消原因')
    close_reason = db.Column(db.String(200), comment='关闭原因')

    # 关联对象
    user = db.relationship('User', backref='orders')
    battery = db.relationship('Battery', backref='orders')
    station = db.relationship('Station', backref='orders')
    cabinet = db.relationship('Cabinet', backref='orders')
    package = db.relationship('Package', backref='orders')

    # 订单状态机定义
    VALID_STATUS_TRANSITIONS = {
        'pending': {'paid', 'rented', 'cancelled'},
        'paid': {'rented', 'cancelled', 'refunded', 'completed'},
        'rented': {'returned', 'completed'},
        'returned': {'completed', 'refunded'},
        'completed': {'refunded'},
        'cancelled': set(),
        'refunded': set()
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_no:
            self.order_no = self.generate_order_no()

    @staticmethod
    def generate_order_no():
        """生成订单号"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = random.randint(1000, 9999)
        return f"ORD{timestamp}{random_str}"

    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['is_overdue'] = self.is_overdue()
        # 便于前端展示的冗余字段
        try:
            data['battery_code'] = self.battery.battery_code if self.battery else None
        except Exception:
            data['battery_code'] = None
        try:
            data['station_name'] = self.station.name if self.station else None
        except Exception:
            data['station_name'] = None
        try:
            data['package_name'] = self.package.name if self.package else None
        except Exception:
            data['package_name'] = None
        return data

    def is_overdue(self):
        """检查是否逾期"""
        if self.expected_return_time and self.status == 'rented':
            return datetime.now() > self.expected_return_time
        return False

    def cancel_order(self, reason=None):
        """取消订单"""
        if not self.can_transition_to('cancelled'):
            return False, "订单无法取消"
        self.status = 'cancelled'
        self.cancel_reason = reason
        self.save()
        return True, "订单已取消"

    def can_transition_to(self, target_status):
        """检查状态是否允许迁移"""
        return target_status in self.VALID_STATUS_TRANSITIONS.get(self.status, set())

    def transition_status(self, target_status, reason=None):
        """按状态机规则迁移订单状态"""
        if not self.can_transition_to(target_status):
            return False, f"订单状态不允许从 {self.status} 变更为 {target_status}"

        self.status = target_status
        if target_status == 'cancelled' and reason:
            self.cancel_reason = reason
            self.close_reason = reason
        self.save()
        return True, "订单状态更新成功"

    @classmethod
    def get_by_order_no(cls, order_no):
        """根据订单号获取订单"""
        from flask import g
        tenant_id = getattr(g, 'tenant_id', 1)
        return cls.query.filter_by(order_no=order_no, tenant_id=tenant_id, is_deleted=False).first()

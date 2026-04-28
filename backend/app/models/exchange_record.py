"""
换电记录模型
"""
from .base import BaseModel
from .. import db


class ExchangeRecord(BaseModel):
    """换电记录"""
    __tablename__ = 'exchange_records'

    record_no = db.Column(db.String(50), nullable=False, unique=True, comment='换电记录号')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), comment='关联订单ID')
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='站点ID')
    cabinet_id = db.Column(db.Integer, db.ForeignKey('cabinets.id'), comment='柜机ID')
    old_battery_id = db.Column(db.Integer, db.ForeignKey('batteries.id'), comment='旧电池ID')
    new_battery_id = db.Column(db.Integer, db.ForeignKey('batteries.id'), comment='新电池ID')
    exchange_fee = db.Column(db.Numeric(10, 2), default=0.00, comment='换电费用')
    status = db.Column(db.String(20), default='completed', comment='状态 pending/completed/failed')
    operator_type = db.Column(db.String(20), default='user', comment='操作人类型')
    remarks = db.Column(db.String(255), comment='备注')

    user = db.relationship('User', backref='exchange_records')
    order = db.relationship('Order', backref='exchange_records')
    station = db.relationship('Station', backref='exchange_records')
    cabinet = db.relationship('Cabinet', backref='exchange_records')
    old_battery = db.relationship('Battery', foreign_keys=[old_battery_id], backref='out_exchange_records')
    new_battery = db.relationship('Battery', foreign_keys=[new_battery_id], backref='in_exchange_records')

    @staticmethod
    def generate_record_no():
        from datetime import datetime
        import random
        return f"EXC{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.record_no:
            self.record_no = self.generate_record_no()

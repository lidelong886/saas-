"""
电池预约模型
"""
from datetime import datetime
from .base import BaseModel
from .. import db


class RiderReservation(BaseModel):
    """电池预约表"""
    __tablename__ = 'rider_reservations'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False, comment='站点ID')
    battery_id = db.Column(db.Integer, db.ForeignKey('batteries.id'), nullable=True, comment='预约的电池ID')

    reserved_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='预约时间')
    expires_at = db.Column(db.DateTime, nullable=False, comment='过期时间')

    status = db.Column(db.String(20), default='pending', comment='状态: pending/confirmed/completed/cancelled/timeout')
    timeout_job_id = db.Column(db.String(100), nullable=True, comment='超时任务ID')

    # 关联对象
    user = db.relationship('User', foreign_keys=[user_id], backref='reservations')
    station = db.relationship('Station', foreign_keys=[station_id], backref='reservations')
    battery = db.relationship('Battery', foreign_keys=[battery_id], backref='reservations')

    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        # 添加关联信息
        if self.station:
            data['station_name'] = self.station.name
            data['station_address'] = self.station.address
        if self.battery:
            data['battery_code'] = self.battery.battery_code
            data['battery_power_level'] = self.battery.power_level
        return data

    def is_expired(self):
        """检查是否已过期"""
        return datetime.now() > self.expires_at

    def can_cancel(self):
        """检查是否可以取消"""
        return self.status in ['pending', 'confirmed']

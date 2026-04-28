"""
故障报修模型
"""
from datetime import datetime
import random
from .base import BaseModel
from .. import db


class FaultReport(BaseModel):
    """故障报修"""
    __tablename__ = 'fault_reports'

    report_no = db.Column(db.String(50), unique=True, nullable=False, comment='工单号')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='关联站点ID')
    battery_id = db.Column(db.Integer, db.ForeignKey('batteries.id'), comment='关联电池ID')
    fault_type = db.Column(db.String(20), nullable=False, comment='故障类型 battery/cabinet/station/other')
    description = db.Column(db.Text, nullable=False, comment='故障描述')
    images = db.Column(db.JSON, comment='图片URL列表')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    status = db.Column(db.String(20), default='pending', comment='状态 pending/processing/resolved/closed')
    admin_remarks = db.Column(db.String(500), comment='管理员备注')
    resolved_at = db.Column(db.DateTime, comment='解决时间')

    user = db.relationship('User', backref='fault_reports')
    station = db.relationship('Station', backref='fault_reports')
    battery = db.relationship('Battery', backref='fault_reports')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.report_no:
            self.report_no = self.generate_report_no()

    @staticmethod
    def generate_report_no():
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        rand = random.randint(1000, 9999)
        return f"RPT{timestamp}{rand}"

    def to_dict(self):
        data = super().to_dict()
        try:
            data['station_name'] = self.station.name if self.station else None
        except Exception:
            data['station_name'] = None
        return data

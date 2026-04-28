"""
电池模型
"""
from datetime import datetime, timedelta
from .base import BaseModel
from .. import db

class Battery(BaseModel):
    """电池模型"""
    __tablename__ = 'batteries'

    # 基本信息
    battery_code = db.Column(db.String(50), unique=True, nullable=False, comment='电池编码')
    battery_type = db.Column(db.String(20), default='lithium_ion', comment='电池类型')  # lithium_ion/lithium_polymer/lead_acid
    model = db.Column(db.String(100), nullable=False, comment='电池型号')
    capacity = db.Column(db.Integer, nullable=False, comment='电池容量(mAh)')
    voltage_type = db.Column(db.String(10), default='60V', comment='电压类型')  # 60V/72V

    # 状态信息
    status = db.Column(db.String(20), default='available', comment='电池状态')  # available/rented/charging/maintenance/scrapped
    power_level = db.Column(db.Integer, default=100, comment='电量百分比(0-100)')
    voltage = db.Column(db.Numeric(5, 2), comment='电压(V)')
    temperature = db.Column(db.Numeric(5, 1), comment='温度(°C)')

    # 位置信息
    current_station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='当前所在站点ID')
    current_cabinet_id = db.Column(db.Integer, db.ForeignKey('cabinets.id'), comment='当前所在柜子ID')
    slot_position = db.Column(db.String(20), comment='柜子位置')

    # 使用信息
    current_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='当前使用者ID')
    rented_at = db.Column(db.DateTime, comment='租用时间')
    expected_return_at = db.Column(db.DateTime, comment='预计归还时间')

    # 所有权信息 (支持用户买断自己的电池)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='所有者ID（若为空则属于平台）')
    selling_price = db.Column(db.Numeric(8, 2), default=0.00, comment='售卖价格')

    # 维护信息
    last_maintenance_at = db.Column(db.DateTime, comment='最后维护时间')
    next_maintenance_at = db.Column(db.DateTime, comment='下次维护时间')
    maintenance_count = db.Column(db.Integer, default=0, comment='维护次数')

    # 生命周期
    purchase_date = db.Column(db.Date, comment='购买日期')
    warranty_period = db.Column(db.Integer, default=24, comment='质保期(月)')
    total_usage_hours = db.Column(db.Integer, default=0, comment='总使用时长(小时)')
    cycle_count = db.Column(db.Integer, default=0, comment='循环次数')

    # 价格信息
    rental_price_per_hour = db.Column(db.Numeric(8, 2), default=0.50, comment='每小时租用价格')
    deposit_amount = db.Column(db.Numeric(8, 2), default=50.00, comment='押金金额')

    # 设备信息
    imei = db.Column(db.String(50), comment='IMEI号')
    bluetooth_mac = db.Column(db.String(20), comment='蓝牙MAC地址')
    firmware_version = db.Column(db.String(20), comment='固件版本')

    # 关联对象
    current_station = db.relationship('Station', foreign_keys=[current_station_id], backref='batteries')
    current_cabinet = db.relationship('Cabinet', foreign_keys=[current_cabinet_id], backref='batteries')
    current_user = db.relationship('User', foreign_keys=[current_user_id], backref='rented_batteries')

    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        return data

    def is_available(self):
        """检查电池是否可用"""
        if self.owner_id is not None:
            from flask import g
            # 允许拥有者自己操作（可选，不过一般租用流程不适用于私有电池）
            # return self.status == 'available' and self.power_level >= 20
            return False
        return self.status == 'available' and self.power_level >= 20

    def rent_to_user(self, user_id, hours=24):
        """租用给用户"""
        if not self.is_available():
            return False, "电池不可用"
        self.current_user_id = user_id
        self.status = 'rented'
        self.rented_at = datetime.now()
        self.expected_return_at = datetime.now() + timedelta(hours=hours)
        self.save()
        return True, "租用成功"

    def return_battery(self, station_id=None, cabinet_id=None):
        """归还电池"""
        if self.status != 'rented':
            return False, "电池不在使用中"
        if self.rented_at:
            usage_hours = int((datetime.now() - self.rented_at).total_seconds() / 3600)
            self.total_usage_hours += usage_hours
        self.current_user_id = None
        self.status = 'available'
        self.rented_at = None
        self.expected_return_at = None
        if station_id is not None:
            self.current_station_id = station_id
        if cabinet_id is not None:
            self.current_cabinet_id = cabinet_id
        self.last_return_time = datetime.now()
        self.save()
        return True, "归还成功"

    @classmethod
    def get_by_code(cls, battery_code):
        """根据电池编码获取电池"""
        from flask import g
        tenant_id = getattr(g, 'tenant_id', 1)
        return cls.query.filter_by(battery_code=battery_code, tenant_id=tenant_id, is_deleted=False).first()

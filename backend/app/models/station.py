"""
站点模型
"""
import math
from flask import g
from .base import BaseModel
from .. import db

class Station(BaseModel):
    """充电换电站点模型"""
    __tablename__ = 'stations'

    # 基本信息
    station_code = db.Column(db.String(50), unique=True, nullable=False, comment='站点编码')
    name = db.Column(db.String(100), nullable=False, comment='站点名称')
    type = db.Column(db.String(20), default='street', comment='站点类型')  # street/mall/office/residential/parking
    status = db.Column(db.String(20), default='active', comment='站点状态')  # active/maintenance/inactive

    # 地理位置
    latitude = db.Column(db.Numeric(10, 7), nullable=False, comment='纬度')
    longitude = db.Column(db.Numeric(10, 7), nullable=False, comment='经度')
    address = db.Column(db.String(500), nullable=False, comment='详细地址')
    city = db.Column(db.String(50), comment='城市')
    district = db.Column(db.String(50), comment='区县')

    # 运营信息
    phone = db.Column(db.String(20), comment='联系电话')
    business_hours = db.Column(db.String(50), comment='营业时间')
    open_time = db.Column(db.Time, comment='开放时间')
    close_time = db.Column(db.Time, comment='关闭时间')
    is_24_hour = db.Column(db.Boolean, default=False, comment='是否24小时开放')

    # 设施信息
    total_cabinets = db.Column(db.Integer, default=0, comment='柜子总数')
    total_slots = db.Column(db.Integer, default=0, comment='插槽总数')
    available_slots = db.Column(db.Integer, default=0, comment='可用插槽数')

    # 电池统计
    total_batteries = db.Column(db.Integer, default=0, comment='电池总数')
    available_batteries = db.Column(db.Integer, default=0, comment='可用电池数')
    charging_batteries = db.Column(db.Integer, default=0, comment='充电中电池数')

    # 运营数据
    monthly_rentals = db.Column(db.Integer, default=0, comment='月租用次数')
    monthly_revenue = db.Column(db.Numeric(12, 2), default=0.00, comment='月收入')

    # 设备信息
    network_status = db.Column(db.Boolean, default=True, comment='网络状态')
    last_heartbeat = db.Column(db.DateTime, comment='最后心跳时间')
    firmware_version = db.Column(db.String(20), comment='固件版本')
    images = db.Column(db.JSON, comment='站点图片URL列表')

    def to_dict(self, include_stats=True):
        """转换为字典"""
        data = super().to_dict()
        if include_stats and self.total_slots > 0:
            data['occupancy_rate'] = (self.total_slots - self.available_slots) / self.total_slots * 100
        return data

    @classmethod
    def get_by_code(cls, station_code):
        """根据站点编码获取站点"""
        tenant_id = getattr(g, 'tenant_id', 1)
        return cls.query.filter_by(station_code=station_code, tenant_id=tenant_id, is_deleted=False).first()

    @classmethod
    def find_nearby_stations(cls, latitude, longitude, radius_km=3, limit=20):
        """
        按球面距离查找附近站点，返回 to_dict 列表并带 distance（米，整数）
        """
        tenant_id = getattr(g, 'tenant_id', 1)
        lat0, lng0 = float(latitude), float(longitude)
        r_km = float(radius_km)
        lim = int(limit) if limit else 20

        def haversine_km(lat1, lon1, lat2, lon2):
            r_earth = 6371.0
            p1, p2 = math.radians(lat1), math.radians(lat2)
            dlat = math.radians(lat2 - lat1)
            dlng = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
            c = 2 * math.asin(min(1.0, math.sqrt(a)))
            return r_earth * c

        rows = cls.query.filter_by(tenant_id=tenant_id, is_deleted=False).all()
        scored = []
        for s in rows:
            try:
                d_km = haversine_km(lat0, lng0, float(s.latitude), float(s.longitude))
            except (TypeError, ValueError):
                continue
            if d_km <= r_km:
                item = s.to_dict()
                item['distance'] = int(round(d_km * 1000))
                scored.append((d_km, item))

        scored.sort(key=lambda x: x[0])
        return [item for _, item in scored[:lim]]

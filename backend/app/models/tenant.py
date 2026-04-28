"""
租户模型
"""
from .base import BaseModel
from .. import db


class Tenant(BaseModel):
    """租户模型"""
    __tablename__ = 'tenants'

    name = db.Column(db.String(100), nullable=False, unique=True, comment='租户名称')
    code = db.Column(db.String(50), nullable=False, unique=True, comment='租户编码')
    brand_name = db.Column(db.String(100), comment='品牌名称')  # 运营商品牌
    brand_logo = db.Column(db.String(500), comment='品牌Logo URL')  # 品牌Logo
    contact_name = db.Column(db.String(50), comment='联系人')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    contact_email = db.Column(db.String(120), comment='联系邮箱')
    status = db.Column(db.String(20), default='active', comment='状态 active/disabled')
    max_users = db.Column(db.Integer, default=100, comment='用户配额')
    max_stations = db.Column(db.Integer, default=20, comment='站点配额')
    max_batteries = db.Column(db.Integer, default=1000, comment='电池配额')
    remarks = db.Column(db.String(500), comment='备注')

    def to_dict(self):
        data = super().to_dict()
        data['is_active'] = self.status == 'active'
        return data

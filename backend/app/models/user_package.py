"""
用户套餐/卡券 模型
用于记录用户购买但尚未使用的，或者正在使用的套餐
"""
from datetime import datetime, timedelta
from .base import BaseModel
from .. import db

class UserPackage(BaseModel):
    """用户套餐/卡券模型"""
    __tablename__ = 'user_packages'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False, comment='套餐ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), comment='来源订单ID')
    
    status = db.Column(db.String(20), default='unused', comment='状态: unused/active/expired/exhausted')
    
    # 卡券相关属性（从原Package复制以便快照）
    package_name = db.Column(db.String(100), nullable=False)
    package_type = db.Column(db.String(20))
    total_hours = db.Column(db.Integer, comment='套餐包含总时长(小时)')
    
    # 使用时间
    activated_at = db.Column(db.DateTime, comment='激活/开始使用时间')
    expires_at = db.Column(db.DateTime, comment='过期时间')
    
    # NOTE: REMOVED db.relationship for order to prevent recursive import issues or parsing issues.

    def to_dict(self):
        data = super().to_dict()
        return data

    def activate(self):
        """激活卡券"""
        if self.status != 'unused':
            return False, "卡券状态不可激活"
        self.status = 'active'
        self.activated_at = datetime.now()
        if self.total_hours:
            self.expires_at = self.activated_at + timedelta(hours=self.total_hours)
        self.save()
        return True, "激活成功"
        
    @property
    def is_valid(self):
        if self.status != 'active':
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True

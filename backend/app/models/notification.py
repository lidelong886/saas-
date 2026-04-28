"""
消息通知模型
"""
from .base import BaseModel
from .. import db


class Notification(BaseModel):
    """消息通知"""
    __tablename__ = 'notifications'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    noti_type = db.Column(db.String(20), nullable=False, comment='通知类型 order/exchange/system/fault')
    title = db.Column(db.String(100), nullable=False, comment='标题')
    content = db.Column(db.String(500), comment='内容')
    is_read = db.Column(db.Boolean, default=False, comment='是否已读')
    link_type = db.Column(db.String(20), comment='关联类型 order/exchange/fault/none')
    link_id = db.Column(db.String(50), comment='关联业务ID')

    user = db.relationship('User', backref='notifications')

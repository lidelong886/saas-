"""后台操作日志模型"""
from .base import BaseModel
from .. import db


class OperationLog(BaseModel):
    __tablename__ = 'operation_logs'

    operator_id = db.Column(db.Integer, comment='操作管理员ID')
    operator = db.Column(db.String(100), nullable=False, comment='操作人')
    action = db.Column(db.String(100), nullable=False, comment='操作动作')
    target = db.Column(db.String(200), comment='操作对象')
    module = db.Column(db.String(50), comment='所属模块')
    status = db.Column(db.String(20), default='success', comment='操作结果 success/warning/danger')
    ip = db.Column(db.String(64), comment='IP地址')
    extra = db.Column(db.JSON, comment='扩展信息')

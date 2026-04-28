"""
用户行为日志模型
"""
from datetime import datetime
from .base import BaseModel
from .. import db


class UserBehaviorLog(BaseModel):
    """用户行为日志表"""
    __tablename__ = 'user_behavior_logs'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    action_type = db.Column(db.String(50), nullable=False, comment='行为类型: swap/reserve/view_station/purchase_package/cancel_reserve')
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=True, comment='关联站点ID')
    extra_data = db.Column(db.JSON, comment='元数据（JSON格式）')

    # 关联对象
    user = db.relationship('User', foreign_keys=[user_id], backref='behavior_logs')
    station = db.relationship('Station', foreign_keys=[station_id], backref='behavior_logs')

    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        return data

    @classmethod
    def log_action(cls, user_id, action_type, station_id=None, extra_data=None):
        """记录用户行为（异步记录，不阻塞主流程）"""
        try:
            log = cls(
                user_id=user_id,
                action_type=action_type,
                station_id=station_id,
                extra_data=extra_data or {}
            )
            log.save()
            return True
        except Exception as e:
            # 日志记录失败不影响主流程
            print(f"Failed to log user behavior: {str(e)}")
            return False

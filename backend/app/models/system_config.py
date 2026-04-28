"""
系统配置模型 - 持久化存储 AMAP Key、微信支付等配置
"""
from datetime import datetime
from .. import db


class SystemConfig(db.Model):
    """
    系统配置表（键值对形式，支持多租户）
    """
    __tablename__ = 'system_configs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(64), unique=True, nullable=False, comment='配置键')
    value = db.Column(db.Text, nullable=True, comment='配置值')
    description = db.Column(db.String(255), nullable=True, comment='说明')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<SystemConfig {self.key}>'

    @classmethod
    def get_value(cls, key, default=None):
        """读取配置值，不存在则返回默认值"""
        record = cls.query.filter_by(key=key).first()
        return record.value if record else default

    @classmethod
    def set_value(cls, key, value, description=None):
        """写入或更新配置值"""
        record = cls.query.filter_by(key=key).first()
        if record:
            record.value = value
            if description is not None:
                record.description = description
        else:
            record = cls(key=key, value=value, description=description)
            db.session.add(record)
        db.session.commit()
        return record

    @classmethod
    def get_all(cls):
        """读取所有配置，返回 {key: value} 字典"""
        records = cls.query.all()
        return {r.key: r.value for r in records}

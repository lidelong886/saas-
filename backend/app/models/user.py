"""
用户模型
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta
from .base import BaseModel
from .. import db

class User(BaseModel):
    """
    用户模型
    """
    __tablename__ = 'users'

    # 基本信息
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='邮箱')
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='手机号')
    password_hash = db.Column(db.String(256), nullable=False, comment='密码哈希')
    avatar = db.Column(db.String(500), comment='头像URL')
    wechat_openid = db.Column(db.String(100), unique=True, comment='微信OpenID')
    wechat_unionid = db.Column(db.String(100), comment='微信UnionID')
    auth_source = db.Column(db.String(20), default='password', comment='认证来源')

    # 个人信息
    nickname = db.Column(db.String(50), comment='昵称')
    real_name = db.Column(db.String(50), comment='真实姓名')
    id_card_no = db.Column(db.String(30), comment='身份证号')
    realname_status = db.Column(db.String(20), default='unverified', comment='实名认证状态')
    gender = db.Column(db.Enum('male', 'female', 'unknown'), default='unknown', comment='性别')
    birth_date = db.Column(db.Date, comment='出生日期')

    # 账户状态
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    is_verified = db.Column(db.Boolean, default=False, comment='是否实名认证')
    disabled_reason = db.Column(db.String(255), comment='禁用原因')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')

    # 骑手信息（如果是骑手）
    is_rider = db.Column(db.Boolean, default=False, comment='是否为骑手')
    rider_level = db.Column(db.Enum('bronze', 'silver', 'gold', 'platinum'), default='bronze', comment='骑手等级')
    work_status = db.Column(db.Enum('offline', 'online', 'busy'), default='offline', comment='工作状态')

    # 积分和余额
    points = db.Column(db.Integer, default=0, comment='积分')
    balance = db.Column(db.Numeric(10, 2), default=0.00, comment='账户余额')

    # 地理位置信息
    latitude = db.Column(db.Numeric(10, 7), comment='纬度')
    longitude = db.Column(db.Numeric(10, 7), comment='经度')
    location_updated_at = db.Column(db.DateTime, comment='位置更新时间')

    # 设备信息
    device_id = db.Column(db.String(100), comment='设备ID')
    push_token = db.Column(db.String(500), comment='推送令牌')

    # 用户偏好设置
    preferences = db.Column(db.JSON, comment='用户偏好设置（JSON格式）')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.nickname:
            self.nickname = self.username

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        # 固定使用 pbkdf2，避免不同环境下默认算法不兼容
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_tokens(self):
        """
        生成JWT令牌
        """
        access_token = create_access_token(
            identity=str(self.id),
            additional_claims={
                'username': self.username,
                'tenant_id': self.tenant_id
            }
        )
        refresh_token = create_refresh_token(identity=str(self.id))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(timedelta(hours=2).total_seconds())
        }

    def update_location(self, latitude, longitude):
        """
        更新用户位置
        """
        self.latitude = latitude
        self.longitude = longitude
        self.location_updated_at = datetime.now()
        self.save()

    def update_last_login(self):
        """
        更新最后登录时间
        """
        self.last_login_at = datetime.now()
        self.save()

    def add_points(self, points):
        """
        添加积分
        """
        self.points += points
        self.save()

    def deduct_points(self, points):
        """
        扣除积分
        """
        if self.points >= points:
            self.points -= points
            self.save()
            return True
        return False

    def add_balance(self, amount):
        """
        增加余额
        """
        self.balance += amount
        self.save()

    def deduct_balance(self, amount, reason=''):
        """
        扣除余额
        """
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def to_dict(self, include_private=False):
        """
        转换为字典
        """
        data = super().to_dict()

        # 移除敏感信息
        data.pop('password_hash', None)

        if not include_private:
            # 普通用户不可见的字段
            private_fields = ['balance', 'points', 'device_id', 'push_token']
            for field in private_fields:
                data.pop(field, None)

        return data

    @classmethod
    def get_by_username(cls, username):
        """
        根据用户名获取用户
        """
        tenant_id = getattr(__import__('flask').g, 'tenant_id', 1)
        return cls.query.filter_by(
            username=username,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()

    @classmethod
    def get_by_phone(cls, phone):
        """
        根据手机号获取用户
        """
        tenant_id = getattr(__import__('flask').g, 'tenant_id', 1)
        return cls.query.filter_by(
            phone=phone,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()

    @classmethod
    def get_nearby_riders(cls, latitude, longitude, radius_km=5):
        """
        获取附近在线的骑手
        """
        tenant_id = getattr(__import__('flask').g, 'tenant_id', 1)

        # 简化的距离计算（实际应该使用数据库的地理函数）
        # 这里使用简单的经纬度范围估算
        lat_range = radius_km / 111.0  # 1度纬度约111km
        lng_range = radius_km / (111.0 * __import__('math').cos(__import__('math').radians(latitude))) if latitude != 0 else radius_km / 111.0

        return cls.query.filter(
            cls.tenant_id == tenant_id,
            cls.is_deleted == False,
            cls.is_rider == True,
            cls.work_status == 'online',
            cls.latitude.between(latitude - lat_range, latitude + lat_range),
            cls.longitude.between(longitude - lng_range, longitude + lng_range)
        ).all()


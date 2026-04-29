"""
配置文件
"""
import os
from datetime import timedelta


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = int(os.environ.get('REDIS_DB') or 0)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 高德地图API配置
    AMAP_KEY = os.environ.get('AMAP_KEY')

    # 微信支付配置
    WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID') or 'your-app-id'
    WECHAT_MCH_ID = os.environ.get('WECHAT_MCH_ID') or 'your-mch-id'
    WECHAT_PRIVATE_KEY = os.environ.get('WECHAT_PRIVATE_KEY') or 'your-private-key'
    WECHAT_SERIAL_NO = os.environ.get('WECHAT_SERIAL_NO') or 'your-serial-no'

    # 分页配置
    ITEMS_PER_PAGE = 20

    # 订单状态机/超时配置
    ORDER_PENDING_TIMEOUT_MINUTES = int(os.environ.get('ORDER_PENDING_TIMEOUT_MINUTES') or 15)
    ORDER_TIMEOUT_SCAN_INTERVAL_SECONDS = int(os.environ.get('ORDER_TIMEOUT_SCAN_INTERVAL_SECONDS') or 60)

    # 数据初始化配置：开发演示可自动建表和填充数据，生产环境必须显式开启
    AUTO_CREATE_TABLES = os.environ.get('AUTO_CREATE_TABLES', 'false').lower() == 'true'
    ENABLE_DEMO_DATA = os.environ.get('ENABLE_DEMO_DATA', 'false').lower() == 'true'

    # CORS配置：开发环境可放开，生产环境必须通过环境变量显式配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or '*'

    @classmethod
    def validate_required_config(cls):
        if getattr(cls, 'DEBUG', False):
            return
        required = {
            'SECRET_KEY': cls.SECRET_KEY,
            'JWT_SECRET_KEY': cls.JWT_SECRET_KEY,
            'AMAP_KEY': cls.AMAP_KEY,
            'DATABASE_URL': getattr(cls, 'SQLALCHEMY_DATABASE_URI', None),
            'CORS_ORIGINS': cls.CORS_ORIGINS if cls.CORS_ORIGINS != '*' else None,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"缺少必要环境变量: {', '.join(missing)}")


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SECRET_KEY = Config.SECRET_KEY or os.environ.get('DEV_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = Config.JWT_SECRET_KEY or os.environ.get('DEV_JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    AMAP_KEY = Config.AMAP_KEY or os.environ.get('DEV_AMAP_KEY', '')
    AUTO_CREATE_TABLES = os.environ.get('AUTO_CREATE_TABLES', 'true').lower() == 'true'
    ENABLE_DEMO_DATA = os.environ.get('ENABLE_DEMO_DATA', 'true').lower() == 'true'
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # 开发环境默认使用 SQLite，避免硬编码 MySQL 密码
        sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'battery_saas_dev.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{sqlite_path}'
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'false').lower() == 'true'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS')

    # 生产环境JWT配置更严格
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

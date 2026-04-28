"""
电池SaaS平台Flask应用初始化
"""
import os
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import logging
from redis import Redis
import pymysql

# 数据库实例
db = SQLAlchemy()
migrate = Migrate()

# Redis实例
redis_client = Redis()

# SocketIO实例
socketio = SocketIO()

# 限流器实例（开发环境禁用限流）
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # 禁用默认限流
    storage_uri="memory://"
)


def create_app(config_name='development'):
    """
    应用工厂函数
    """
    app = Flask(__name__)

    from .config import config
    config_class = config[config_name]
    config_class.validate_required_config()
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    # 初始化限流器
    limiter.init_app(app)

    # 初始化SocketIO
    socketio.init_app(app, cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'))

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        from flask import make_response
        import json
        return make_response(json.dumps({"code": 401, "msg": "Missing token", "message": "Missing token"}), 401, {'Content-Type': 'application/json'})

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        from flask import make_response
        import json
        return make_response(json.dumps({"code": 401, "msg": "Invalid token", "message": "Invalid token"}), 401, {'Content-Type': 'application/json'})
        
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from flask import make_response
        import json
        return make_response(json.dumps({"code": 401, "msg": "Token has expired", "message": "Token has expired"}), 401, {'Content-Type': 'application/json'})
    # CORS 配置：从环境变量读取允许的域名列表
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    if cors_origins == '*':
        app.logger.warning('CORS 配置为 * (允许所有来源)，生产环境请配置具体域名')
        CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)
    else:
        origins_list = [origin.strip() for origin in cors_origins.split(',')]
        CORS(app, resources={r"/api/*": {"origins": origins_list}}, supports_credentials=False)
        app.logger.info(f'CORS 已配置允许的域名: {origins_list}')

    global redis_client
    try:
        redis_client = Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            password=app.config.get('REDIS_PASSWORD'),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        redis_client.ping()
        app.logger.info('Redis连接成功')
    except Exception as e:
        app.logger.warning(f'Redis连接失败，将使用内存缓存: {str(e)}')

        class MemoryCache:
            def __init__(self):
                self._cache = {}
                self._lists = {}

            def _purge_expired(self, key):
                item = self._cache.get(key)
                if not item:
                    return None
                value, expires_at = item
                if expires_at and expires_at <= datetime.now():
                    self._cache.pop(key, None)
                    return None
                return value

            def _set_value(self, key, value, ttl=None):
                expires_at = datetime.now() + timedelta(seconds=ttl) if ttl else None
                self._cache[key] = (value, expires_at)

            def get(self, key):
                return self._purge_expired(key)

            def set(self, key, value, ex=None):
                self._set_value(key, value, ex)
                return True

            def setex(self, key, time, value):
                self._set_value(key, value, time)
                return True

            def delete(self, key):
                deleted = 0
                if key in self._cache:
                    self._cache.pop(key, None)
                    deleted += 1
                if key in self._lists:
                    self._lists.pop(key, None)
                    deleted += 1
                return deleted

            def exists(self, key):
                if key in self._lists:
                    return True
                return self._purge_expired(key) is not None

            def ttl(self, key):
                item = self._cache.get(key)
                if not item:
                    return -2
                _, expires_at = item
                if not expires_at:
                    return -1
                remaining = int((expires_at - datetime.now()).total_seconds())
                if remaining < 0:
                    self._cache.pop(key, None)
                    return -2
                return remaining

            def expire(self, key, seconds):
                if seconds <= 0:
                    return False
                if key in self._cache:
                    value = self._purge_expired(key)
                    if value is None:
                        return False
                    self._set_value(key, value, seconds)
                    return True
                return False

            def lpush(self, key, value):
                self._lists.setdefault(key, [])
                self._lists[key].insert(0, value)
                return len(self._lists[key])

            def ltrim(self, key, start, end):
                values = self._lists.get(key, [])
                if end == -1:
                    self._lists[key] = values[start:]
                else:
                    self._lists[key] = values[start:end + 1]
                return True

            def lrange(self, key, start, end):
                values = self._lists.get(key, [])
                if end == -1:
                    return values[start:]
                return values[start:end + 1]

            def lindex(self, key, index):
                values = self._lists.get(key, [])
                if -len(values) <= index < len(values):
                    return values[index]
                return None

            def lset(self, key, index, value):
                values = self._lists.get(key, [])
                values[index] = value
                return True

            def ping(self):
                return True

        redis_client = MemoryCache()

    setup_logging(app)
    register_blueprints(app)

    # 注册WebSocket事件处理器
    from .websocket import events

    if not app.config.get('TESTING', False):
        from .tasks.order_scheduler import init_order_scheduler
        from .tasks.reservation_tasks import init_reservation_scheduler
        init_order_scheduler(app)
        init_reservation_scheduler(app)

    @app.before_request
    def before_request():
        from flask_jwt_extended import get_jwt, verify_jwt_in_request
        g.tenant_id = 1
        header_tenant_id = request.headers.get('X-Tenant-ID')
        if header_tenant_id:
            try:
                g.tenant_id = int(header_tenant_id)
            except (TypeError, ValueError):
                g.tenant_id = 1
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            if claims and 'tenant_id' in claims:
                g.tenant_id = int(claims['tenant_id'])
        except Exception as e:
            from flask_jwt_extended.exceptions import NoAuthorizationError
            from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
            import json
            import logging
            logging.error(f"JWT Verification failed: {type(e).__name__} - {str(e)}")
            
            # Allow completely missing authorization
            if isinstance(e, NoAuthorizationError) or "Missing Authorization Header" in str(e):
                pass
            # If a token was provided but it's expired
            elif isinstance(e, ExpiredSignatureError) or "Token has expired" in str(e):
                from flask import make_response
                import json
                return make_response(json.dumps({"code": 401, "msg": "Token has expired", "message": "Token has expired"}), 401, {'Content-Type': 'application/json'})
            # If a token was provided but it's invalid for other reasons
            elif isinstance(e, InvalidTokenError) or "Invalid" in str(e) or "Not enough segments" in str(e) or "codec can't decode" in str(e) or "decode" in str(e):
                from flask import make_response
                import json
                return make_response(json.dumps({"code": 401, "msg": "Invalid token", "message": "Invalid token"}), 401, {'Content-Type': 'application/json'})
            else:
                # 其他异常不应该阻止请求，允许通过（例如登录请求）
                pass

        g.request_start_time = datetime.now()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'request_start_time'):
            duration = datetime.now() - g.request_start_time
            response.headers['X-Response-Time'] = str(duration.total_seconds() * 1000) + 'ms'

        return response

    register_error_handlers(app)

    with app.app_context():
        try:
            db.create_all()
            app.logger.info('数据库表创建成功')
        except Exception as e:
            app.logger.error(f'数据库表创建失败: {str(e)}')
            app.logger.error('请检查数据库连接配置或确保数据库服务正在运行')
            if not app.config.get('DEBUG'):
                raise

    return app

def setup_logging(app):
    """
    配置日志
    """
    # 开发环境也输出到控制台
    if app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)
    else:
        # 生产环境日志
        handler = logging.FileHandler('app.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

def register_blueprints(app):
    """
    注册API蓝图
    """
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.battery import battery_bp
    from .routes.order import order_bp
    from .routes.station import station_bp
    from .routes.admin import admin_bp
    from .routes.health import health_bp
    from .routes.payment import payment_bp
    from .routes.exchange import exchange_bp
    from .routes.package import package_bp
    from .routes.admin_auth import admin_auth_bp
    from .routes.admin_tenant import admin_tenant_bp
    from .routes.rbac import rbac_bp
    from .routes.statistics import statistics_bp
    from .routes.recommend import recommend_bp
    from .routes.user_package import user_package_bp
    from .routes.battery_store import store_bp
    from .routes.fault_report import fault_report_bp
    from .routes.notification import notification_bp
    from .routes.rider import rider_bp
    from .routes.tenant_public import tenant_public_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user_bp, url_prefix='/api/v1/user')
    app.register_blueprint(battery_bp, url_prefix='/api/v1/battery')
    app.register_blueprint(order_bp, url_prefix='/api/v1/order')
    app.register_blueprint(station_bp, url_prefix='/api/v1/station')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(payment_bp, url_prefix='/api/v1/payment')
    app.register_blueprint(exchange_bp, url_prefix='/api/v1/exchange')
    app.register_blueprint(package_bp, url_prefix='/api/v1/package')
    app.register_blueprint(admin_auth_bp, url_prefix='/api/v1/admin-auth')
    app.register_blueprint(admin_tenant_bp, url_prefix='/api/v1/admin/tenant')
    app.register_blueprint(rbac_bp, url_prefix='/api/v1/admin/rbac')
    app.register_blueprint(statistics_bp, url_prefix='/api/v1/statistics')
    app.register_blueprint(recommend_bp, url_prefix='/api/v1/recommend')
    app.register_blueprint(user_package_bp, url_prefix='/api/v1/user-package')
    app.register_blueprint(store_bp, url_prefix='/api/v1/store')
    app.register_blueprint(fault_report_bp, url_prefix='/api/v1/fault-report')
    app.register_blueprint(notification_bp, url_prefix='/api/v1/notification')
    app.register_blueprint(rider_bp, url_prefix='/api/v1/rider')
    app.register_blueprint(tenant_public_bp, url_prefix='/api/v1/tenant')
    from .routes.battery_my import battery_my_bp
    app.register_blueprint(battery_my_bp, url_prefix='/api/v1/battery')
def register_error_handlers(app):
    """
    注册错误处理器
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'code': 400,
            'message': '请求参数错误',
            'data': {},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'code': 401,
            'message': '未授权访问',
            'data': {},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'code': 403,
            'message': '访问被拒绝',
            'data': {},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': '资源不存在',
            'data': {},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'服务器错误: {str(error)}')
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': {},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 500

    from jwt.exceptions import PyJWTError
    @app.errorhandler(PyJWTError)
    def handle_jwt_error(e):
        from flask import make_response
        import json
        return make_response(json.dumps({"code": 401, "msg": "Invalid token", "message": "Invalid token"}), 401, {'Content-Type': 'application/json'})

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, ValueError) and "codec can't decode" in str(e):
            from flask import make_response
            import json
            return make_response(json.dumps({"code": 401, "msg": "Invalid token", "message": "Invalid token format"}), 401, {'Content-Type': 'application/json'})
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return e
        app.logger.error(f'Unhandled exception: {str(e)}')
        from flask import jsonify
        from datetime import datetime
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': {},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 500

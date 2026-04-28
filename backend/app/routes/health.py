"""
健康检查路由
"""
from flask import Blueprint
from ..utils.response import success_response
from .. import db, redis_client
import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'services': {}
    }

    # 检查数据库连接
    try:
        # 兼容SQLite和MySQL的查询方式
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # 检查Redis连接
    try:
        redis_client.ping()
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # 检查应用状态
    health_status['services']['application'] = 'healthy'

    if health_status['status'] == 'healthy':
        return success_response(health_status, 'Health check OK')
    else:
        return success_response(health_status, 'Health check: some services down', 503)

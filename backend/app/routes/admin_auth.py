"""
后台管理员认证路由
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from .. import db
from ..services.admin_auth_service import AdminAuthService
from ..utils.response import success_response, error_response
from ..utils.operation_log import log_admin_action


admin_auth_bp = Blueprint('admin_auth', __name__)


@admin_auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        phone = data.get('username') or data.get('phone') or ''
        phone = str(phone).strip()
        password = data.get('password', '')
        if not phone or not password:
            return error_response('账号和密码不能为空', 400)
        success, result = AdminAuthService.login(phone, password)
        if not success:
            return error_response(result, 401)
        log_admin_action('登录系统', '管理后台', '认证中心', extra={'username': phone})
        db.session.commit()
        return success_response(result, '登录成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'管理员登录失败: {str(e)}', 500)


@admin_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        claims = get_jwt()
        admin_id = claims.get('admin_id')
        if admin_id:
            log_admin_action('退出登录', '管理后台', '认证中心', extra={'admin_id': admin_id})
            db.session.commit()
        return success_response(None, '退出成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'管理员退出失败: {str(e)}', 500)


@admin_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    try:
        claims = get_jwt()
        admin_id = claims.get('admin_id')
        if not admin_id:
            return error_response('当前不是管理员身份', 403)
        admin = AdminAuthService.get_current_admin(admin_id)
        if not admin:
            return error_response('管理员不存在', 404)
        data = admin.to_dict()
        data['permissions'] = sorted({perm.code for role in admin.roles for perm in role.permissions})
        return success_response(data, '获取当前管理员成功')
    except Exception as e:
        return error_response(f'获取当前管理员失败: {str(e)}', 500)

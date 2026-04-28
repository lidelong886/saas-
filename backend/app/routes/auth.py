"""
认证路由
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token
from sqlalchemy import or_
from ..utils.auth_helpers import get_current_user_id
from datetime import datetime, timedelta
import re

from ..models import User
from ..services.auth_service import AuthService
from ..utils.response import success_response, error_response
from ..utils.validators import validate_phone, validate_password, sanitize_input
from .. import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")  # 注册限制：每小时5次
def register():
    """用户注册"""
    try:
        data = request.get_json()
        required_fields = ['username', 'password', 'phone']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段: {field}', 400)

        username = sanitize_input(data['username'].strip(), max_length=20)
        password = data['password']
        phone = sanitize_input(data['phone'].strip(), max_length=11)

        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return error_response('用户名格式不正确（3-20位字母数字下划线）', 400)

        if User.query.filter_by(username=username, tenant_id=g.tenant_id, is_deleted=False).first():
            return error_response('用户名已存在', 400)

        if User.query.filter_by(phone=phone, tenant_id=g.tenant_id, is_deleted=False).first():
            return error_response('手机号已被注册', 400)

        user = User(
            username=username,
            phone=phone,
            email=sanitize_input(data.get('email', f'{username}@example.com').strip(), max_length=100),
            nickname=sanitize_input(data.get('nickname', '').strip() or username, max_length=50)
        )
        user.password = password
        user.save()

        tokens = user.generate_tokens()
        return success_response({'user': user.to_dict(), 'tokens': tokens}, '注册成功')
    except Exception as e:
        return error_response(f'注册失败: {str(e)}', 500)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")  # 登录限制：每分钟10次
def login():
    """用户登录"""
    try:
        data = request.get_json() or {}
        account = sanitize_input((data.get('username') or data.get('account') or '').strip(), max_length=100)
        password = data.get('password')

        if not account or not password:
            return error_response('账号和密码不能为空', 400)

        user = User.query.filter(
            User.tenant_id == g.tenant_id,
            User.is_deleted == False,
            or_(
                User.username == account,
                User.phone == account,
                User.email == account
            )
        ).first()
        if not user:
            return error_response('账号或密码错误', 401)
        if not user.is_active:
            return error_response('账号已被禁用', 401)
        if not user.verify_password(password):
            return error_response('账号或密码错误', 401)

        user.update_last_login()
        tokens = user.generate_tokens()
        return success_response({'user': user.to_dict(), 'tokens': tokens}, '登录成功')
    except Exception as e:
        return error_response(f'登录失败: {str(e)}', 500)

@auth_bp.route('/user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    try:
        current_user_id = get_current_user_id()
        user = User.get_by_id(current_user_id)
        if not user:
            return error_response('用户不存在', 401)
        return success_response(user.to_dict(include_private=True), '获取用户信息成功')
    except Exception as e:
        return error_response(f'获取用户信息失败: {str(e)}', 500)

@auth_bp.route('/refresh-token', methods=['POST'])
@jwt_required()
def refresh_token():
    """刷新访问令牌"""
    try:
        current_user_id = get_current_user_id()
        user = User.get_by_id(current_user_id)
        if not user:
            return error_response('用户不存在', 401)

        access_token = create_access_token(
            identity=user.id,
            additional_claims={'username': user.username, 'tenant_id': user.tenant_id}
        )
        return success_response({'access_token': access_token, 'token_type': 'Bearer'}, '令牌刷新成功')
    except Exception as e:
        return error_response(f'令牌刷新失败: {str(e)}', 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        return success_response(None, '登出成功')
    except Exception as e:
        return error_response(f'登出失败: {str(e)}', 500)

@auth_bp.route('/send-sms', methods=['POST'])
def send_sms():
    """发送短信验证码（模拟）"""
    try:
        data = request.get_json() or {}
        phone = (data.get('phone') or '').strip()
        sms_type = (data.get('type') or 'login').strip()
        if not phone:
            return error_response('手机号不能为空', 400)
        if not validate_phone(phone):
            return error_response('手机号格式不正确', 400)

        success, message = AuthService.send_sms_code(phone, sms_type)
        if not success:
            return error_response(message, 500)
        return success_response({'sms_type': sms_type}, message)
    except Exception as e:
        return error_response(f'发送验证码失败: {str(e)}', 500)

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json() or {}
        phone = (data.get('phone') or '').strip()
        code = (data.get('code') or '').strip()
        sms_type = (data.get('type') or 'reset_password').strip()
        new_password = data.get('new_password')

        if not phone or not new_password or not code:
            return error_response('手机号、验证码和新密码不能为空', 400)
        if not validate_phone(phone):
            return error_response('手机号格式不正确', 400)
        if not validate_password(new_password):
            return error_response('密码格式不正确（至少8位，包含字母和数字）', 400)
        if not AuthService.verify_sms_code(phone, code, sms_type):
            return error_response('验证码错误或已过期', 400)

        user = User.query.filter_by(phone=phone, tenant_id=g.tenant_id, is_deleted=False).first()
        if not user:
            return error_response('用户不存在', 400)

        user.password = new_password
        user.save()
        return success_response(None, '密码重置成功')
    except Exception as e:
        return error_response(f'密码重置失败: {str(e)}', 500)

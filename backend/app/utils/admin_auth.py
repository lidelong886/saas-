"""
后台管理员认证与权限工具
"""
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from .response import error_response


def admin_required():
    """要求管理员身份"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get('is_admin'):
                return error_response('需要管理员身份', 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission_code):
    """要求指定权限"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get('is_admin'):
                return error_response('需要管理员身份', 403)
            if claims.get('is_super_admin'):
                return fn(*args, **kwargs)

            permissions = claims.get('permissions', [])
            if permission_code not in permissions:
                return error_response('无权限执行此操作', 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

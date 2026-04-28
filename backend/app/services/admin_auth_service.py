"""
后台管理员认证服务
"""
from datetime import datetime
from flask_jwt_extended import create_access_token
from flask import g

from .. import db
from ..models import AdminUser


class AdminAuthService:
    """后台管理员认证服务"""

    @staticmethod
    def login(account, password):
        admin = AdminUser.query.filter(
            (AdminUser.phone == account) | (AdminUser.username == account),
            AdminUser.tenant_id == g.tenant_id,
            AdminUser.is_deleted == False
        ).first()
        if not admin:
            return False, '管理员不存在'
        if not admin.is_active:
            return False, '管理员已禁用'
        if not admin.verify_password(password):
            return False, '手机号或密码错误'

        admin.last_login_at = datetime.now()
        db.session.commit()

        permissions = sorted({perm.code for role in admin.roles for perm in role.permissions})

        token = create_access_token(
            identity=f'admin:{admin.id}',
            additional_claims={
                'admin_id': admin.id,
                'tenant_id': admin.tenant_id,
                'is_admin': True,
                'is_super_admin': admin.is_super_admin,
                'roles': [role.code for role in admin.roles],
                'permissions': permissions
            }
        )
        return True, {
            'token': token,
            'token_type': 'Bearer',
            'admin': admin.to_dict()
        }

    @staticmethod
    def get_current_admin(admin_id):
        return AdminUser.query.filter_by(id=admin_id, tenant_id=g.tenant_id, is_deleted=False).first()

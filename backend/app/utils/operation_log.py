"""后台操作日志工具"""
from flask import request, g
from flask_jwt_extended import get_jwt

from .. import db
from ..models import OperationLog, AdminUser


def log_admin_action(action, target='', module='系统管理', status='success', extra=None):
    try:
        claims = get_jwt() or {}
        admin_id = claims.get('admin_id')
        operator = 'admin'

        if admin_id:
            admin = AdminUser.query.filter_by(id=admin_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if admin:
                operator = getattr(admin, 'username', None) or getattr(admin, 'name', None) or 'admin'

        log = OperationLog(
            operator_id=admin_id,
            operator=operator,
            action=action,
            target=str(target or ''),
            module=module,
            status=status,
            ip=(request.headers.get('X-Forwarded-For') or request.remote_addr or '').split(',')[0].strip(),
            extra=extra or {},
            tenant_id=getattr(g, 'tenant_id', 1)
        )
        db.session.add(log)
        db.session.flush()
        return log
    except Exception:
        return None

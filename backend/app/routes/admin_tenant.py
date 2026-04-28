"""
租户管理路由 (超级管理员视角)
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from .. import db
from ..models.tenant import Tenant
from ..models.rbac import AdminUser
from ..utils.response import success_response, error_response
from ..utils.operation_log import log_admin_action

admin_tenant_bp = Blueprint('admin_tenant', __name__)

@admin_tenant_bp.route('/list', methods=['GET'])
@jwt_required()
def get_tenants():
    """获取租户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Tenant.query.filter_by(is_deleted=False)
        pagination = query.order_by(Tenant.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return success_response({
            'list': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page
        })
    except Exception as e:
        return error_response(f'获取租户列表失败: {str(e)}', 500)

@admin_tenant_bp.route('/register', methods=['POST'])
@jwt_required()
def register_tenant():
    """创建新租户（运营商入驻）"""
    try:
        data = request.get_json()
        required_fields = ['name', 'code', 'contact_name', 'contact_phone']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段: {field}', 400)
                
        # 检查是否重复
        if Tenant.query.filter_by(code=data['code'], is_deleted=False).first():
            return error_response('租户编码已存在', 400)
            
        tenant = Tenant(
            name=data['name'],
            code=data['code'],
            contact_name=data['contact_name'],
            contact_phone=data['contact_phone'],
            contact_email=data.get('contact_email'),
            max_users=data.get('max_users', 100),
            max_stations=data.get('max_stations', 20),
            max_batteries=data.get('max_batteries', 1000)
        )
        db.session.add(tenant)
        db.session.flush() # 获取ID
        
        # 可选：同时为该租户创建一个默认的租户管理员
        if data.get('create_admin') and data.get('admin_phone') and data.get('admin_password'):
            admin = AdminUser(
                username=data.get('admin_username', f"admin_{tenant.code}"),
                phone=data['admin_phone'],
                nickname=f"{tenant.name}管理员",
                tenant_id=tenant.id,
                is_super_admin=False
            )
            admin.password = data['admin_password']
            db.session.add(admin)
            
        log_admin_action('创建租户', '租户管理', '入驻', extra={'tenant_code': tenant.code})
        db.session.commit()
        return success_response(tenant.to_dict(), '租户创建成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建租户失败: {str(e)}', 500)

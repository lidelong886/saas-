"""
租户、角色、权限、管理员管理路由
"""
from flask import Blueprint, request, g

from ..models import Tenant, TenantApplication, Role, Permission, AdminUser, User, Station, Battery, Notification
from .. import db
from ..services.tenant_config_service import TenantConfigService
from ..utils.admin_auth import admin_required
from ..utils.response import success_response, error_response


rbac_bp = Blueprint('rbac', __name__)


def _build_tenant_code(name):
    base = ''.join(ch for ch in (name or '').upper() if ch.isalnum())[:12] or 'TENANT'
    code = base
    index = 1
    while Tenant.query.filter_by(code=code, is_deleted=False).first():
        index += 1
        code = f'{base}{index}'
    return code


@rbac_bp.route('/tenants', methods=['GET'])
@admin_required()
def get_tenants():
    try:
        if g.tenant_id != 1:
            return error_response('只有系统管理员可以管理租户', 403)
        items = Tenant.query.filter_by(is_deleted=False).order_by(Tenant.created_at.desc()).all()
        tenants = []
        for tenant in items:
            tenant_data = tenant.to_dict()
            tenant_data['user_count'] = User.query.filter_by(tenant_id=tenant.id, is_deleted=False).count()
            tenant_data['station_count'] = Station.query.filter_by(tenant_id=tenant.id, is_deleted=False).count()
            tenant_data['battery_count'] = Battery.query.filter_by(tenant_id=tenant.id, is_deleted=False).count()
            tenant_data.update(TenantConfigService.get_settings(tenant.id))
            tenants.append(tenant_data)
        return success_response(tenants, '获取租户列表成功')
    except Exception as e:
        return error_response(f'获取租户列表失败: {str(e)}', 500)


@rbac_bp.route('/tenants', methods=['POST'])
@admin_required()
def create_tenant():
    try:
        if g.tenant_id != 1:
            return error_response('只有系统管理员可以管理租户', 403)
        data = request.get_json() or {}
        if not data.get('name') or not data.get('code'):
            return error_response('name和code不能为空', 400)
        tenant = Tenant(
            name=data['name'],
            code=data['code'],
            contact_name=data.get('contact_name'),
            contact_phone=data.get('contact_phone'),
            contact_email=data.get('contact_email'),
            status=data.get('status', 'active'),
            max_users=data.get('max_users', 100),
            max_stations=data.get('max_stations', 20),
            max_batteries=data.get('max_batteries', 1000),
            remarks=data.get('remarks'),
            tenant_id=1
        )
        db.session.add(tenant)
        db.session.flush()
        TenantConfigService.set_settings(tenant.id, data)

        # 初始化租户管理员角色
        admin_role = Role(
            code='tenant_admin',
            name='租户管理员',
            scope='tenant',
            description='拥有本租户所有权限',
            tenant_id=tenant.id
        )
        # 关联所有现有权限（如果是租户级别）
        permissions = Permission.query.all()
        admin_role.permissions = permissions
        db.session.add(admin_role)

        # 初始化租户超级管理员账号
        if data.get('admin_phone') and data.get('admin_password'):
            from werkzeug.security import generate_password_hash
            new_admin = AdminUser(
                username=data.get('admin_username', 'admin'),
                phone=data['admin_phone'],
                password_hash=generate_password_hash(data['admin_password']),
                is_super_admin=True,
                tenant_id=tenant.id
            )
            new_admin.roles.append(admin_role)
            db.session.add(new_admin)

        db.session.commit()
        return success_response(tenant.to_dict(), '创建租户并初始化管理员成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建租户失败: {str(e)}', 500)


@rbac_bp.route('/tenants/<int:tenant_id>', methods=['PUT'])
@admin_required()
def update_tenant(tenant_id):
    try:
        if g.tenant_id != 1:
            return error_response('只有系统管理员可以管理租户', 403)
        tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first()
        if not tenant:
            return error_response('租户不存在', 404)

        data = request.get_json() or {}
        if data.get('code') and data['code'] != tenant.code:
            exists = Tenant.query.filter(
                Tenant.code == data['code'],
                Tenant.id != tenant_id,
                Tenant.is_deleted == False
            ).first()
            if exists:
                return error_response('租户编码已存在', 400)

        if data.get('name') and data['name'] != tenant.name:
            exists = Tenant.query.filter(
                Tenant.name == data['name'],
                Tenant.id != tenant_id,
                Tenant.is_deleted == False
            ).first()
            if exists:
                return error_response('租户名称已存在', 400)

        for field in [
            'name', 'code', 'brand_name', 'brand_logo', 'contact_name',
            'contact_phone', 'contact_email', 'status', 'max_users',
            'max_stations', 'max_batteries', 'remarks'
        ]:
            if field in data:
                setattr(tenant, field, data.get(field))

        TenantConfigService.set_settings(tenant.id, data)

        db.session.commit()
        result = tenant.to_dict()
        result.update(TenantConfigService.get_settings(tenant.id))
        return success_response(result, '租户更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新租户失败: {str(e)}', 500)


@rbac_bp.route('/tenants/<int:tenant_id>', methods=['DELETE'])
@admin_required()
def delete_tenant(tenant_id):
    try:
        if g.tenant_id != 1:
            return error_response('只有系统管理员可以管理租户', 403)
        if tenant_id == 1:
            return error_response('默认系统租户不能删除', 400)
        tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first()
        if not tenant:
            return error_response('租户不存在', 404)
        tenant.is_deleted = True
        db.session.commit()
        return success_response(None, '租户删除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除租户失败: {str(e)}', 500)


@rbac_bp.route('/tenant-applications', methods=['GET'])
@admin_required()
def get_tenant_applications():
    try:
        if g.tenant_id != 1:
            return error_response('只有系统管理员可以查看入驻申请', 403)
        status = request.args.get('status', '').strip()
        query = TenantApplication.query.filter_by(is_deleted=False)
        if status:
            query = query.filter_by(status=status)
        items = query.order_by(TenantApplication.created_at.desc()).all()
        result = []
        for item in items:
            data = item.to_dict()
            applicant = User.query.filter_by(id=item.applicant_user_id, is_deleted=False).first()
            data['applicant_name'] = applicant.username if applicant else ''
            data['applicant_phone'] = applicant.phone if applicant else ''
            result.append(data)
        return success_response(result, '获取入驻申请成功')
    except Exception as e:
        return error_response(f'获取入驻申请失败: {str(e)}', 500)


@rbac_bp.route('/tenant-applications/<int:application_id>/review', methods=['POST'])
@admin_required()
def review_tenant_application(application_id):
    try:
        if g.tenant_id != 1:
            return error_response('只有系统管理员可以审核入驻申请', 403)
        data = request.get_json() or {}
        action = data.get('action')
        remark = data.get('remark', '')

        application = TenantApplication.query.filter_by(id=application_id, is_deleted=False).first()
        if not application:
            return error_response('入驻申请不存在', 404)
        if application.status != 'pending':
            return error_response('该申请已处理', 400)

        if action == 'approve':
            tenant = Tenant(
                name=application.name,
                code=data.get('code') or _build_tenant_code(application.name),
                brand_name=application.name,
                contact_name=application.contact_name,
                contact_phone=application.contact_phone,
                status='active',
                remarks=application.message,
                tenant_id=1
            )
            tenant.save()
            application.status = 'approved'
            application.approved_tenant_id = tenant.id
            application.review_remark = remark or '已通过，租户已创建'
            if application.applicant_user_id:
                for noti_tenant_id in {application.tenant_id, tenant.id}:
                    Notification(
                        user_id=application.applicant_user_id,
                        noti_type='system',
                        title='入驻申请已通过',
                        content=f'您的“{application.name}”入驻申请已通过，租户已创建，可在小程序切换租户查看。',
                        link_type='none',
                        tenant_id=noti_tenant_id
                    ).save()
            application.save()
            return success_response({'application': application.to_dict(), 'tenant': tenant.to_dict()}, '审核通过并创建租户成功')

        if action == 'reject':
            application.status = 'rejected'
            application.review_remark = remark or '申请未通过'
            if application.applicant_user_id:
                Notification(
                    user_id=application.applicant_user_id,
                    noti_type='system',
                    title='入驻申请未通过',
                    content=f'您的“{application.name}”入驻申请未通过，原因：{application.review_remark}',
                    link_type='none',
                    tenant_id=application.tenant_id
                ).save()
            application.save()
            return success_response(application.to_dict(), '已拒绝申请')

        return error_response('action 只能为 approve 或 reject', 400)
    except Exception as e:
        from .. import db
        db.session.rollback()
        return error_response(f'审核入驻申请失败: {str(e)}', 500)


@rbac_bp.route('/roles', methods=['GET'])
@admin_required()
def get_roles():
    try:
        items = Role.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).order_by(Role.created_at.desc()).all()
        return success_response([item.to_dict() for item in items], '获取角色列表成功')
    except Exception as e:
        return error_response(f'获取角色列表失败: {str(e)}', 500)


@rbac_bp.route('/roles', methods=['POST'])
@admin_required()
def create_role():
    try:
        data = request.get_json() or {}
        if not data.get('code') or not data.get('name'):
            return error_response('code和name不能为空', 400)
        role = Role(
            code=data['code'],
            name=data['name'],
            scope=data.get('scope', 'tenant'),
            description=data.get('description'),
            tenant_id=g.tenant_id
        )
        permission_codes = data.get('permissions', [])
        if permission_codes:
            permissions = Permission.query.filter(Permission.code.in_(permission_codes), Permission.is_deleted == False).all()
            role.permissions = permissions
        role.save()
        return success_response(role.to_dict(), '创建角色成功')
    except Exception as e:
        return error_response(f'创建角色失败: {str(e)}', 500)


@rbac_bp.route('/roles/<int:role_id>', methods=['PUT'])
@admin_required()
def update_role(role_id):
    try:
        role = Role.query.filter_by(id=role_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not role:
            return error_response('角色不存在', 404)
        data = request.get_json() or {}
        for field in ['code', 'name', 'scope', 'description']:
            if field in data:
                setattr(role, field, data[field])
        if 'permissions' in data:
            permissions = Permission.query.filter(Permission.code.in_(data['permissions']), Permission.is_deleted == False).all()
            role.permissions = permissions
        role.save()
        return success_response(role.to_dict(), '更新角色成功')
    except Exception as e:
        return error_response(f'更新角色失败: {str(e)}', 500)


@rbac_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@admin_required()
def delete_role(role_id):
    try:
        role = Role.query.filter_by(id=role_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not role:
            return error_response('角色不存在', 404)
        role.soft_delete()
        return success_response(None, '删除角色成功')
    except Exception as e:
        return error_response(f'删除角色失败: {str(e)}', 500)


@rbac_bp.route('/permissions', methods=['GET'])
@admin_required()
def get_permissions():
    try:
        items = Permission.query.filter_by(is_deleted=False).order_by(Permission.module.asc(), Permission.code.asc()).all()
        return success_response([item.to_dict() for item in items], '获取权限列表成功')
    except Exception as e:
        return error_response(f'获取权限列表失败: {str(e)}', 500)


@rbac_bp.route('/permissions', methods=['POST'])
@admin_required()
def create_permission():
    try:
        data = request.get_json() or {}
        if not data.get('code') or not data.get('name') or not data.get('module') or not data.get('action'):
            return error_response('code/name/module/action不能为空', 400)
        permission = Permission(
            code=data['code'],
            name=data['name'],
            module=data['module'],
            action=data['action'],
            description=data.get('description'),
            tenant_id=g.tenant_id
        )
        permission.save()
        return success_response(permission.to_dict(), '创建权限成功')
    except Exception as e:
        return error_response(f'创建权限失败: {str(e)}', 500)


@rbac_bp.route('/permissions/<int:permission_id>', methods=['PUT'])
@admin_required()
def update_permission(permission_id):
    try:
        permission = Permission.query.filter_by(id=permission_id, is_deleted=False).first()
        if not permission:
            return error_response('权限不存在', 404)
        data = request.get_json() or {}
        for field in ['code', 'name', 'module', 'action', 'description']:
            if field in data:
                setattr(permission, field, data[field])
        permission.save()
        return success_response(permission.to_dict(), '更新权限成功')
    except Exception as e:
        return error_response(f'更新权限失败: {str(e)}', 500)


@rbac_bp.route('/permissions/<int:permission_id>', methods=['DELETE'])
@admin_required()
def delete_permission(permission_id):
    try:
        permission = Permission.query.filter_by(id=permission_id, is_deleted=False).first()
        if not permission:
            return error_response('权限不存在', 404)
        permission.soft_delete()
        return success_response(None, '删除权限成功')
    except Exception as e:
        return error_response(f'删除权限失败: {str(e)}', 500)


@rbac_bp.route('/admins', methods=['GET'])
@admin_required()
def get_admins():
    try:
        items = AdminUser.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).order_by(AdminUser.created_at.desc()).all()
        return success_response([item.to_dict() for item in items], '获取管理员列表成功')
    except Exception as e:
        return error_response(f'获取管理员列表失败: {str(e)}', 500)


@rbac_bp.route('/admins', methods=['POST'])
@admin_required()
def create_admin():
    try:
        data = request.get_json() or {}
        for field in ['username', 'phone', 'password']:
            if not data.get(field):
                return error_response(f'{field}不能为空', 400)

        admin = AdminUser(
            username=data['username'],
            phone=data['phone'],
            email=data.get('email'),
            nickname=data.get('nickname') or data['username'],
            is_active=data.get('is_active', True),
            is_super_admin=data.get('is_super_admin', False),
            tenant_id=g.tenant_id
        )
        admin.password = data['password']
        role_codes = data.get('roles', [])
        if role_codes:
            roles = Role.query.filter(Role.code.in_(role_codes), Role.tenant_id == g.tenant_id, Role.is_deleted == False).all()
            admin.roles = roles
        admin.save()
        return success_response(admin.to_dict(), '创建管理员成功')
    except Exception as e:
        return error_response(f'创建管理员失败: {str(e)}', 500)


@rbac_bp.route('/admins/<int:admin_id>', methods=['PUT'])
@admin_required()
def update_admin(admin_id):
    try:
        admin = AdminUser.query.filter_by(id=admin_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not admin:
            return error_response('管理员不存在', 404)
        data = request.get_json() or {}
        for field in ['username', 'phone', 'email', 'nickname', 'is_active', 'is_super_admin']:
            if field in data:
                setattr(admin, field, data[field])
        if data.get('password'):
            admin.password = data['password']
        if 'roles' in data:
            roles = Role.query.filter(Role.code.in_(data['roles']), Role.tenant_id == g.tenant_id, Role.is_deleted == False).all()
            admin.roles = roles
        admin.save()
        return success_response(admin.to_dict(), '更新管理员成功')
    except Exception as e:
        return error_response(f'更新管理员失败: {str(e)}', 500)


@rbac_bp.route('/admins/<int:admin_id>', methods=['DELETE'])
@admin_required()
def delete_admin(admin_id):
    try:
        admin = AdminUser.query.filter_by(id=admin_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not admin:
            return error_response('管理员不存在', 404)
        admin.soft_delete()
        return success_response(None, '删除管理员成功')
    except Exception as e:
        return error_response(f'删除管理员失败: {str(e)}', 500)

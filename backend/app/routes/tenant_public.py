"""
小程序端租户公开接口
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Tenant, TenantApplication, Notification
from ..utils.auth_helpers import get_current_user_id
from ..utils.response import success_response, error_response


tenant_public_bp = Blueprint('tenant_public', __name__)


@tenant_public_bp.route('/list', methods=['GET'])
def list_tenants():
    """小程序端租户列表，用于答辩演示租户切换"""
    try:
        tenants = Tenant.query.filter_by(status='active', is_deleted=False).order_by(Tenant.id.asc()).all()
        return success_response([tenant.to_dict() for tenant in tenants], '获取租户列表成功')
    except Exception as e:
        return error_response(f'获取租户列表失败: {str(e)}', 500)


@tenant_public_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_tenant():
    """提交运营商入驻申请"""
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        contact_name = (data.get('contact_name') or data.get('contactName') or '').strip()
        contact_phone = (data.get('contact_phone') or data.get('phone') or '').strip()
        city = (data.get('city') or '').strip()
        fund_level = (data.get('fund_level') or data.get('fundLevel') or '').strip()
        message = (data.get('message') or '').strip()

        if not name or not contact_name or not contact_phone or not city:
            return error_response('名称、联系人、电话和城市不能为空', 400)

        application = TenantApplication(
            applicant_user_id=get_current_user_id(),
            name=name,
            contact_name=contact_name,
            contact_phone=contact_phone,
            city=city,
            fund_level=fund_level,
            message=message,
            tenant_id=g.tenant_id
        )
        application.save()

        Notification(
            user_id=get_current_user_id(),
            noti_type='system',
            title='入驻申请已提交',
            content=f'您提交的“{name}”入驻申请已进入后台审核，请等待管理员处理。',
            link_type='none',
            tenant_id=g.tenant_id
        ).save()

        return success_response(application.to_dict(), '入驻申请提交成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'提交入驻申请失败: {str(e)}', 500)

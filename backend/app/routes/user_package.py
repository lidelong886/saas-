from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from ..models import UserPackage, Battery
from ..utils.auth_helpers import get_current_user_id
from ..utils.response import success_response, error_response, paginate_response
from .. import db

user_package_bp = Blueprint('user_package', __name__)

@user_package_bp.route('/list', methods=['GET'])
@jwt_required()
def get_user_packages():
    """获取我的卡券/套餐列表"""
    try:
        user_id = get_current_user_id()
        status = request.args.get('status', 'unused')  # unused / active / expired
        
        query = UserPackage.query.filter_by(user_id=user_id, tenant_id=g.tenant_id, is_deleted=False)
        if status:
            query = query.filter_by(status=status)
            
        items = query.order_by(UserPackage.created_at.desc()).all()
        return success_response([item.to_dict() for item in items], '获取卡券成功')
    except Exception as e:
        return error_response(f'获取失败: {str(e)}', 500)

@user_package_bp.route('/<int:up_id>/activate', methods=['POST'])
@jwt_required()
def activate_package(up_id):
    """激活卡券（例如激活租用月卡）"""
    try:
        user_id = get_current_user_id()
        up = UserPackage.query.filter_by(id=up_id, user_id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
        
        if not up:
            return error_response('卡券不存在', 404)
            
        success, msg = up.activate()
        if not success:
            return error_response(msg, 400)
            
        return success_response(up.to_dict(), '激活成功')
    except Exception as e:
        return error_response(f'激活失败: {str(e)}', 500)

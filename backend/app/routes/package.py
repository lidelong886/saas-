"""
套餐路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from ..models import Package
from ..utils.response import success_response, error_response, paginate_response


package_bp = Blueprint('package', __name__)


@package_bp.route('/list', methods=['GET'])
def get_packages():
    """获取套餐列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        package_type = request.args.get('package_type')
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        query = Package.query.filter_by(tenant_id=g.tenant_id, is_deleted=False)
        if package_type:
            query = query.filter_by(package_type=package_type)
        if active_only:
            query = query.filter_by(is_active=True)

        pagination = query.order_by(Package.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return paginate_response(
            [item.to_dict() for item in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取套餐列表成功'
        )
    except Exception as e:
        return error_response(f'获取套餐列表失败: {str(e)}', 500)


@package_bp.route('/<int:package_id>', methods=['GET'])
def get_package_detail(package_id):
    """获取套餐详情"""
    try:
        package = Package.query.filter_by(id=package_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not package:
            return error_response('套餐不存在', 404)
        return success_response(package.to_dict(), '获取套餐详情成功')
    except Exception as e:
        return error_response(f'获取套餐详情失败: {str(e)}', 500)


@package_bp.route('/admin/list', methods=['GET'])
@jwt_required()
def get_admin_packages():
    """后台获取全部套餐"""
    return get_packages()


@package_bp.route('/admin', methods=['POST'])
@jwt_required()
def create_package():
    """创建套餐"""
    try:
        data = request.get_json() or {}
        if not data.get('name'):
            return error_response('name不能为空', 400)

        package = Package(
            name=data['name'],
            package_type=data.get('package_type', 'rental'),
            battery_model=data.get('battery_model'),
            hours=data.get('hours', 24),
            price=data.get('price', 0),
            deposit_amount=data.get('deposit_amount', 0),
            exchange_fee=data.get('exchange_fee', 0),
            is_active=data.get('is_active', True),
            description=data.get('description'),
            tenant_id=g.tenant_id
        )
        package.save()
        return success_response(package.to_dict(), '创建套餐成功')
    except Exception as e:
        return error_response(f'创建套餐失败: {str(e)}', 500)


@package_bp.route('/admin/<int:package_id>', methods=['PUT'])
@jwt_required()
def update_package(package_id):
    """更新套餐"""
    try:
        package = Package.query.filter_by(id=package_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not package:
            return error_response('套餐不存在', 404)

        data = request.get_json() or {}
        for field in ['name', 'package_type', 'battery_model', 'hours', 'price', 'deposit_amount', 'exchange_fee', 'is_active', 'description']:
            if field in data:
                setattr(package, field, data[field])
        package.save()
        return success_response(package.to_dict(), '更新套餐成功')
    except Exception as e:
        return error_response(f'更新套餐失败: {str(e)}', 500)

@package_bp.route('/admin/<int:package_id>', methods=['DELETE'])
@jwt_required()
def delete_package(package_id):
    """删除套餐（软删除）"""
    try:
        package = Package.query.filter_by(id=package_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not package:
            return error_response('套餐不存在', 404)

        package.soft_delete()
        return success_response(None, '删除套餐成功')
    except Exception as e:
        return error_response(f'删除套餐失败: {str(e)}', 500)

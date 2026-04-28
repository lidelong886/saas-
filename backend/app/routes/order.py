"""
订单管理路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id
from ..models import Order, Payment
from ..services.order_service import OrderService
from ..utils.response import success_response, error_response, paginate_response
from ..utils.validators import validate_order_no
from .. import limiter

order_bp = Blueprint('order', __name__)

@order_bp.route('/create', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")  # 订单创建限制：每分钟20次
def create_order():
    """创建订单"""
    try:
        data = request.get_json()
        order_type = data.get('order_type')
        battery_id = data.get('battery_id')
        hours = data.get('hours', 24)
        package_id = data.get('package_id')
        station_id = data.get('station_id')
        cabinet_id = data.get('cabinet_id')

        if order_type not in ['rental', 'purchase', 'exchange']:
            return error_response('订单类型不正确', 400)

        user_id = get_current_user_id()
        success, result = OrderService.create_order(
            user_id,
            order_type,
            battery_id,
            hours,
            package_id=package_id,
            station_id=station_id,
            cabinet_id=cabinet_id
        )
        if not success:
            return error_response(result, 400)
        return success_response(result, '订单创建成功')
    except Exception as e:
        return error_response(f'创建订单失败: {str(e)}', 500)

@order_bp.route('/<order_no>', methods=['GET'])
@jwt_required()
def get_order(order_no):
    """获取订单详情"""
    try:
        if not validate_order_no(order_no):
            return error_response('订单号格式不正确', 400)

        order = Order.query.filter_by(order_no=order_no, tenant_id=g.tenant_id, is_deleted=False).first()
        if not order:
            return error_response('订单不存在', 404)
        user_id = get_current_user_id()
        if order.user_id != user_id:
            return error_response('无权查看此订单', 403)
        return success_response(order.to_dict(), '订单详情获取成功')
    except Exception as e:
        return error_response(f'获取订单详情失败: {str(e)}', 500)

@order_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """获取我的订单列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        order_type = request.args.get('order_type')
        user_id = get_current_user_id()

        query = Order.query.filter_by(user_id=user_id, tenant_id=g.tenant_id, is_deleted=False)
        if status:
            query = query.filter_by(status=status)
        if order_type:
            query = query.filter_by(order_type=order_type)
        query = query.order_by(Order.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginate_response(
            [order.to_dict() for order in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取订单列表成功'
        )
    except Exception as e:
        return error_response(f'获取订单列表失败: {str(e)}', 500)

@order_bp.route('/<order_no>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_no):
    """取消订单"""
    try:
        if not validate_order_no(order_no):
            return error_response('订单号格式不正确', 400)

        order = Order.query.filter_by(order_no=order_no, tenant_id=g.tenant_id, is_deleted=False).first()
        if not order:
            return error_response('订单不存在', 404)

        user_id = get_current_user_id()
        if order.user_id != user_id:
            return error_response('无权操作此订单', 403)

        data = request.get_json(silent=True) or {}
        reason = data.get('reason', '用户取消订单')

        success, result = order.transition_status('cancelled', reason=reason)
        if not success:
            return error_response(result, 400)

        return success_response(order.to_dict(), result)
    except Exception as e:
        return error_response(f'取消订单失败: {str(e)}', 500)

@order_bp.route('/<order_no>/refund', methods=['POST'])
@jwt_required()
def refund_order(order_no):
    """申请退款"""
    try:
        if not validate_order_no(order_no):
            return error_response('订单号格式不正确', 400)

        user_id = get_current_user_id()
        success, result = OrderService.request_refund(user_id, order_no)

        if not success:
            return error_response(result, 400)
        return success_response(None, result)
    except Exception as e:
        return error_response(f'申请退款失败: {str(e)}', 500)

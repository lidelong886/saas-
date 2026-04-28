"""
支付管理路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required, get_jwt
from ..utils.auth_helpers import get_current_user_id
from ..models import Order, Payment
from ..services.payment_service import PaymentService
from ..utils.response import success_response, error_response, paginate_response
from ..utils.validators import validate_order_no, validate_positive_number

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_payment_order():
    """
    创建支付订单
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['order_no', 'payment_method']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段: {field}', 400)

        order_no = data['order_no']
        payment_method = data['payment_method']

        if not validate_order_no(order_no):
            return error_response('订单号格式不正确', 400)

        if payment_method not in ['wechat', 'alipay', 'balance']:
            return error_response('不支持的支付方式', 400)

        # 获取订单
        order = Order.query.filter_by(
            order_no=order_no,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not order:
            return error_response('订单不存在', 404)

        user_id = get_current_user_id()
        if order.user_id != user_id:
            return error_response('无权操作此订单', 403)

        if order.status != 'pending':
            return error_response('订单状态不允许支付', 400)

        success, result = PaymentService.create_payment_order(order.id, payment_method)
        if not success:
            return error_response(result, 400)

        return success_response(result, '支付订单创建成功')

    except Exception as e:
        return error_response(f'创建支付订单失败: {str(e)}', 500)

@payment_bp.route('/pay/<order_no>', methods=['POST'])
@jwt_required()
def pay_order(order_no):
    """
    支付订单（小程序端）
    """
    try:
        if not validate_order_no(order_no):
            return error_response('订单号格式不正确', 400)

        data = request.get_json()
        payment_method = data.get('payment_method', 'wechat')

        if payment_method not in ['wechat', 'alipay', 'balance']:
            return error_response('不支持的支付方式', 400)

        # 获取订单
        order = Order.query.filter_by(
            order_no=order_no,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not order:
            return error_response('订单不存在', 404)

        user_id = get_current_user_id()
        if order.user_id != user_id:
            return error_response('无权操作此订单', 403)

        success, result = PaymentService.pay_order(order.id, payment_method)
        if not success:
            return error_response(result, 400)

        return success_response(result, '支付发起成功')

    except Exception as e:
        return error_response(f'支付失败: {str(e)}', 500)

@payment_bp.route('/notify', methods=['POST'])
def payment_notify():
    """
    支付结果通知（微信支付回调）
    """
    try:
        # 获取请求头和body
        headers = dict(request.headers)
        body = request.get_data(as_text=True)

        success, result = PaymentService.handle_payment_notify(headers, body)
        if success:
            return result, 200
        else:
            return 'fail', 400

    except Exception as e:
        print(f'支付通知处理失败: {str(e)}')
        return 'fail', 500

@payment_bp.route('/refund', methods=['POST'])
@jwt_required()
def refund_payment():
    """
    申请退款
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['order_no', 'refund_amount', 'reason']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段: {field}', 400)

        order_no = data['order_no']
        refund_amount = data['refund_amount']
        reason = data['reason']

        if not validate_order_no(order_no):
            return error_response('订单号格式不正确', 400)

        if not validate_positive_number(refund_amount):
            return error_response('退款金额必须大于0', 400)

        # 获取订单
        order = Order.query.filter_by(
            order_no=order_no,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not order:
            return error_response('订单不存在', 404)

        # 检查权限（只能退自己的订单或管理员）
        uid = get_current_user_id()
        if order.user_id != uid:
            # 检查是否为管理员
            claims = get_jwt()
            if not claims.get('is_admin'):
                return error_response('无权操作此订单', 403)

        success, result = PaymentService.refund_order(order.id, refund_amount, reason)
        if not success:
            return error_response(result, 400)

        return success_response(result, '退款申请提交成功')

    except Exception as e:
        return error_response(f'退款申请失败: {str(e)}', 500)

@payment_bp.route('/query/<order_no>', methods=['GET'])
@jwt_required()
def query_payment(order_no):
    """
    查询支付状态
    """
    try:
        if not validate_order_no(order_no):
            return error_response('订单号格式不正确', 400)

        # 获取订单
        order = Order.query.filter_by(
            order_no=order_no,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not order:
            return error_response('订单不存在', 404)

        if order.user_id != get_current_user_id():
            return error_response('无权查看此订单', 403)

        success, result = PaymentService.query_payment_status(order.id)
        if not success:
            return error_response(result, 400)

        return success_response(result, '支付状态查询成功')

    except Exception as e:
        return error_response(f'查询支付状态失败: {str(e)}', 500)

@payment_bp.route('/records', methods=['GET'])
@jwt_required()
def get_payment_records():
    """
    获取支付记录列表
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        payment_type = request.args.get('type')
        status = request.args.get('status')

        user_id = get_current_user_id()
        pagination = Payment.get_user_payments(
            user_id, page, per_page, payment_type
        )

        return paginate_response(
            [payment.to_dict() for payment in pagination.items],
            {
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            '获取支付记录成功'
        )

    except Exception as e:
        return error_response(f'获取支付记录失败: {str(e)}', 500)


@payment_bp.route('/recharge', methods=['POST'])
@jwt_required()
def create_recharge():
    """创建充值单"""
    try:
        data = request.get_json() or {}
        amount = data.get('amount')
        payment_method = data.get('payment_method', 'wechat')
        if not validate_positive_number(amount):
            return error_response('充值金额必须大于0', 400)

        success, result = PaymentService.create_recharge_order(
            get_current_user_id(),
            amount,
            payment_method
        )
        if not success:
            return error_response(result, 400)
        return success_response(result, '充值订单创建成功')
    except Exception as e:
        return error_response(f'创建充值订单失败: {str(e)}', 500)


@payment_bp.route('/recharge/<payment_no>/complete', methods=['POST'])
@jwt_required()
def complete_recharge(payment_no):
    """毕设演示模式完成充值"""
    try:
        success, result = PaymentService.complete_recharge(payment_no)
        if not success:
            return error_response(result, 400)
        return success_response(result, '充值成功')
    except Exception as e:
        return error_response(f'充值失败: {str(e)}', 500)

"""
电池商城路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id

from ..models import Battery, User, Order
from ..utils.response import success_response, error_response, paginate_response
from .. import db

store_bp = Blueprint('store', __name__)

@store_bp.route('/list', methods=['GET'])
def get_store_batteries():
    """获取可售卖电池列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 查找可售卖电池：目前设定为没有 owner 且有 deposit_amount 的电池
        query = Battery.query.filter(
            Battery.tenant_id == g.tenant_id,
            Battery.is_deleted == False,
            Battery.owner_id == None,
            Battery.status == 'available'
        )

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return paginate_response(
            [item.to_dict() for item in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取商城列表成功'
        )
    except Exception as e:
        return error_response(f'获取列表失败: {str(e)}', 500)

@store_bp.route('/purchase/<int:battery_id>', methods=['POST'])
@jwt_required()
def purchase_battery(battery_id):
    """购买电池"""
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        # 获取电池
        battery = Battery.query.filter_by(
            id=battery_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not battery:
            return error_response('电池不存在', 404)

        if battery.owner_id is not None:
            return error_response('该电池已被购买', 400)

        if battery.status != 'available':
            return error_response('该电池不可购买', 400)

        # 计算价格
        from decimal import Decimal
        price = Decimal(str(battery.selling_price)) if battery.selling_price else Decimal(str(battery.deposit_amount))

        # 检查余额
        if user.balance < price:
            return error_response('余额不足', 400)

        # 扣除余额
        user.deduct_balance(price, f'购买电池 {battery.battery_code}')

        # 转移所有权
        battery.owner_id = user_id
        battery.status = 'available'
        battery.save()

        # 创建购买订单记录
        from datetime import datetime
        order = Order(
            order_no=f'PUR{datetime.now().strftime("%Y%m%d%H%M%S")}{user_id:04d}',
            user_id=user_id,
            order_type='purchase',
            battery_id=battery.id,
            total_amount=price,
            status='completed',
            tenant_id=g.tenant_id
        )
        db.session.add(order)
        db.session.commit()

        return success_response({
            'battery': battery.to_dict(),
            'order_no': order.order_no,
            'balance': float(user.balance)
        }, '购买成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'购买失败: {str(e)}', 500)

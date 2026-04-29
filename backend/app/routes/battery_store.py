"""
电池商城路由
"""
from flask import Blueprint, request, g
from sqlalchemy import asc, desc, case
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id

from ..models import Battery, User, Order
from ..utils.response import success_response, error_response, paginate_response
from .. import db

store_bp = Blueprint('store', __name__)

@store_bp.route('/list', methods=['GET'])
def get_store_batteries():
    """Get batteries available for sale."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort = request.args.get('sort', 'recommend')
        voltage_type = request.args.get('voltage_type')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)

        price_expr = case(
            (Battery.selling_price > 0, Battery.selling_price),
            else_=Battery.deposit_amount
        )

        query = Battery.query.filter(
            Battery.tenant_id == g.tenant_id,
            Battery.is_deleted == False,
            Battery.owner_id == None,
            Battery.status == 'available'
        )

        if voltage_type:
            query = query.filter(Battery.voltage_type == voltage_type)
        if price_min is not None:
            query = query.filter(price_expr >= price_min)
        if price_max is not None:
            query = query.filter(price_expr < price_max)

        if sort == 'priceAsc':
            query = query.order_by(asc(price_expr), desc(Battery.power_level), desc(Battery.created_at))
        elif sort == 'priceDesc':
            query = query.order_by(desc(price_expr), desc(Battery.power_level), desc(Battery.created_at))
        elif sort == 'powerDesc':
            query = query.order_by(desc(Battery.power_level), asc(price_expr), desc(Battery.created_at))
        else:
            query = query.order_by(desc(Battery.power_level), desc(Battery.created_at))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for item in pagination.items:
            data = item.to_dict()
            data['current_station_name'] = item.current_station.name if item.current_station else ''
            items.append(data)

        return paginate_response(
            items,
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            'Get store list successfully'
        )
    except Exception as e:
        return error_response(f'Get store list failed: {str(e)}', 500)


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

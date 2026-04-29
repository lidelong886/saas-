"""
电池商城路由
"""
from flask import Blueprint, request, g
from sqlalchemy import asc, desc, case, func
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id

from ..models import Battery, User, Order
from ..utils.response import success_response, error_response, paginate_response
from .. import db

store_bp = Blueprint('store', __name__)


def _price_expr():
    return case(
        (Battery.selling_price > 0, Battery.selling_price),
        else_=Battery.deposit_amount
    )


def _capacity_label(capacity):
    capacity = int(capacity or 0)
    if capacity >= 1000:
        return f'{round(capacity / 1000)}Ah'
    return f'{capacity}mAh'


def _category_id(voltage_type, capacity):
    return f'{voltage_type or "60V"}-{int(capacity or 0)}'


def _category_name(voltage_type, capacity):
    return f'{voltage_type or "60V"} {_capacity_label(capacity)} 智能锂电池'

@store_bp.route('/list', methods=['GET'])
def get_store_batteries():
    """按规格品类获取商城商品，不直接暴露单块库存电池。"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort = request.args.get('sort', 'recommend')
        voltage_type = request.args.get('voltage_type')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)

        price_expr = _price_expr()
        base_filters = [
            Battery.tenant_id == g.tenant_id,
            Battery.is_deleted == False,
            Battery.owner_id == None,
            Battery.status == 'available'
        ]

        if voltage_type:
            base_filters.append(Battery.voltage_type == voltage_type)
        if price_min is not None:
            base_filters.append(price_expr >= price_min)
        if price_max is not None:
            base_filters.append(price_expr < price_max)

        query = db.session.query(
            Battery.voltage_type.label('voltage_type'),
            Battery.capacity.label('capacity'),
            func.count(Battery.id).label('stock'),
            func.min(price_expr).label('selling_price'),
            func.min(Battery.deposit_amount).label('deposit_amount'),
            func.max(Battery.power_level).label('power_level'),
            func.avg(Battery.power_level).label('avg_power_level'),
            func.max(Battery.warranty_period).label('warranty_period')
        ).filter(*base_filters).group_by(Battery.voltage_type, Battery.capacity)

        if sort == 'priceAsc':
            query = query.order_by(asc('selling_price'), desc('power_level'))
        elif sort == 'priceDesc':
            query = query.order_by(desc('selling_price'), desc('power_level'))
        elif sort == 'powerDesc':
            query = query.order_by(desc('power_level'), asc('selling_price'))
        else:
            query = query.order_by(desc('stock'), desc('power_level'), asc('selling_price'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for item in pagination.items:
            items.append({
                'id': _category_id(item.voltage_type, item.capacity),
                'category_id': _category_id(item.voltage_type, item.capacity),
                'model': _category_name(item.voltage_type, item.capacity),
                'voltage_type': item.voltage_type or '60V',
                'capacity': int(item.capacity or 0),
                'capacity_label': _capacity_label(item.capacity),
                'selling_price': float(item.selling_price or 0),
                'deposit_amount': float(item.deposit_amount or 0),
                'power_level': int(item.power_level or 0),
                'avg_power_level': round(float(item.avg_power_level or 0), 1),
                'stock': int(item.stock or 0),
                'warranty_period': int(item.warranty_period or 24),
                'sale_mode': 'category'
            })

        return paginate_response(
            items,
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            'Get store list successfully'
        )
    except Exception as e:
        return error_response(f'Get store list failed: {str(e)}', 500)


def _purchase_available_battery(user, battery, price):
    from datetime import datetime

    user.balance = user.balance - price
    battery.owner_id = user.id
    battery.current_user_id = user.id
    battery.status = 'owned'
    db.session.add(battery)

    order = Order(
        order_no=f'PUR{datetime.now().strftime("%Y%m%d%H%M%S")}{user.id:04d}',
        user_id=user.id,
        order_type='purchase',
        battery_id=battery.id,
        total_amount=price,
        status='completed',
        tenant_id=g.tenant_id,
        pricing_snapshot={
            'sale_mode': 'category',
            'voltage_type': battery.voltage_type,
            'capacity': battery.capacity,
            'price': float(price)
        }
    )
    db.session.add(order)
    db.session.commit()
    return order


@store_bp.route('/purchase-category', methods=['POST'])
@jwt_required()
def purchase_battery_category():
    """按规格购买电池，后端自动从库存里分配一块真实电池。"""
    try:
        data = request.get_json() or {}
        voltage_type = data.get('voltage_type')
        try:
            capacity = int(data.get('capacity') or 0)
        except (TypeError, ValueError):
            capacity = 0

        if not voltage_type or capacity <= 0:
            return error_response('请选择要购买的电池规格', 400)

        user = User.get_by_id(get_current_user_id())
        if not user:
            return error_response('用户不存在', 404)

        price_expr = _price_expr()
        battery = Battery.query.filter(
            Battery.tenant_id == g.tenant_id,
            Battery.is_deleted == False,
            Battery.owner_id == None,
            Battery.status == 'available',
            Battery.voltage_type == voltage_type,
            Battery.capacity == capacity
        ).order_by(desc(Battery.power_level), asc(price_expr), asc(Battery.id)).first()

        if not battery:
            return error_response('该规格暂时售罄', 400)

        from decimal import Decimal
        price = Decimal(str(battery.selling_price)) if battery.selling_price else Decimal(str(battery.deposit_amount))
        if user.balance < price:
            return error_response('余额不足', 400)

        order = _purchase_available_battery(user, battery, price)

        return success_response({
            'battery': battery.to_dict(),
            'order_no': order.order_no,
            'balance': float(user.balance)
        }, '购买成功，已为您分配专属电池')

    except Exception as e:
        db.session.rollback()
        return error_response(f'购买失败: {str(e)}', 500)


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

        order = _purchase_available_battery(user, battery, price)

        return success_response({
            'battery': battery.to_dict(),
            'order_no': order.order_no,
            'balance': float(user.balance)
        }, '购买成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'购买失败: {str(e)}', 500)

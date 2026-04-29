"""
管理后台路由 - 完整CRUD + 数据统计 + 租户管理 + 换电 + 系统设置
"""
from flask import Blueprint, request, g, current_app
from flask_jwt_extended import jwt_required
from ..utils.admin_auth import admin_required
from ..models import User, Station, Battery, Order, Payment, Cabinet, Tenant, OperationLog, SystemConfig
from .. import db
from ..utils.response import success_response, error_response, paginate_response
from ..utils.operation_log import log_admin_action
from ..utils.amap import AMapService
from ..services.payment_service import PaymentService
from ..services.tenant_config_service import TenantConfigService
from datetime import datetime, timedelta
from sqlalchemy import func, case, extract
import random

admin_bp = Blueprint('admin', __name__)


def is_system_admin():
    return getattr(g, 'tenant_id', 1) == 1


def resolve_manage_tenant_id(data=None):
    if not is_system_admin():
        return g.tenant_id

    tenant_id = (data or {}).get('tenant_id') or request.args.get('tenant_id', type=int) or g.tenant_id
    tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first()
    return tenant.id if tenant else g.tenant_id


def scoped_admin_query(model):
    query = model.query.filter_by(is_deleted=False)
    if is_system_admin():
        tenant_id = request.args.get('tenant_id', type=int)
        if tenant_id:
            query = query.filter(model.tenant_id == tenant_id)
    else:
        query = query.filter(model.tenant_id == g.tenant_id)
    return query


def get_admin_record(model, record_id):
    query = model.query.filter_by(id=record_id, is_deleted=False)
    if not is_system_admin():
        query = query.filter(model.tenant_id == g.tenant_id)
    return query.first()


def attach_tenant_name(item):
    tenant = Tenant.query.filter_by(id=item.get('tenant_id'), is_deleted=False).first()
    item['tenant_name'] = tenant.name if tenant else ''
    return item

SYSTEM_SETTINGS = {
    'wechatAppId': '',
    'wechatMchId': '',
    'amapKey': ''
}

# ==================== 仪表板 ====================

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required()
def get_dashboard_stats():
    """获取仪表板统计数据"""
    try:
        today = datetime.now().date()
        this_month = today.replace(day=1)

        total_users = User.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).count()
        today_users = User.query.filter(
            User.tenant_id == g.tenant_id,
            func.date(User.created_at) == today,
            User.is_deleted == False
        ).count()

        total_stations = Station.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).count()
        active_stations = Station.query.filter(
            Station.tenant_id == g.tenant_id,
            Station.status == 'active',
            Station.is_deleted == False
        ).count()

        total_batteries = Battery.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).count()
        available_batteries = Battery.query.filter(
            Battery.tenant_id == g.tenant_id,
            Battery.status == 'available',
            Battery.is_deleted == False
        ).count()
        rented_batteries = Battery.query.filter(
            Battery.tenant_id == g.tenant_id,
            Battery.status.in_(['rented', 'in_use', 'charging']),
            Battery.is_deleted == False
        ).count()

        total_orders = Order.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).count()
        today_orders = Order.query.filter(
            Order.tenant_id == g.tenant_id,
            func.date(Order.created_at) == today,
            Order.is_deleted == False
        ).count()

        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.tenant_id == g.tenant_id,
            Order.status == 'completed',
            func.date(Order.created_at) == today,
            Order.is_deleted == False
        ).scalar() or 0

        month_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.tenant_id == g.tenant_id,
            Order.status == 'completed',
            Order.created_at >= this_month,
            Order.is_deleted == False
        ).scalar() or 0

        stats = {
            'users': {'total': total_users, 'today_new': today_users},
            'stations': {'total': total_stations, 'active': active_stations},
            'batteries': {'total': total_batteries, 'available': available_batteries, 'rented': rented_batteries},
            'orders': {'total': total_orders, 'today': today_orders},
            'revenue': {'today': float(today_revenue), 'month': float(month_revenue)}
        }

        return success_response(stats, '获取统计数据成功')
    except Exception as e:
        return error_response(f'获取统计数据失败: {str(e)}', 500)

# ==================== 用户管理 ====================

@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_users():
    """获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '')

        query = User.query.filter_by(tenant_id=g.tenant_id, is_deleted=False)
        if keyword:
            query = query.filter(
                (User.username.like(f'%{keyword}%')) |
                (User.phone.like(f'%{keyword}%')) |
                (User.email.like(f'%{keyword}%'))
            )
        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginate_response(
            [user.to_dict(include_private=True) for user in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取用户列表成功'
        )
    except Exception as e:
        return error_response(f'获取用户列表失败: {str(e)}', 500)

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user_detail(user_id):
    """获取用户详情"""
    try:
        user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not user:
            return error_response('用户不存在', 404)
        return success_response(user.to_dict(include_private=True), '获取用户详情成功')
    except Exception as e:
        return error_response(f'获取用户详情失败: {str(e)}', 500)

@admin_bp.route('/users', methods=['POST'])
@admin_required()
def create_user():
    """创建用户"""
    try:
        data = request.get_json()
        required_fields = ['username', 'phone', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field}不能为空', 400)
        
        if User.query.filter_by(username=data['username'], tenant_id=g.tenant_id, is_deleted=False).first():
            return error_response('用户名已存在', 400)
        if User.query.filter_by(phone=data['phone'], tenant_id=g.tenant_id, is_deleted=False).first():
            return error_response('手机号已存在', 400)

        user = User(
            username=data['username'],
            phone=data['phone'],
            email=data['email'],
            nickname=data.get('nickname', data['username']),
            is_rider=data.get('is_rider', False),
            tenant_id=g.tenant_id
        )
        user.password = data['password']
        db.session.add(user)
        db.session.commit()
        return success_response(user.to_dict(include_private=True), '创建用户成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建用户失败: {str(e)}', 500)

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    """更新用户"""
    try:
        user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not user:
            return error_response('用户不存在', 404)
        data = request.get_json()
        for field in ['nickname', 'email', 'is_rider', 'is_active', 'balance', 'points']:
            if field in data:
                setattr(user, field, data[field])
        if 'password' in data and data['password']:
            user.password = data['password']
        user.updated_at = datetime.now()
        db.session.commit()
        return success_response(user.to_dict(include_private=True), '更新用户成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新用户失败: {str(e)}', 500)

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not user:
            return error_response('用户不存在', 404)
        user.is_deleted = True
        user.updated_at = datetime.now()
        db.session.commit()
        return success_response(None, '删除用户成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除用户失败: {str(e)}', 500)

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required()
def toggle_user_status(user_id):
    """切换用户状态"""
    try:
        user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not user:
            return error_response('用户不存在', 404)
        data = request.get_json()
        user.is_active = data.get('is_active', not user.is_active)
        user.updated_at = datetime.now()
        db.session.commit()
        return success_response(user.to_dict(include_private=True), '更新用户状态成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新用户状态失败: {str(e)}', 500)

# ==================== 站点管理 ====================

@admin_bp.route('/stations', methods=['GET'])
@admin_required()
def get_stations():
    """获取站点列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')
        query = scoped_admin_query(Station)
        if keyword:
            query = query.filter(
                (Station.name.like(f'%{keyword}%')) |
                (Station.station_code.like(f'%{keyword}%')) |
                (Station.address.like(f'%{keyword}%'))
            )
        if status:
            query = query.filter(Station.status == status)
        query = query.order_by(Station.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginate_response(
            [attach_tenant_name(station.to_dict()) for station in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取站点列表成功'
        )
    except Exception as e:
        return error_response(f'获取站点列表失败: {str(e)}', 500)

@admin_bp.route('/stations/<int:station_id>', methods=['GET'])
@admin_required()
def get_station_detail(station_id):
    """获取站点详情"""
    try:
        station = get_admin_record(Station, station_id)
        if not station:
            return error_response('站点不存在', 404)
        return success_response(attach_tenant_name(station.to_dict()), '获取站点详情成功')
    except Exception as e:
        return error_response(f'获取站点详情失败: {str(e)}', 500)

@admin_bp.route('/stations', methods=['POST'])
@admin_required()
def create_station():
    """创建站点"""
    try:
        data = request.get_json()
        required_fields = ['name', 'address', 'latitude', 'longitude']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field}不能为空', 400)

        tenant_id = resolve_manage_tenant_id(data)
        station_code = f"STN{tenant_id:03d}{random.randint(1000, 9999)}"
        station = Station(
            station_code=station_code,
            name=data['name'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            phone=data.get('phone', ''),
            business_hours=data.get('business_hours', ''),
            city=data.get('city', ''),
            district=data.get('district', ''),
            is_24_hour=data.get('is_24_hour', False),
            total_cabinets=data.get('total_cabinets', 0),
            total_slots=data.get('total_slots', 0),
            total_batteries=data.get('total_batteries', 0),
            available_batteries=data.get('available_batteries', 0),
            tenant_id=tenant_id
        )
        station.tenant_id = tenant_id
        # 设置枚举字段 - 使用字符串值
        station.type = data.get('type', 'street')
        station.status = data.get('status', 'active')
        
        db.session.add(station)
        log_admin_action('创建站点', station.name, '站点管理', extra={'station_code': station_code})
        db.session.commit()
        return success_response(attach_tenant_name(station.to_dict()), '创建站点成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建站点失败: {str(e)}', 500)

@admin_bp.route('/stations/<int:station_id>', methods=['PUT'])
@admin_required()
def update_station(station_id):
    """更新站点"""
    try:
        station = get_admin_record(Station, station_id)
        if not station:
            return error_response('站点不存在', 404)
        data = request.get_json()
        for field in ['name', 'address', 'latitude', 'longitude', 'phone', 'business_hours', 'city', 'district', 'is_24_hour', 'total_cabinets', 'total_slots', 'total_batteries', 'available_batteries']:
            if field in data:
                setattr(station, field, data[field])
        if 'type' in data:
            station.type = data['type']
        if 'status' in data:
            station.status = data['status']
        if is_system_admin() and 'tenant_id' in data:
            station.tenant_id = resolve_manage_tenant_id(data)
        station.updated_at = datetime.now()
        log_admin_action('更新站点', station.name, '站点管理', extra={'station_id': station.id})
        db.session.commit()
        return success_response(attach_tenant_name(station.to_dict()), '更新站点成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新站点失败: {str(e)}', 500)

@admin_bp.route('/stations/<int:station_id>', methods=['DELETE'])
@admin_required()
def delete_station(station_id):
    """删除站点"""
    try:
        station = get_admin_record(Station, station_id)
        if not station:
            return error_response('站点不存在', 404)
        station_name = station.name
        station.is_deleted = True
        station.updated_at = datetime.now()
        log_admin_action('删除站点', station_name, '站点管理', status='warning', extra={'station_id': station.id})
        db.session.commit()
        return success_response(None, '删除站点成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除站点失败: {str(e)}', 500)

# ==================== 电池管理 ====================

@admin_bp.route('/batteries', methods=['GET'])
@admin_required()
def get_batteries():
    """获取电池列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')
        voltage_type = request.args.get('voltage_type', '')
        station_id = request.args.get('station_id', type=int)

        query = scoped_admin_query(Battery)
        if keyword:
            query = query.filter(
                (Battery.battery_code.like(f'%{keyword}%')) |
                (Battery.model.like(f'%{keyword}%'))
            )
        if status:
            query = query.filter(Battery.status == status)
        if voltage_type:
            query = query.filter(Battery.voltage_type == voltage_type)
        if station_id:
            query = query.filter(Battery.current_station_id == station_id)
        query = query.order_by(Battery.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        batteries_data = []
        for battery in pagination.items:
            battery_dict = battery.to_dict()
            if battery.current_station_id:
                station = Station.query.filter_by(id=battery.current_station_id, tenant_id=battery.tenant_id, is_deleted=False).first()
                battery_dict['current_station_name'] = station.name if station else ''
            else:
                battery_dict['current_station_name'] = ''
            attach_tenant_name(battery_dict)
            batteries_data.append(battery_dict)

        return paginate_response(
            batteries_data,
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取电池列表成功'
        )
    except Exception as e:
        return error_response(f'获取电池列表失败: {str(e)}', 500)

@admin_bp.route('/batteries/<int:battery_id>', methods=['GET'])
@admin_required()
def get_battery_detail(battery_id):
    """获取电池详情"""
    try:
        battery = get_admin_record(Battery, battery_id)
        if not battery:
            return error_response('电池不存在', 404)
        battery_dict = battery.to_dict()
        if battery.current_station_id:
            station = Station.query.filter_by(id=battery.current_station_id, tenant_id=battery.tenant_id, is_deleted=False).first()
            battery_dict['current_station_name'] = station.name if station else ''
        return success_response(attach_tenant_name(battery_dict), '获取电池详情成功')
    except Exception as e:
        return error_response(f'获取电池详情失败: {str(e)}', 500)

@admin_bp.route('/batteries', methods=['POST'])
@admin_required()
def create_battery():
    """创建电池"""
    try:
        data = request.get_json()
        required_fields = ['model', 'capacity']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field}不能为空', 400)

        tenant_id = resolve_manage_tenant_id(data)
        station_id = data.get('current_station_id')
        if station_id:
            station = Station.query.filter_by(id=station_id, tenant_id=tenant_id, is_deleted=False).first()
            if not station:
                return error_response('所属站点不属于选择的运营商', 400)
        battery_code = data.get('battery_code') or f"BAT{tenant_id:03d}{random.randint(100000, 999999)}"
        battery = Battery(
            battery_code=battery_code,
            model=data['model'],
            capacity=data['capacity'],
            power_level=data.get('power_level', 100),
            voltage_type=data.get('voltage_type', '60V'),
            voltage=data.get('voltage'),
            temperature=data.get('temperature'),
            current_station_id=station_id,
            rental_price_per_hour=data.get(
                'rental_price_per_hour',
                TenantConfigService.get_value(tenant_id, 'rental_price_per_hour')
            ),
            deposit_amount=data.get(
                'deposit_amount',
                TenantConfigService.get_value(tenant_id, 'deposit_amount')
            ),
            selling_price=data.get('selling_price'),
            tenant_id=tenant_id
        )
        battery.tenant_id = tenant_id
        # 设置枚举字段 - 使用字符串值
        battery.battery_type = data.get('battery_type', 'lithium_ion')
        battery.status = data.get('status', 'available')
        
        db.session.add(battery)
        log_admin_action('新增电池', battery_code, '电池管理', extra={'model': battery.model})
        db.session.commit()
        return success_response(attach_tenant_name(battery.to_dict()), '创建电池成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建电池失败: {str(e)}', 500)

@admin_bp.route('/batteries/<int:battery_id>', methods=['PUT'])
@admin_required()
def update_battery(battery_id):
    """更新电池"""
    try:
        battery = get_admin_record(Battery, battery_id)
        if not battery:
            return error_response('电池不存在', 404)
        data = request.get_json()
        target_tenant_id = resolve_manage_tenant_id(data) if is_system_admin() and 'tenant_id' in data else battery.tenant_id
        station_changed = 'current_station_id' in data and data.get('current_station_id') != battery.current_station_id
        tenant_changed = is_system_admin() and 'tenant_id' in data and target_tenant_id != battery.tenant_id
        if (station_changed or tenant_changed) and data.get('current_station_id'):
            station = Station.query.filter_by(id=data.get('current_station_id'), tenant_id=target_tenant_id, is_deleted=False).first()
            if not station:
                return error_response('所属站点不属于选择的运营商', 400)
        for field in ['battery_code', 'model', 'capacity', 'power_level', 'status', 'voltage_type', 'current_station_id', 'rental_price_per_hour', 'deposit_amount', 'selling_price', 'voltage', 'temperature']:
            if field in data:
                setattr(battery, field, data[field])
        if 'battery_type' in data:
            battery.battery_type = data['battery_type']
        if 'status' in data:
            battery.status = data['status']
        if is_system_admin() and 'tenant_id' in data:
            battery.tenant_id = target_tenant_id
        battery.updated_at = datetime.now()
        log_admin_action('更新电池', battery.battery_code, '电池管理', extra={'battery_id': battery.id})
        db.session.commit()
        return success_response(attach_tenant_name(battery.to_dict()), '更新电池成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新电池失败: {str(e)}', 500)

@admin_bp.route('/batteries/<int:battery_id>', methods=['DELETE'])
@admin_required()
def delete_battery(battery_id):
    """删除电池"""
    try:
        battery = get_admin_record(Battery, battery_id)
        if not battery:
            return error_response('电池不存在', 404)
        battery_code = battery.battery_code
        battery.is_deleted = True
        battery.updated_at = datetime.now()
        log_admin_action('删除电池', battery_code, '电池管理', status='warning', extra={'battery_id': battery.id})
        db.session.commit()
        return success_response(None, '删除电池成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除电池失败: {str(e)}', 500)

# ==================== 订单管理 ====================

@admin_bp.route('/orders', methods=['GET'])
@admin_required()
def get_orders():
    """获取订单列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')

        query = Order.query.filter_by(tenant_id=g.tenant_id, is_deleted=False)
        if keyword:
            query = query.filter(Order.order_no.like(f'%{keyword}%'))
        if status:
            query = query.filter(Order.status == status)
        query = query.order_by(Order.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        orders_data = []
        for order in pagination.items:
            order_dict = order.to_dict()
            if order.user_id:
                user = User.query.filter_by(id=order.user_id, tenant_id=g.tenant_id, is_deleted=False).first()
                order_dict['user_name'] = user.username if user else ''
            else:
                order_dict['user_name'] = ''
            orders_data.append(order_dict)

        return paginate_response(
            orders_data,
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取订单列表成功'
        )
    except Exception as e:
        return error_response(f'获取订单列表失败: {str(e)}', 500)

@admin_bp.route('/orders/<int:order_id>', methods=['GET'])
@admin_required()
def get_order_detail(order_id):
    """获取订单详情"""
    try:
        order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not order:
            return error_response('订单不存在', 404)
        order_dict = order.to_dict()
        if order.user_id:
            user = User.query.filter_by(id=order.user_id, tenant_id=g.tenant_id, is_deleted=False).first()
            order_dict['user_name'] = user.username if user else ''
        if order.battery_id:
            battery = Battery.query.filter_by(id=order.battery_id, tenant_id=g.tenant_id, is_deleted=False).first()
            order_dict['battery_code'] = battery.battery_code if battery else ''
        if order.station_id:
            station = Station.query.filter_by(id=order.station_id, tenant_id=g.tenant_id, is_deleted=False).first()
            order_dict['station_name'] = station.name if station else ''
        return success_response(order_dict, '获取订单详情成功')
    except Exception as e:
        return error_response(f'获取订单详情失败: {str(e)}', 500)

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@admin_required()
def update_order_status(order_id):
    """更新订单状态"""
    try:
        order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not order:
            return error_response('订单不存在', 404)
        data = request.get_json()
        new_status = data.get('status')
        if not new_status:
            return error_response('缺少 status 参数', 400)
        ok, msg = order.transition_status(new_status)
        if not ok:
            return error_response(msg, 400)
        order.updated_at = datetime.now()
        log_admin_action('更新订单状态', order.order_no, '订单管理', extra={'status': order.status, 'order_id': order.id})
        db.session.commit()
        return success_response(order.to_dict(), '更新订单状态成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新订单状态失败: {str(e)}', 500)

@admin_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@admin_required()
def cancel_order(order_id):
    """取消订单"""
    try:
        order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not order:
            return error_response('订单不存在', 404)
        data = request.get_json() or {}
        reason = data.get('reason', '管理员取消')
        ok, msg = order.transition_status('cancelled', reason=reason)
        if not ok:
            return error_response(msg, 400)
        order.updated_at = datetime.now()
        log_admin_action('取消订单', order.order_no, '订单管理', status='warning', extra={'reason': order.cancel_reason, 'order_id': order.id})
        db.session.commit()
        return success_response(order.to_dict(), '取消订单成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'取消订单失败: {str(e)}', 500)

@admin_bp.route('/orders/<int:order_id>/refund', methods=['POST'])
@admin_required()
def refund_order(order_id):
    """退款"""
    try:
        order = Order.query.filter_by(id=order_id, tenant_id=g.tenant_id, is_deleted=False).first()
        if not order:
            return error_response('订单不存在', 404)
        data = request.get_json() or {}
        refund_amount = float(data.get('amount', order.total_amount or 0))
        reason = data.get('reason', '管理员退款')
        # 走支付服务退款（含电池归还逻辑）
        ok, result = PaymentService.refund_order(order_id, refund_amount, reason)
        if not ok:
            return error_response(result, 400)
        order.refund_reason = reason
        order.updated_at = datetime.now()
        log_admin_action('订单退款', order.order_no, '订单管理', status='danger', extra={'reason': reason, 'order_id': order.id})
        db.session.commit()
        return success_response(order.to_dict(), '退款成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'退款失败: {str(e)}', 500)

# ==================== 数据统计 ====================

@admin_bp.route('/statistics/revenue', methods=['GET'])
@admin_required()
def get_revenue_stats():
    """营收统计（近30天每日营收）"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now().date() - timedelta(days=days - 1)
        rows = db.session.query(
            func.date(Order.created_at).label('day'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('count')
        ).filter(
            Order.tenant_id == g.tenant_id,
            Order.status.in_(['paid', 'completed', 'rented']),
            Order.is_deleted == False,
            func.date(Order.created_at) >= start_date
        ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()

        result = []
        day_map = {str(r.day): {'revenue': float(r.revenue or 0), 'count': int(r.count)} for r in rows}
        for i in range(days):
            d = str(start_date + timedelta(days=i))
            info = day_map.get(d, {'revenue': 0, 'count': 0})
            result.append({'date': d, 'revenue': info['revenue'], 'order_count': info['count']})

        total_revenue = sum(item['revenue'] for item in result)
        total_orders = sum(item['order_count'] for item in result)
        return success_response({
            'daily': result,
            'total_revenue': round(total_revenue, 2),
            'total_orders': total_orders
        }, '获取营收统计成功')
    except Exception as e:
        return error_response(f'获取营收统计失败: {str(e)}', 500)

@admin_bp.route('/statistics/orders', methods=['GET'])
@admin_required()
def get_order_stats():
    """订单量统计（按类型、按状态）"""
    try:
        by_type = db.session.query(
            Order.order_type, func.count(Order.id)
        ).filter(
            Order.tenant_id == g.tenant_id, Order.is_deleted == False
        ).group_by(Order.order_type).all()

        by_status = db.session.query(
            Order.status, func.count(Order.id)
        ).filter(
            Order.tenant_id == g.tenant_id, Order.is_deleted == False
        ).group_by(Order.status).all()

        return success_response({
            'by_type': [{'type': t, 'count': c} for t, c in by_type],
            'by_status': [{'status': s, 'count': c} for s, c in by_status]
        }, '获取订单统计成功')
    except Exception as e:
        return error_response(f'获取订单统计失败: {str(e)}', 500)

@admin_bp.route('/statistics/batteries', methods=['GET'])
@admin_required()
def get_battery_stats():
    """电池使用率分析"""
    try:
        by_status = db.session.query(
            Battery.status, func.count(Battery.id)
        ).filter(
            Battery.tenant_id == g.tenant_id, Battery.is_deleted == False
        ).group_by(Battery.status).all()

        total = sum(c for _, c in by_status)
        in_use = sum(c for s, c in by_status if s in ('in_use', 'rented'))
        utilization = round((in_use / total * 100) if total > 0 else 0, 1)

        return success_response({
            'by_status': [{'status': s, 'count': c} for s, c in by_status],
            'total': total,
            'in_use': in_use,
            'utilization': utilization
        }, '获取电池统计成功')
    except Exception as e:
        return error_response(f'获取电池统计失败: {str(e)}', 500)

@admin_bp.route('/statistics/stations', methods=['GET'])
@admin_required()
def get_station_stats():
    """站点运营数据"""
    try:
        stations = Station.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).all()
        result = []
        for st in stations:
            order_count = Order.query.filter_by(station_id=st.id, tenant_id=g.tenant_id, is_deleted=False).count()
            user_count = db.session.query(func.count(func.distinct(Order.user_id))).filter(
                Order.station_id == st.id, Order.tenant_id == g.tenant_id, Order.is_deleted == False
            ).scalar() or 0
            result.append({
                'station_id': st.id,
                'name': st.name,
                'address': st.address,
                'status': st.status,
                'total_batteries': st.total_batteries or 0,
                'available_batteries': st.available_batteries or 0,
                'order_count': order_count,
                'user_count': user_count
            })
        return success_response(result, '获取站点统计成功')
    except Exception as e:
        return error_response(f'获取站点统计失败: {str(e)}', 500)

# ==================== 换电服务 ====================

@admin_bp.route('/exchange/records', methods=['GET'])
@admin_required()
def get_exchange_records():
    """换电记录查询"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        query = Order.query.filter_by(
            tenant_id=g.tenant_id, order_type='exchange', is_deleted=False
        ).order_by(Order.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for o in pagination.items:
            d = o.to_dict()
            if o.user_id:
                u = User.query.get(o.user_id)
                d['user_name'] = u.username if u else ''
            items.append(d)
        return paginate_response(items, {
            'total': pagination.total, 'page': pagination.page,
            'per_page': pagination.per_page, 'pages': pagination.pages
        }, '获取换电记录成功')
    except Exception as e:
        return error_response(f'获取换电记录失败: {str(e)}', 500)

# ==================== 系统设置 ====================

import logging
logger = logging.getLogger(__name__)

@admin_bp.route('/map/geocode', methods=['GET'])
@admin_required()
def geocode_address():
    """高德地址解析"""
    logger.info(f'[Geocode] ========== 请求进入 geocode_address ==========')
    logger.info(f'[Geocode] request.args: {dict(request.args)}')
    try:
        address = (request.args.get('address') or '').strip()
        city = (request.args.get('city') or '').strip() or None
        logger.info(f'[Geocode] 解析后参数: address="{address}", city={city}')

        if not address:
            logger.warning('[Geocode] address 为空，返回 400')
            return error_response('address不能为空', 400)

        logger.info(f'[Geocode] 收到地址解析请求: address={address}, city={city}')

        api_key = AMapService.get_api_key()
        logger.info(f'[Geocode] 当前生效 Key: {"已配置 (隐藏)" if api_key else "未配置!!!"}')

        if not api_key:
            logger.warning('[Geocode] API Key 未配置')
            return error_response('高德地图 Key 未配置，请前往系统设置填写', 400)

        result = AMapService.geocode(address, city)
        logger.info(f'[Geocode] 解析结果: {result}')

        if not result.get('success'):
            logger.warning(f'[Geocode] 解析失败: {result.get("message")}')
            return error_response(result.get('message', '地址解析失败'), 400)

        return success_response(result.get('data'), '地址解析成功')
    except Exception as e:
        logger.exception('[Geocode] 解析异常:')
        return error_response(f'地址解析失败: {str(e)}', 500)

@admin_bp.route('/settings', methods=['GET'])
@admin_required()
def get_settings():
    """获取系统设置"""
    try:
        runtime_settings = {
            **SYSTEM_SETTINGS,
            'amapKey': SystemConfig.get_value('amap_key', SYSTEM_SETTINGS.get('amapKey', '')),
            'wechatAppId': SystemConfig.get_value('wechat_app_id', SYSTEM_SETTINGS.get('wechatAppId', '')),
            'wechatMchId': SystemConfig.get_value('wechat_mch_id', SYSTEM_SETTINGS.get('wechatMchId', ''))
        }
        return success_response({
            **runtime_settings,
            'packages': [
                {'id': 1, 'name': '日租套餐', 'hours': 24, 'price': 10.0},
                {'id': 2, 'name': '周租套餐', 'hours': 168, 'price': 50.0},
                {'id': 3, 'name': '月租套餐', 'hours': 720, 'price': 150.0}
            ]
        }, '获取设置成功')
    except Exception as e:
        return error_response(f'获取设置失败: {str(e)}', 500)

@admin_bp.route('/settings', methods=['PUT'])
@admin_required()
def update_settings():
    """更新系统设置"""
    try:
        data = request.get_json() or {}
        allowed_fields = set(SYSTEM_SETTINGS.keys())
        for field, value in data.items():
            if field in allowed_fields:
                SYSTEM_SETTINGS[field] = value

        if 'amapKey' in data:
            SystemConfig.set_value('amap_key', data.get('amapKey') or '')
        if 'wechatAppId' in data:
            SystemConfig.set_value('wechat_app_id', data.get('wechatAppId') or '')
        if 'wechatMchId' in data:
            SystemConfig.set_value('wechat_mch_id', data.get('wechatMchId') or '')

        runtime_settings = {
            **SYSTEM_SETTINGS,
            'amapKey': SystemConfig.get_value('amap_key', SYSTEM_SETTINGS.get('amapKey', '')),
            'wechatAppId': SystemConfig.get_value('wechat_app_id', SYSTEM_SETTINGS.get('wechatAppId', '')),
            'wechatMchId': SystemConfig.get_value('wechat_mch_id', SYSTEM_SETTINGS.get('wechatMchId', ''))
        }
        return success_response({
            **runtime_settings,
            'packages': [
                {'id': 1, 'name': '日租套餐', 'hours': 24, 'price': 10.0},
                {'id': 2, 'name': '周租套餐', 'hours': 168, 'price': 50.0},
                {'id': 3, 'name': '月租套餐', 'hours': 720, 'price': 150.0}
            ]
        }, '设置更新成功')
    except Exception as e:
        return error_response(f'更新设置失败: {str(e)}', 500)

# ==================== 操作日志 ====================

@admin_bp.route('/logs', methods=['GET'])
@admin_required()
def get_operation_logs():
    """获取操作日志"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        action = request.args.get('action', '').strip()
        query = OperationLog.query.filter_by(tenant_id=g.tenant_id, is_deleted=False)
        if action:
            query = query.filter(
                (OperationLog.action.like(f'%{action}%')) |
                (OperationLog.module.like(f'%{action}%'))
            )
        query = query.order_by(OperationLog.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return paginate_response(
            [item.to_dict() for item in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取日志成功'
        )
    except Exception as e:
        return error_response(f'获取日志失败: {str(e)}', 500)

# ==================== 故障报修管理 ====================

@admin_bp.route('/fault-reports', methods=['GET'])
@admin_required()
def get_fault_reports():
    """获取故障报修列表"""
    try:
        from ..models.fault_report import FaultReport

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        report_no = request.args.get('report_no', '').strip()
        fault_type = request.args.get('fault_type', '').strip()
        status = request.args.get('status', '').strip()

        query = FaultReport.query.filter_by(tenant_id=g.tenant_id, is_deleted=False)

        if report_no:
            query = query.filter(FaultReport.report_no.like(f'%{report_no}%'))
        if fault_type:
            query = query.filter_by(fault_type=fault_type)
        if status:
            query = query.filter_by(status=status)

        query = query.order_by(FaultReport.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginate_response(
            [item.to_dict() for item in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取报修列表成功'
        )
    except Exception as e:
        return error_response(f'获取报修列表失败: {str(e)}', 500)

@admin_bp.route('/fault-reports/<int:report_id>', methods=['PUT'])
@admin_required()
def update_fault_report(report_id):
    """更新故障报修状态"""
    try:
        from ..models.fault_report import FaultReport

        report = FaultReport.query.filter_by(
            id=report_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not report:
            return error_response('报修记录不存在', 404)

        data = request.get_json()

        if 'status' in data:
            report.status = data['status']
        if 'admin_remarks' in data:
            report.admin_remarks = data['admin_remarks']

        report.updated_at = datetime.now()
        db.session.commit()

        log_admin_action('处理报修', report.report_no, '故障报修', extra={'status': report.status})

        return success_response(report.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}', 500)

# ==================== 消息通知管理 ====================

@admin_bp.route('/notifications', methods=['GET'])
@admin_required()
def get_notifications():
    """获取消息通知列表"""
    try:
        from ..models.notification import Notification

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        noti_type = request.args.get('noti_type', '').strip()
        user_id = request.args.get('user_id', '').strip()

        query = Notification.query.filter_by(tenant_id=g.tenant_id, is_deleted=False)

        if noti_type:
            query = query.filter_by(noti_type=noti_type)
        if user_id:
            query = query.filter_by(user_id=int(user_id))

        query = query.order_by(Notification.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginate_response(
            [item.to_dict() for item in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取通知列表成功'
        )
    except Exception as e:
        return error_response(f'获取通知列表失败: {str(e)}', 500)

@admin_bp.route('/notifications', methods=['POST'])
@admin_required()
def create_notification():
    """发送消息通知"""
    try:
        from ..models.notification import Notification

        data = request.get_json()
        noti_type = data.get('noti_type', 'system')
        user_id = data.get('user_id')
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title or not content:
            return error_response('标题和内容不能为空', 400)

        # 如果指定了用户ID，发送给该用户
        if user_id:
            notification = Notification(
                user_id=int(user_id),
                noti_type=noti_type,
                title=title,
                content=content,
                tenant_id=g.tenant_id
            )
            notification.save()
            log_admin_action('发送通知', f'用户#{user_id}', '消息通知')
            return success_response(notification.to_dict(), '发送成功')

        # 否则发送给所有用户
        users = User.query.filter_by(tenant_id=g.tenant_id, is_deleted=False).all()
        count = 0
        for user in users:
            notification = Notification(
                user_id=user.id,
                noti_type=noti_type,
                title=title,
                content=content,
                tenant_id=g.tenant_id
            )
            notification.save()
            count += 1

        log_admin_action('群发通知', f'{count}个用户', '消息通知')
        return success_response({'count': count}, f'成功发送给{count}个用户')

    except Exception as e:
        db.session.rollback()
        return error_response(f'发送失败: {str(e)}', 500)

@admin_bp.route('/notifications/<int:noti_id>', methods=['DELETE'])
@admin_required()
def delete_notification(noti_id):
    """删除消息通知"""
    try:
        from ..models.notification import Notification

        notification = Notification.query.filter_by(
            id=noti_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not notification:
            return error_response('通知不存在', 404)

        notification.is_deleted = True
        notification.updated_at = datetime.now()
        db.session.commit()

        log_admin_action('删除通知', f'ID#{noti_id}', '消息通知', status='warning')

        return success_response(None, '删除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}', 500)

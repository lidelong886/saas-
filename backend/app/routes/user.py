"""
用户路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id
from datetime import datetime, timedelta
from sqlalchemy import func
from .. import limiter

from ..models import User
from ..models import WalletTransaction
from ..services.user_service import UserService
from ..utils.response import success_response, error_response, paginate_response
from ..utils.validators import validate_phone, validate_email

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    获取用户个人信息（包含租户品牌信息）
    """
    try:
        from ..models import Tenant
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        # 获取租户品牌信息
        tenant = Tenant.query.get(g.tenant_id)
        tenant_info = None
        if tenant:
            tenant_info = {
                'name': tenant.name,
                'brand_name': tenant.brand_name,
                'brand_logo': tenant.brand_logo
            }

        user_data = user.to_dict(include_private=True)
        user_data['tenant_info'] = tenant_info

        return success_response(user_data, '获取成功')

    except Exception as e:
        return error_response(f'获取用户信息失败: {str(e)}', 500)

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    获取用户统计信息（订单数、完成数、消费金额、今日/本周统计、套餐、租用电池）
    """
    try:
        from ..models import Order, ExchangeRecord, Package, Battery
        from .. import db
        user_id = get_current_user_id()

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())

        # ===== 原有统计 =====
        total_orders = Order.query.filter_by(
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).count()

        completed_orders = Order.query.filter_by(
            user_id=user_id,
            tenant_id=g.tenant_id,
            status='completed',
            is_deleted=False
        ).count()

        active_orders = Order.query.filter(
            Order.user_id == user_id,
            Order.tenant_id == g.tenant_id,
            Order.is_deleted == False,
            Order.status.in_(['pending', 'paid', 'rented', 'returned'])
        ).count()

        # 用 SQL 聚合替代 Python 循环
        total_amount_result = db.session.query(
            func.coalesce(func.sum(Order.total_amount), 0)
        ).filter(
            Order.user_id == user_id,
            Order.status == 'completed',
            Order.is_deleted == False,
            Order.tenant_id == g.tenant_id
        ).scalar()

        # ===== 新增：今日统计 =====
        today_stats = db.session.query(
            func.count(Order.id).label('count'),
            func.coalesce(func.sum(Order.total_amount), 0).label('amount')
        ).filter(
            Order.user_id == user_id,
            Order.status == 'completed',
            Order.is_deleted == False,
            Order.tenant_id == g.tenant_id,
            Order.created_at >= today_start
        ).first()

        # ===== 新增：本周统计 =====
        week_stats = db.session.query(
            func.count(Order.id).label('count'),
            func.coalesce(func.sum(Order.total_amount), 0).label('amount')
        ).filter(
            Order.user_id == user_id,
            Order.status == 'completed',
            Order.is_deleted == False,
            Order.tenant_id == g.tenant_id,
            Order.created_at >= week_start
        ).first()

        # ===== 新增：换电次数 =====
        today_exchanges = ExchangeRecord.query.filter(
            ExchangeRecord.user_id == user_id,
            ExchangeRecord.status == 'completed',
            ExchangeRecord.is_deleted == False,
            ExchangeRecord.tenant_id == g.tenant_id,
            ExchangeRecord.created_at >= today_start
        ).count()

        week_exchanges = ExchangeRecord.query.filter(
            ExchangeRecord.user_id == user_id,
            ExchangeRecord.status == 'completed',
            ExchangeRecord.is_deleted == False,
            ExchangeRecord.tenant_id == g.tenant_id,
            ExchangeRecord.created_at >= week_start
        ).count()

        from ..models import UserPackage
        
        # ===== 新增：当前套餐信息 =====
        current_package = None
        
        # 查找正在使用中的套餐 (active)，或者购买了未使用的套餐 (unused)
        # 优先级：正在使用的 > 刚购买未使用的
        active_package = UserPackage.query.filter(
            UserPackage.user_id == user_id,
            UserPackage.status == 'active',
            UserPackage.is_deleted == False,
            UserPackage.tenant_id == g.tenant_id
        ).order_by(UserPackage.expires_at.desc()).first()
        
        if not active_package:
            active_package = UserPackage.query.filter(
                UserPackage.user_id == user_id,
                UserPackage.status == 'unused',
                UserPackage.is_deleted == False,
                UserPackage.tenant_id == g.tenant_id
            ).order_by(UserPackage.created_at.desc()).first()

        if active_package:
            pkg = Package.query.get(active_package.package_id)
            current_package = {
                'name': active_package.package_name,
                'type': active_package.package_type,
                'price': float(pkg.price) if pkg else 0,
                'started_at': active_package.activated_at.isoformat() if active_package.activated_at else None,
                'expires_at': active_package.expires_at.isoformat() if active_package.expires_at else None,
                'status': active_package.status
            }
        else:
            # 兼容旧逻辑（如果旧用户有未完成订单里的套餐）
            package_order = Order.query.filter(
                Order.user_id == user_id,
                Order.order_type == 'rental',
                Order.status.in_(['paid', 'rented']),
                Order.is_deleted == False,
                Order.tenant_id == g.tenant_id,
                Order.package_id != None
            ).order_by(Order.created_at.desc()).first()

            if package_order and package_order.package_id:
                pkg = Package.query.get(package_order.package_id)
                if pkg:
                    current_package = {
                        'name': pkg.name,
                        'type': pkg.package_type,
                        'price': float(pkg.price) if pkg.price else 0,
                        'started_at': package_order.rental_start_time.isoformat() if package_order.rental_start_time else None,
                        'expires_at': package_order.expected_return_time.isoformat() if package_order.expected_return_time else None,
                    }

        # ===== 新增：当前租用电池信息 =====
        rented_battery = Battery.query.filter(
            Battery.current_user_id == user_id,
            Battery.status == 'rented', Battery.owner_id == None,
            Battery.is_deleted == False,
            Battery.tenant_id == g.tenant_id
        ).first()

        rented_battery_info = None
        if rented_battery:
            active_order = Order.query.filter_by(
                user_id=user_id,
                battery_id=rented_battery.id,
                status='rented',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).order_by(Order.id.desc()).first()
            
            rented_battery_info = {
                'id': rented_battery.id,
                'battery_code': rented_battery.battery_code,
                'model': rented_battery.model,
                'power_level': rented_battery.power_level,
                'voltage': float(rented_battery.voltage) if rented_battery.voltage else None,
                'rented_at': rented_battery.rented_at.isoformat() if rented_battery.rented_at else None,
                'order_no': active_order.order_no if active_order else None
            }

        return success_response({
            # 原有字段（保持向后兼容）
            'totalOrders': total_orders,
            'completedOrders': completed_orders,
            'activeOrders': active_orders,
            'totalAmount': round(float(total_amount_result), 2),

            # 新增字段
            'todayOrders': today_stats.count if today_stats else 0,
            'todayAmount': round(float(today_stats.amount), 2) if today_stats else 0,
            'todayExchanges': today_exchanges,

            'weekOrders': week_stats.count if week_stats else 0,
            'weekAmount': round(float(week_stats.amount), 2) if week_stats else 0,
            'weekExchanges': week_exchanges,

            'currentPackage': current_package,
            'rentedBattery': rented_battery_info,
        }, '获取成功')
    except Exception as e:
        return error_response(f'获取统计失败: {str(e)}', 500)

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    更新用户个人信息
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        data = request.get_json()

        # 可更新的字段
        updatable_fields = [
            'nickname', 'real_name', 'gender', 'birth_date',
            'avatar', 'work_status', 'id_card_no'
        ]

        update_data = {}
        for field in updatable_fields:
            if field in data:
                if field == 'birth_date' and data[field]:
                    # 验证日期格式
                    try:
                        datetime.strptime(data[field], '%Y-%m-%d')
                    except ValueError:
                        return error_response('出生日期格式不正确', 400)

                update_data[field] = data[field]

        if update_data:
            user.update_from_dict(update_data)
            if 'real_name' in update_data or 'id_card_no' in update_data:
                if user.real_name and user.id_card_no:
                    user.realname_status = 'verified'
                    user.is_verified = True
                else:
                    user.realname_status = 'unverified'
                    user.is_verified = False
            user.save()

        return success_response(user.to_dict(include_private=True), '更新成功')

    except Exception as e:
        return error_response(f'更新用户信息失败: {str(e)}', 500)

@user_bp.route('/location', methods=['PUT'])
@jwt_required()
def update_location():
    """
    更新用户位置
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        data = request.get_json()

        if not data.get('latitude') or not data.get('longitude'):
            return error_response('经纬度不能为空', 400)

        latitude = data['latitude']
        longitude = data['longitude']

        # 简单的坐标验证
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return error_response('坐标范围不正确', 400)

        user.update_location(latitude, longitude)

        return success_response(None, '位置更新成功')

    except Exception as e:
        return error_response(f'位置更新失败: {str(e)}', 500)

@user_bp.route('/bind-phone', methods=['POST'])
@jwt_required()
def bind_phone():
    """
    绑定手机号
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        data = request.get_json()

        if not data.get('phone') or not data.get('sms_code'):
            return error_response('手机号和验证码不能为空', 400)

        phone = data['phone'].strip()
        sms_code = data['sms_code']

        # 验证手机号格式
        if not validate_phone(phone):
            return error_response('手机号格式不正确', 400)

        # 检查手机号是否已被其他用户绑定
        existing_user = User.query.filter_by(
            phone=phone,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if existing_user and existing_user.id != user.id:
            return error_response('该手机号已被其他用户绑定', 400)

        # 验证短信验证码
        from ..services.auth_service import AuthService
        if not AuthService.verify_sms_code(phone, sms_code, 'bind_phone'):
            return error_response('短信验证码错误或已过期', 400)

        # 更新手机号
        user.phone = phone
        user.save()

        return success_response(user.to_dict(), '手机号绑定成功')

    except Exception as e:
        return error_response(f'绑定手机号失败: {str(e)}', 500)

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    修改密码
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        data = request.get_json()

        required_fields = ['old_password', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field}不能为空', 400)

        old_password = data['old_password']
        new_password = data['new_password']

        # 验证旧密码
        if not user.verify_password(old_password):
            return error_response('旧密码错误', 400)

        # 验证新密码强度
        from ..utils.validators import validate_password
        if not validate_password(new_password):
            return error_response('新密码至少8位，必须包含字母和数字', 400)

        # 更新密码
        user.password = new_password
        user.save()

        return success_response(None, '密码修改成功')

    except Exception as e:
        return error_response(f'密码修改失败: {str(e)}', 500)

@user_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    """
    获取用户余额
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        return success_response({
            'balance': float(user.balance),
            'points': user.points
        }, '获取成功')

    except Exception as e:
        return error_response(f'获取余额失败: {str(e)}', 500)

@user_bp.route('/recharge', methods=['POST'])
@jwt_required()
def recharge_balance():
    """
    余额充值
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        data = request.get_json()

        if not data.get('amount'):
            return error_response('充值金额不能为空', 400)

        amount = data['amount']

        if not isinstance(amount, (int, float)) or amount <= 0:
            return error_response('充值金额必须大于0', 400)

        # 创建充值订单（这里简化为直接增加余额）
        # 实际项目中应该创建支付订单
        user.add_balance(amount)

        return success_response({
            'balance': float(user.balance)
        }, '充值成功')

    except Exception as e:
        return error_response(f'充值失败: {str(e)}', 500)


@user_bp.route('/wallet/transactions', methods=['GET'])
@jwt_required()
def get_wallet_transactions():
    """获取钱包流水"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = get_current_user_id()

        pagination = WalletTransaction.query.filter_by(
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).order_by(WalletTransaction.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return paginate_response(
            [item.to_dict() for item in pagination.items],
            {'total': pagination.total, 'page': pagination.page, 'per_page': pagination.per_page, 'pages': pagination.pages},
            '获取钱包流水成功'
        )
    except Exception as e:
        return error_response(f'获取钱包流水失败: {str(e)}', 500)

@user_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_user_preferences():
    """
    获取用户偏好设置
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        # 返回用户偏好设置（目前只有模式）
        preferences = {
            'mode': user.preferences.get('mode', 'normal') if user.preferences else 'normal'
        }

        return success_response(preferences, '获取成功')

    except Exception as e:
        return error_response(f'获取用户偏好失败: {str(e)}', 500)

@user_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_user_preferences():
    """
    更新用户偏好设置
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        data = request.get_json()

        # 获取当前偏好设置
        preferences = user.preferences or {}

        # 更新模式设置
        if 'mode' in data:
            mode = data['mode']
            if mode not in ['normal', 'delivery']:
                return error_response('模式参数不正确，只能是 normal 或 delivery', 400)
            preferences['mode'] = mode

        # 保存偏好设置
        user.preferences = preferences
        user.save()

        return success_response(preferences, '更新成功')

    except Exception as e:
        return error_response(f'更新用户偏好失败: {str(e)}', 500)

@user_bp.route('/riders/nearby', methods=['GET'])
@jwt_required()
def get_nearby_riders():
    """
    获取附近骑手
    """
    try:
        user_id = get_current_user_id()
        user = User.get_by_id(user_id)

        if not user:
            return error_response('用户不存在', 404)

        # 获取查询参数
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', 5, type=int)  # 默认5公里

        if not latitude or not longitude:
            return error_response('经纬度参数不能为空', 400)

        # 查找附近骑手
        nearby_riders = User.get_nearby_riders(latitude, longitude, radius)

        # 格式化返回数据（不包含敏感信息）
        riders_data = []
        for rider in nearby_riders:
            rider_info = {
                'id': rider.id,
                'nickname': rider.nickname,
                'avatar': rider.avatar,
                'latitude': rider.latitude,
                'longitude': rider.longitude,
                'work_status': rider.work_status,
                'last_location_update': rider.location_updated_at.isoformat() if rider.location_updated_at else None
            }
            riders_data.append(rider_info)

        return success_response({
            'riders': riders_data,
            'total': len(riders_data)
        }, '获取成功')

    except Exception as e:
        return error_response(f'获取附近骑手失败: {str(e)}', 500)

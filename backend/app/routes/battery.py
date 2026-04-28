"""
电池管理路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required, get_jwt
from ..utils.auth_helpers import get_current_user_id
from ..models import Battery, Station, Cabinet, Order, UserPackage, Package
from ..services.battery_service import BatteryService
from ..utils.admin_auth import admin_required, permission_required
from ..utils.response import success_response, error_response, paginate_response
from ..utils.validators import validate_battery_code, validate_positive_number, validate_integer, sanitize_input
from .. import db, limiter

battery_bp = Blueprint('battery', __name__)

@battery_bp.route('/scan/<battery_code>', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")  # 扫描限制：每分钟30次
def scan_battery(battery_code):
    """
    扫描电池二维码
    """
    try:
        battery_code = sanitize_input(battery_code, max_length=50)
        if not validate_battery_code(battery_code):
            return error_response('电池编码格式不正确', 400)

        battery = Battery.query.filter_by(
            battery_code=battery_code,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not battery:
            return error_response('电池不存在', 404)

        return success_response(battery.to_dict(), '电池信息获取成功')

    except Exception as e:
        return error_response(f'扫描电池失败: {str(e)}', 500)

@battery_bp.route('/available', methods=['GET'])
@jwt_required(optional=True)
def get_available_batteries():
    """
    获取可用电池列表
    """
    try:
        station_id = request.args.get('station_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        filters = {'status': 'available'}
        if station_id:
            filters['current_station_id'] = station_id

        pagination = Battery.get_list(
            page=page,
            per_page=per_page,
            filters=filters
        )

        return paginate_response(
            [battery.to_dict() for battery in pagination['items']],
            pagination,
            '获取可用电池列表成功'
        )

    except Exception as e:
        return error_response(f'获取可用电池列表失败: {str(e)}', 500)

@battery_bp.route('/<int:battery_id>', methods=['GET'])
@jwt_required()
def get_battery(battery_id):
    """
    获取电池详情
    """
    try:
        battery = Battery.get_by_id(battery_id)
        if not battery:
            return error_response('电池不存在', 404)

        return success_response(battery.to_dict(), '电池详情获取成功')

    except Exception as e:
        return error_response(f'获取电池详情失败: {str(e)}', 500)

@battery_bp.route('/<int:battery_id>/rent', methods=['POST'])
@jwt_required()
def rent_battery(battery_id):
    """
    租用电池
    有套餐: 0元自动完成
    无套餐: 创建待支付订单
    """
    try:
        data = request.get_json() or {}
        hours = data.get('hours', 24)
        station_id = data.get('station_id')
        cabinet_id = data.get('cabinet_id')

        if not validate_positive_number(hours) or float(hours) > 168:
            return error_response('租用时长必须在1-168小时之间', 400)

        user_id = get_current_user_id()

        success, result = BatteryService.rent_battery(
            user_id=user_id,
            battery_id=battery_id,
            hours=float(hours),
            station_id=station_id,
            cabinet_id=cabinet_id
        )

        if not success:
            return error_response(result, 400)

        # 有套餐时 result 中有 package_id
        if result.get('package_id'):
            return success_response(result, '租用成功，无需支付')

        return success_response(result, '订单创建成功，请完成支付')

    except Exception as e:
        db.session.rollback()
        return error_response(f'租用电池失败: {str(e)}', 500)

@battery_bp.route('/<int:battery_id>/return', methods=['POST'])
@jwt_required()
def return_battery(battery_id):
    """
    归还电池
    """
    try:
        data = request.get_json()
        station_id = data.get('station_id')
        cabinet_id = data.get('cabinet_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        battery = Battery.get_by_id(battery_id)
        if not battery:
            return error_response('电池不存在', 404)

        user_id = get_current_user_id()
        
        # 检查电池是否属于当前用户
        if battery.current_user_id != user_id:
            return error_response('该电池不属于您', 403)

        success, result = BatteryService.return_battery(
            battery_id, station_id, cabinet_id, latitude, longitude
        )
        if not success:
            return error_response(result, 400)

        return success_response(result, '电池归还成功')

    except Exception as e:
        return error_response(f'归还电池失败: {str(e)}', 500)

@battery_bp.route('/<int:battery_id>/status', methods=['PUT'])
@admin_required()
@permission_required('battery:edit')
def update_battery_status(battery_id):
    """
    更新电池状态（管理员功能）
    """
    try:
        data = request.get_json()

        battery = Battery.get_by_id(battery_id)
        if not battery:
            return error_response('电池不存在', 404)

        # 更新电池状态
        if 'power_level' in data:
            power_level = data['power_level']
            if not validate_integer(power_level, 0, 100):
                return error_response('电量必须在0-100之间', 400)
            battery.power_level = power_level

        if 'status' in data:
            battery.status = data['status']

        if 'voltage' in data:
            battery.voltage = data['voltage']

        if 'temperature' in data:
            battery.temperature = data['temperature']

        battery.save()

        return success_response(battery.to_dict(), '电池状态更新成功')

    except Exception as e:
        return error_response(f'更新电池状态失败: {str(e)}', 500)

@battery_bp.route('/list', methods=['GET'])
@admin_required()
@permission_required('battery:view')
def get_battery_list():
    """
    获取电池列表（管理员功能）
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        station_id = request.args.get('station_id', type=int)

        filters = {}
        if status:
            filters['status'] = status
        if station_id:
            filters['current_station_id'] = station_id

        pagination = Battery.get_list(
            page=page,
            per_page=per_page,
            filters=filters
        )

        return paginate_response(
            [battery.to_dict() for battery in pagination['items']],
            pagination,
            '获取电池列表成功'
        )

    except Exception as e:
        return error_response(f'获取电池列表失败: {str(e)}', 500)

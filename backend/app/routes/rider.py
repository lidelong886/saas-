"""
骑手路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from ..utils.auth_helpers import get_current_user_id
from ..services.rider_service import RiderService
from ..utils.response import success_response, error_response, paginate_response

rider_bp = Blueprint('rider', __name__)


@rider_bp.route('/nearby-stations', methods=['GET'])
@jwt_required()
def get_nearby_stations():
    """获取附近站点（带可用电池数）"""
    try:
        user_id = get_current_user_id()

        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', 5, type=int)
        limit = request.args.get('limit', 20, type=int)

        if not latitude or not longitude:
            return error_response('缺少经纬度参数', 400)

        if radius > 50:
            return error_response('搜索半径不能超过50公里', 400)

        success, result = RiderService.get_nearby_stations_with_availability(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius,
            limit=limit
        )

        if not success:
            return error_response(result, 400)

        return success_response(result, '获取附近站点成功')

    except Exception as e:
        return error_response(f'获取附近站点失败: {str(e)}', 500)


@rider_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    """创建预约"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        station_id = data.get('station_id')
        duration_minutes = data.get('duration_minutes', 30)

        if not station_id:
            return error_response('缺少站点ID', 400)

        if duration_minutes < 10 or duration_minutes > 120:
            return error_response('预约时长必须在10-120分钟之间', 400)

        success, result = RiderService.create_reservation(
            user_id=user_id,
            station_id=station_id,
            duration_minutes=duration_minutes
        )

        if not success:
            return error_response(result, 400)

        return success_response(result, '预约成功')

    except Exception as e:
        return error_response(f'创建预约失败: {str(e)}', 500)


@rider_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def cancel_reservation(reservation_id):
    """取消预约"""
    try:
        user_id = get_current_user_id()

        success, result = RiderService.cancel_reservation(
            reservation_id=reservation_id,
            user_id=user_id
        )

        if not success:
            return error_response(result, 400)

        return success_response(result, '取消预约成功')

    except Exception as e:
        return error_response(f'取消预约失败: {str(e)}', 500)


@rider_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_reservations():
    """获取我的预约列表"""
    try:
        user_id = get_current_user_id()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', type=str)

        result = RiderService.get_user_reservations(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status
        )

        return paginate_response(result['items'], result, '获取预约列表成功')

    except Exception as e:
        return error_response(f'获取预约列表失败: {str(e)}', 500)


@rider_bp.route('/packages', methods=['GET'])
@jwt_required()
def get_rider_packages():
    """获取骑手专属套餐"""
    try:
        user_id = get_current_user_id()

        success, result = RiderService.get_rider_packages(user_id=user_id)

        if not success:
            return error_response(result, 400)

        return success_response(result, '获取骑手套餐成功')

    except Exception as e:
        return error_response(f'获取骑手套餐失败: {str(e)}', 500)

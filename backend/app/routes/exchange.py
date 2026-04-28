"""
换电路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from ..utils.auth_helpers import get_current_user_id
from ..services.exchange_service import ExchangeService
from ..services.rider_service import RiderService
from ..services.notification_service import NotificationService
from ..models import UserBehaviorLog
from ..utils.response import success_response, error_response

exchange_bp = Blueprint('exchange', __name__)

@exchange_bp.route('/do', methods=['POST'])
@jwt_required()
def do_exchange():
    """执行换电"""
    try:
        data = request.get_json()
        user_id = get_current_user_id()
        
        old_battery_id = data.get('old_battery_id')
        new_battery_id = data.get('new_battery_id')
        station_id = data.get('station_id')
        cabinet_id = data.get('cabinet_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not new_battery_id or not station_id:
            return error_response('缺少必要参数', 400)
            
        success, result = ExchangeService.exchange_battery(
            user_id=user_id,
            old_battery_id=old_battery_id,
            new_battery_id=new_battery_id,
            station_id=station_id,
            cabinet_id=cabinet_id,
            latitude=latitude,
            longitude=longitude
        )
        
        if not success:
            return error_response(result, 400)

        # 换电成功，创建通知
        try:
            if isinstance(result, dict):
                record_no = result.get('record_no', '')
                station_name = result.get('station_name', '')
                NotificationService.on_exchange_success(user_id, record_no, station_name)
        except Exception:
            pass

        return success_response(result, '换电成功')
        
    except Exception as e:
        return error_response(f'换电操作异常: {str(e)}', 500)

@exchange_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """获取换电记录"""
    try:
        user_id = get_current_user_id()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        result = ExchangeService.get_exchange_history(user_id, page, per_page)
        return success_response(result, '获取换电历史成功')

    except Exception as e:
        return error_response(f'获取换电历史失败: {str(e)}', 500)


@exchange_bp.route('/quick-swap', methods=['POST'])
@jwt_required()
def quick_swap():
    """快速换电（自动判断是否有骑手套餐）"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        old_battery_id = data.get('old_battery_id')
        new_battery_id = data.get('new_battery_id')
        station_id = data.get('station_id')
        cabinet_id = data.get('cabinet_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not new_battery_id or not station_id:
            return error_response('缺少必要参数', 400)

        # 检查用户是否有有效的骑手套餐
        has_package, package_info = RiderService.check_user_has_active_rider_package(user_id)

        # 执行换电
        success, result = ExchangeService.exchange_battery(
            user_id=user_id,
            old_battery_id=old_battery_id,
            new_battery_id=new_battery_id,
            station_id=station_id,
            cabinet_id=cabinet_id,
            latitude=latitude,
            longitude=longitude
        )

        if not success:
            return error_response(result, 400)

        # 添加套餐信息到返回结果
        if has_package:
            result['has_rider_package'] = True
            result['package_info'] = package_info
        else:
            result['has_rider_package'] = False

        # 记录用户行为
        try:
            UserBehaviorLog.log_action(
                user_id=user_id,
                action_type='swap',
                station_id=station_id,
                metadata={
                    'old_battery_id': old_battery_id,
                    'new_battery_id': new_battery_id,
                    'has_rider_package': has_package
                }
            )
        except:
            pass

        # 换电成功，创建通知
        try:
            if isinstance(result, dict):
                record_no = result.get('record_no', '')
                station_name = result.get('station_name', '')
                NotificationService.on_exchange_success(user_id, record_no, station_name)
        except Exception:
            pass

        return success_response(result, '换电成功')

    except Exception as e:
        return error_response(f'换电操作异常: {str(e)}', 500)

from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id
from ..models import Battery, Station, Cabinet
from ..utils.response import success_response, error_response

battery_my_bp = Blueprint('battery_my', __name__)

@battery_my_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_batteries():
    """
    获取我的电池（私人拥有的电池）
    """
    try:
        user_id = get_current_user_id()
        batteries = Battery.query.filter_by(
            owner_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).all()
        
        result = []
        for b in batteries:
            b_dict = b.to_dict()
            if b.status == 'charging' and b.current_station_id:
                station = Station.query.get(b.current_station_id)
                if station:
                    b_dict['station_name'] = station.name
                    b_dict['is_charging'] = True
                    b_dict['charging_eta_minutes'] = int((100 - (b.power_level or 0)) * 1.5)  # 估算充满时间
            result.append(b_dict)
            
        return success_response(result, '获取我的电池成功')

    except Exception as e:
        return error_response(f'获取我的电池失败: {str(e)}', 500)

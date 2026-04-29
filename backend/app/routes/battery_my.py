from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id
from ..models import Battery, Station, Cabinet
from ..models.cabinet import CabinetStatus
from ..utils.response import success_response, error_response
from .. import db

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


@battery_my_bp.route('/my/<int:battery_id>/charge', methods=['POST'])
@jwt_required()
def charge_my_battery(battery_id):
    """
    将已购买的专属电池放入公共站点充电。
    """
    try:
        data = request.get_json() or {}
        station_id = data.get('station_id')
        cabinet_id = data.get('cabinet_id')
        user_id = get_current_user_id()

        if not station_id:
            return error_response('请选择公共充电站点', 400)

        battery = Battery.query.filter_by(
            id=battery_id,
            owner_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()
        if not battery:
            return error_response('专属电池不存在', 404)
        if battery.status == 'charging':
            return error_response('该电池已在充电中', 400)

        station = Station.query.filter_by(
            id=station_id,
            tenant_id=g.tenant_id,
            is_deleted=False,
            status='active'
        ).first()
        if not station:
            return error_response('公共充电站点不可用', 404)

        cabinet_query = Cabinet.query.filter(
            Cabinet.station_id == station.id,
            Cabinet.tenant_id == g.tenant_id,
            Cabinet.is_deleted == False,
            Cabinet.status == CabinetStatus.ONLINE,
            Cabinet.is_online == True
        )
        if cabinet_id:
            cabinet_query = cabinet_query.filter(Cabinet.id == cabinet_id)

        cabinet = None
        slot_position = None
        for item in cabinet_query.order_by(Cabinet.id.asc()).all():
            slot_position = item.find_available_slot()
            if slot_position:
                cabinet = item
                break

        if not cabinet:
            return error_response('该站点暂无可用充电插槽', 400)

        battery.status = 'charging'
        battery.current_user_id = user_id
        battery.current_station_id = station.id
        battery.current_cabinet_id = cabinet.id
        battery.slot_position = slot_position
        db.session.add(battery)

        db.session.flush()
        cabinet.occupied_slots = Battery.query.filter(
            Battery.current_cabinet_id == cabinet.id,
            Battery.slot_position != None,
            Battery.is_deleted == False
        ).count()
        cabinet.available_slots = max((cabinet.total_slots or 0) - cabinet.occupied_slots, 0)
        cabinet.battery_count = Battery.query.filter_by(
            current_cabinet_id=cabinet.id,
            is_deleted=False
        ).count()
        station.total_batteries = Battery.query.filter_by(
            current_station_id=station.id,
            is_deleted=False
        ).count()
        station.available_batteries = Battery.query.filter_by(
            current_station_id=station.id,
            status='available',
            is_deleted=False
        ).count()
        station.charging_batteries = Battery.query.filter_by(
            current_station_id=station.id,
            status='charging',
            is_deleted=False
        ).count()
        db.session.commit()

        result = battery.to_dict()
        result['station_name'] = station.name
        result['cabinet_name'] = cabinet.name
        result['is_charging'] = True
        result['charging_eta_minutes'] = int((100 - (battery.power_level or 0)) * 1.5)
        return success_response(result, '已放入公共充电桩充电')

    except Exception as e:
        db.session.rollback()
        return error_response(f'发起充电失败: {str(e)}', 500)

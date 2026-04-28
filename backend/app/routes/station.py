"""
站点管理路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required, get_jwt
from ..models import Station
from ..services.station_service import StationService
from ..utils.admin_auth import admin_required, permission_required
from ..utils.response import success_response, error_response, paginate_response
from ..utils.validators import validate_positive_number

station_bp = Blueprint('station', __name__)

@station_bp.route('/nearby', methods=['GET'])
@jwt_required(optional=True)
def get_nearby_stations():
    """
    获取附近站点
    """
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', 5, type=int)

        if not latitude or not longitude:
            return error_response('经纬度参数不能为空', 400)

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return error_response('坐标范围不正确', 400)

        stations = StationService.get_nearby_stations(latitude, longitude, radius)

        return success_response({
            'stations': stations,
            'total': len(stations)
        }, '获取附近站点成功')

    except Exception as e:
        return error_response(f'获取附近站点失败: {str(e)}', 500)

@station_bp.route('/<int:station_id>', methods=['GET'])
@jwt_required(optional=True)
def get_station_detail(station_id):
    """
    获取站点详情
    """
    try:
        station = StationService.get_station_detail(station_id)

        if not station:
            return error_response('站点不存在', 404)

        return success_response(station, '获取站点详情成功')

    except Exception as e:
        return error_response(f'获取站点详情失败: {str(e)}', 500)

@station_bp.route('/list', methods=['GET'])
@admin_required()
@permission_required('station:view')
def get_station_list():
    """
    获取站点列表（管理员功能）
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        name = request.args.get('name')

        query = Station.query.filter_by(tenant_id=g.tenant_id, is_deleted=False)
        
        if name:
            query = query.filter(Station.name.contains(name))

        pagination = query.order_by(Station.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return paginate_response(
            [station.to_dict() for station in pagination.items],
            {
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            },
            '获取站点列表成功'
        )

    except Exception as e:
        return error_response(f'获取站点列表失败: {str(e)}', 500)

@station_bp.route('/create', methods=['POST'])
@admin_required()
@permission_required('station:edit')
def create_station():
    """
    创建站点（管理员功能）
    """
    try:
        data = request.get_json()

        required_fields = ['name', 'address', 'latitude', 'longitude']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field}不能为空', 400)

        name = data['name']
        address = data['address']
        latitude = data['latitude']
        longitude = data['longitude']
        phone = data.get('phone')
        business_hours = data.get('business_hours')
        capacity = data.get('capacity')

        success, result = StationService.create_station(
            name, address, latitude, longitude, phone, business_hours, capacity
        )

        if not success:
            return error_response(result, 400)

        return success_response(result, '站点创建成功')

    except Exception as e:
        return error_response(f'创建站点失败: {str(e)}', 500)

@station_bp.route('/<int:station_id>', methods=['PUT'])
@admin_required()
@permission_required('station:edit')
def update_station(station_id):
    """
    更新站点信息（管理员功能）
    """
    try:
        station = Station.query.filter_by(
            id=station_id, tenant_id=g.tenant_id, is_deleted=False
        ).first()

        if not station:
            return error_response('站点不存在', 404)

        data = request.get_json()

        # 可更新的字段
        updatable_fields = ['name', 'address', 'latitude', 'longitude', 'phone', 'business_hours', 'capacity']
        
        for field in updatable_fields:
            if field in data:
                setattr(station, field, data[field])

        station.save()

        return success_response(station.to_dict(), '站点更新成功')

    except Exception as e:
        return error_response(f'更新站点失败: {str(e)}', 500)

@station_bp.route('/<int:station_id>', methods=['DELETE'])
@admin_required()
@permission_required('station:delete')
def delete_station(station_id):
    """
    删除站点（管理员功能）
    """
    try:
        station = Station.query.filter_by(
            id=station_id, tenant_id=g.tenant_id, is_deleted=False
        ).first()

        if not station:
            return error_response('站点不存在', 404)

        station.is_deleted = True
        station.save()

        return success_response(None, '站点删除成功')

    except Exception as e:
        return error_response(f'删除站点失败: {str(e)}', 500)

@station_bp.route('/statistics', methods=['GET'])
@admin_required()
@permission_required('station:view')
def get_station_statistics():
    try:
        result = StationService.get_station_statistics()

        return success_response(result, '获取站点统计成功')

    except Exception as e:
        return error_response(f'获取站点统计失败: {str(e)}', 500)

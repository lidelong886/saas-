"""
推荐服务路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from ..utils.auth_helpers import get_current_user_id
from ..services.recommend_service import RecommendService
from ..utils.response import success_response, error_response

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/batteries', methods=['GET'])
@jwt_required()
def get_battery_recommendations():
    """
    获取推荐电池
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        user_id = get_current_user_id()

        batteries = RecommendService.get_user_recommendations(user_id, limit)

        return success_response({
            'batteries': batteries,
            'total': len(batteries)
        }, '获取推荐电池成功')

    except Exception as e:
        return error_response(f'获取推荐电池失败: {str(e)}', 500)

@recommend_bp.route('/stations', methods=['GET'])
@jwt_required()
def get_station_recommendations():
    """
    获取推荐站点
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        user_id = get_current_user_id()

        stations = RecommendService.get_station_recommendations(user_id, limit)

        return success_response({
            'stations': stations,
            'total': len(stations)
        }, '获取推荐站点成功')

    except Exception as e:
        return error_response(f'获取推荐站点失败: {str(e)}', 500)

@recommend_bp.route('/packages', methods=['GET'])
@jwt_required()
def get_package_recommendations():
    """
    获取推荐套餐
    """
    try:
        limit = request.args.get('limit', 3, type=int)
        user_id = get_current_user_id()

        packages = RecommendService.get_package_recommendations(user_id, limit)

        return success_response({
            'packages': packages,
            'total': len(packages)
        }, '获取推荐套餐成功')

    except Exception as e:
        return error_response(f'获取推荐套餐失败: {str(e)}', 500)

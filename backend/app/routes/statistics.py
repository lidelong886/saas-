"""
数据统计路由
"""
from flask import Blueprint, request, g
from ..services.statistics_service import StatisticsService
from ..utils.response import success_response, error_response
from ..utils.admin_auth import admin_required

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/revenue', methods=['GET'])
@admin_required()
def get_revenue_statistics():
    """
    获取营收统计（管理员功能）
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        period = request.args.get('period', 'month')

        result = StatisticsService.get_revenue_statistics(start_date, end_date, period)

        return success_response(result, '获取营收统计成功')

    except Exception as e:
        return error_response(f'获取营收统计失败: {str(e)}', 500)

@statistics_bp.route('/orders', methods=['GET'])
@admin_required()
def get_order_statistics():
    """
    获取订单统计（管理员功能）
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        result = StatisticsService.get_order_statistics(start_date, end_date)

        return success_response(result, '获取订单统计成功')

    except Exception as e:
        return error_response(f'获取订单统计失败: {str(e)}', 500)

@statistics_bp.route('/batteries', methods=['GET'])
@admin_required()
def get_battery_statistics():
    """
    获取电池统计（管理员功能）
    """
    try:
        result = StatisticsService.get_battery_statistics()

        return success_response(result, '获取电池统计成功')

    except Exception as e:
        return error_response(f'获取电池统计失败: {str(e)}', 500)

@statistics_bp.route('/users', methods=['GET'])
@admin_required()
def get_user_statistics():
    """
    获取用户统计（管理员功能）
    """
    try:
        result = StatisticsService.get_user_statistics()

        return success_response(result, '获取用户统计成功')

    except Exception as e:
        return error_response(f'获取用户统计失败: {str(e)}', 500)

@statistics_bp.route('/dashboard', methods=['GET'])
@admin_required()
def get_dashboard_summary():
    """
    获取仪表板摘要（管理员功能）
    """
    try:
        result = StatisticsService.get_dashboard_summary()

        return success_response(result, '获取仪表板数据成功')

    except Exception as e:
        return error_response(f'获取仪表板数据失败: {str(e)}', 500)

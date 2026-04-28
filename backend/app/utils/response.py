"""
统一响应格式工具
"""
from datetime import datetime
from flask import jsonify

def success_response(data=None, message='成功', code=200):
    """
    成功响应
    """
    response = {
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }
    return jsonify(response), code

def error_response(message, code=400, data=None):
    """
    错误响应
    """
    response = {
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }
    return jsonify(response), code

def paginate_response(items, pagination, message='获取成功'):
    """
    分页响应
    """
    # 支持字典和对象两种格式
    if isinstance(pagination, dict):
        page_info = {
            'page': pagination.get('page', 1),
            'per_page': pagination.get('per_page', 20),
            'total': pagination.get('total', 0),
            'pages': pagination.get('pages', 1),
            'has_next': pagination.get('has_next', False),
            'has_prev': pagination.get('has_prev', False)
        }
    else:
        page_info = {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    data = {
        'list': items,
        'pagination': page_info
    }
    return success_response(data, message)


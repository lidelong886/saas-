"""
消息通知路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from ..utils.auth_helpers import get_current_user_id
from ..models.notification import Notification
from ..utils.response import success_response, error_response, paginate_response
from .. import db

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/list', methods=['GET'])
@jwt_required()
def get_notifications():
    """获取通知列表"""
    try:
        user_id = get_current_user_id()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        noti_type = request.args.get('type')

        query = Notification.query.filter_by(
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        )

        if noti_type:
            query = query.filter_by(noti_type=noti_type)

        pagination = query.order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return paginate_response(
            [n.to_dict() for n in pagination.items],
            {
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            },
            '获取通知列表成功'
        )

    except Exception as e:
        return error_response(f'获取通知列表失败: {str(e)}', 500)


@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """获取未读通知数"""
    try:
        user_id = get_current_user_id()

        count = Notification.query.filter_by(
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_read=False,
            is_deleted=False
        ).count()

        return success_response({'count': count}, '获取未读数成功')

    except Exception as e:
        return error_response(f'获取未读数失败: {str(e)}', 500)


@notification_bp.route('/<int:noti_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(noti_id):
    """标记单条已读"""
    try:
        user_id = get_current_user_id()

        noti = Notification.query.filter_by(
            id=noti_id,
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not noti:
            return error_response('通知不存在', 404)

        noti.is_read = True
        noti.save()

        return success_response(None, '已标记为已读')

    except Exception as e:
        return error_response(f'标记已读失败: {str(e)}', 500)


@notification_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """全部标记已读"""
    try:
        user_id = get_current_user_id()

        Notification.query.filter_by(
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_read=False,
            is_deleted=False
        ).update({'is_read': True})

        db.session.commit()

        return success_response(None, '已全部标记为已读')

    except Exception as e:
        db.session.rollback()
        return error_response(f'全部标记已读失败: {str(e)}', 500)

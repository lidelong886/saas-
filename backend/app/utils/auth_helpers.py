"""
JWT 与当前用户辅助函数
"""
from flask_jwt_extended import get_jwt_identity


def get_current_user_id():
    """
    将 JWT identity 转为 int（User.id），与数据库整型主键一致。
    """
    uid = get_jwt_identity()
    if uid is None:
        return None
    try:
        return int(uid)
    except (TypeError, ValueError):
        return None

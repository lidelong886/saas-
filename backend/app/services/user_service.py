"""
用户服务
"""
from datetime import datetime, timedelta
import json
from ..models import User
from .. import redis_client

class UserService:
    """用户服务类"""

    @staticmethod
    def get_user_statistics(user_id):
        """
        获取用户统计信息
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return None

            # 计算统计信息
            stats = {
                'total_orders': len(user.orders),
                'active_orders': len([o for o in user.orders if o.status in ['rented', 'paid']]),
                'completed_orders': len([o for o in user.orders if o.status == 'completed']),
                'total_spent': sum(float(o.total_amount) for o in user.orders if o.status in ['completed', 'returned']),
                'registration_days': (datetime.now() - user.created_at).days,
                'last_login_days': (datetime.now() - user.last_login_at).days if user.last_login_at else None
            }

            return stats

        except Exception as e:
            print(f"[USER_STATS] 获取统计信息失败: {str(e)}")
            return None

    @staticmethod
    def update_user_activity(user_id, activity_type, data=None):
        """
        更新用户活动记录
        """
        try:
            key = f"user_activity:{user_id}"
            activity_record = {
                'type': activity_type,
                'timestamp': datetime.now().isoformat(),
                'data': data or {}
            }

            # 存储最近10条活动记录
            redis_client.lpush(key, json.dumps(activity_record, ensure_ascii=False))
            redis_client.ltrim(key, 0, 9)  # 只保留最新的10条
            redis_client.expire(key, 86400 * 30)  # 30天过期

            return True

        except Exception as e:
            print(f"[USER_ACTIVITY] 更新活动记录失败: {str(e)}")
            return False

    @staticmethod
    def get_user_activity_history(user_id, limit=10):
        """
        获取用户活动历史
        """
        try:
            key = f"user_activity:{user_id}"
            activities = redis_client.lrange(key, 0, limit - 1)

            result = []
            for activity in activities:
                try:
                    result.append(json.loads(activity))
                except:
                    continue

            return result

        except Exception as e:
            print(f"[USER_ACTIVITY] 获取活动历史失败: {str(e)}")
            return []

    @staticmethod
    def check_user_risk_level(user_id):
        """
        检查用户风险等级
        基于订单行为、逾期记录等计算风险等级
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return 'unknown'

            risk_score = 0

            # 检查逾期订单
            overdue_orders = [o for o in user.orders if o.is_overdue()]
            risk_score += len(overdue_orders) * 10

            # 检查取消率
            total_orders = len(user.orders)
            if total_orders > 0:
                cancelled_orders = len([o for o in user.orders if o.status == 'cancelled'])
                cancel_rate = cancelled_orders / total_orders
                risk_score += cancel_rate * 20

            # 检查注册时间（新用户风险较高）
            registration_days = (datetime.now() - user.created_at).days
            if registration_days < 7:
                risk_score += 15
            elif registration_days < 30:
                risk_score += 5

            # 根据风险分数确定等级
            if risk_score >= 50:
                return 'high'
            elif risk_score >= 20:
                return 'medium'
            else:
                return 'low'

        except Exception as e:
            print(f"[USER_RISK] 检查风险等级失败: {str(e)}")
            return 'unknown'

    @staticmethod
    def send_notification(user_id, notification_type, title, content, data=None):
        """
        发送用户通知
        """
        try:
            notification = {
                'type': notification_type,
                'title': title,
                'content': content,
                'data': data or {},
                'timestamp': datetime.now().isoformat(),
                'read': False
            }

            key = f"user_notifications:{user_id}"
            redis_client.lpush(key, json.dumps(notification, ensure_ascii=False))
            redis_client.expire(key, 86400 * 30)  # 30天过期

            # 如果用户有推送令牌，这里可以发送推送通知
            user = User.get_by_id(user_id)
            if user and user.push_token:
                # 调用推送服务
                UserService._send_push_notification(user.push_token, title, content)

            return True

        except Exception as e:
            print(f"[NOTIFICATION] 发送通知失败: {str(e)}")
            return False

    @staticmethod
    def get_user_notifications(user_id, page=1, per_page=20):
        """
        获取用户通知列表
        """
        try:
            key = f"user_notifications:{user_id}"
            start = (page - 1) * per_page
            end = start + per_page - 1

            notifications = redis_client.lrange(key, start, end)

            result = []
            for notification in notifications:
                try:
                    result.append(json.loads(notification))
                except:
                    continue

            return result

        except Exception as e:
            print(f"[NOTIFICATION] 获取通知失败: {str(e)}")
            return []

    @staticmethod
    def mark_notification_read(user_id, notification_index):
        """
        标记通知为已读
        """
        try:
            key = f"user_notifications:{user_id}"
            notification = redis_client.lindex(key, notification_index)

            if notification:
                notification_data = json.loads(notification)
                notification_data['read'] = True
                redis_client.lset(key, notification_index, json.dumps(notification_data, ensure_ascii=False))

            return True

        except Exception as e:
            print(f"[NOTIFICATION] 标记已读失败: {str(e)}")
            return False

    @staticmethod
    def _send_push_notification(push_token, title, content):
        """
        发送推送通知（需要集成推送服务）
        """
        try:
            # 这里应该调用具体的推送服务，如极光推送、腾讯信鸽等
            print(f"[PUSH] 发送推送通知到 {push_token}: {title} - {content}")

            # 示例代码：
            # import requests
            # response = requests.post('https://api.push-service.com/send', json={
            #     'token': push_token,
            #     'title': title,
            #     'content': content
            # })

        except Exception as e:
            print(f"[PUSH] 推送通知失败: {str(e)}")


"""
通知服务
"""
from ..models.notification import Notification
from flask import g


class NotificationService:
    """通知服务 - 创建业务通知"""

    @staticmethod
    def create(user_id, noti_type, title, content, link_type=None, link_id=None):
        """创建一条通知"""
        noti = Notification(
            user_id=user_id,
            noti_type=noti_type,
            title=title,
            content=content,
            link_type=link_type,
            link_id=link_id
        )
        noti.save()
        return noti

    @staticmethod
    def on_exchange_success(user_id, record_no, station_name=None):
        """换电成功通知"""
        station_text = f'（{station_name}）' if station_name else ''
        NotificationService.create(
            user_id=user_id,
            noti_type='exchange',
            title='换电成功',
            content=f'您已成功完成换电{station_text}，记录号：{record_no}',
            link_type='exchange',
            link_id=record_no
        )

    @staticmethod
    def on_order_completed(user_id, order_no):
        """订单完成通知"""
        NotificationService.create(
            user_id=user_id,
            noti_type='order',
            title='订单已完成',
            content=f'您的订单 {order_no} 已完成，感谢使用！',
            link_type='order',
            link_id=order_no
        )

    @staticmethod
    def on_fault_report_update(user_id, report_no, status):
        """报修状态更新通知"""
        status_map = {
            'processing': '处理中',
            'resolved': '已解决',
            'closed': '已关闭'
        }
        status_text = status_map.get(status, status)
        NotificationService.create(
            user_id=user_id,
            noti_type='fault',
            title='报修进度更新',
            content=f'您的报修工单 {report_no} 状态已更新为：{status_text}',
            link_type='fault',
            link_id=report_no
        )

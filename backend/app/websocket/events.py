"""
WebSocket事件处理
"""
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from .. import socketio
import logging

logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect(auth):
    """客户端连接"""
    try:
        if auth and 'token' in auth:
            token = auth['token']
            decoded = decode_token(token)
            user_id = decoded['sub']
            logger.info(f'用户 {user_id} 已连接 WebSocket')
            emit('connected', {'status': 'success', 'message': '连接成功'})
        else:
            logger.warning('WebSocket 连接缺少认证令牌')
            emit('connected', {'status': 'warning', 'message': '未认证连接'})
    except Exception as e:
        logger.error(f'WebSocket 连接错误: {str(e)}')
        emit('error', {'message': '连接失败'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开"""
    logger.info('客户端断开 WebSocket 连接')

@socketio.on('join')
def handle_join(data):
    """加入房间（用于订阅特定数据）"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('joined', {'room': room}, room=room)
        logger.info(f'客户端加入房间: {room}')

@socketio.on('leave')
def handle_leave(data):
    """离开房间"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('left', {'room': room}, room=room)
        logger.info(f'客户端离开房间: {room}')

def emit_battery_status_change(battery_data):
    """推送电池状态变化"""
    socketio.emit('battery_status_change', battery_data, namespace='/')

def emit_order_update(order_data):
    """推送订单更新"""
    socketio.emit('order_update', order_data, namespace='/')

def emit_station_alert(station_data):
    """推送站点告警"""
    socketio.emit('station_alert', station_data, namespace='/')

def emit_realtime_stats(stats_data):
    """推送实时统计数据"""
    socketio.emit('realtime_stats', stats_data, namespace='/')

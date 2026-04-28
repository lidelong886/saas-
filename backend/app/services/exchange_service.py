"""
换电服务
"""
from datetime import datetime, timedelta
from flask import g
from ..models import Battery, ExchangeRecord, User, Order
from .. import db

class ExchangeService:
    """换电服务类"""

    @staticmethod
    def exchange_battery(user_id, old_battery_id, new_battery_id, station_id, cabinet_id, latitude=None, longitude=None):
        """
        执行换电操作

        Args:
            user_id: 用户ID
            old_battery_id: 旧电池ID
            new_battery_id: 新电池ID
            station_id: 站点ID
            cabinet_id: 柜子ID
            latitude: 纬度
            longitude: 经度

        Returns:
            (success, result/error_message)
        """
        try:
            # 验证用户
            user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not user:
                return False, "用户不存在"

            # 以当前真实租用中的电池为准，避免前端缓存旧电池ID导致误判
            current_rented_batteries = Battery.query.filter_by(
                current_user_id=user_id,
                status='rented',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).order_by(Battery.id.desc()).all()

            if not current_rented_batteries:
                return False, "您当前没有正在租用的电池，无法换电"
            
            # 如果前端传了旧电池ID，尝试匹配
            old_battery = None
            if old_battery_id:
                for b in current_rented_batteries:
                    if int(b.id) == int(old_battery_id):
                        old_battery = b
                        break
                        
            # 如果没传或没匹配到，且名下有多块电池，拒绝操作
            if not old_battery:
                if len(current_rented_batteries) > 1:
                    return False, "检测到您名下存在多块租用中的电池，请先在订单列表中选择要换的电池"
                old_battery = current_rented_batteries[0]
            
            old_battery_id = old_battery.id

            # 验证新电池
            new_battery = Battery.query.filter_by(id=new_battery_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not new_battery:
                return False, "新电池不存在"
            if int(new_battery.id) == int(old_battery.id):
                return False, "新旧电池不能相同"

            # 检查新电池是否可用
            if not new_battery.is_available():
                return False, "新电池不可用"

            rented_order = Order.query.filter_by(
                user_id=user_id,
                battery_id=old_battery.id,
                status='rented',
                tenant_id=g.tenant_id,
                is_deleted=False
            ).order_by(Order.id.desc()).first()
            if not rented_order:
                rented_order = Order.query.filter_by(
                    user_id=user_id,
                    status='rented',
                    tenant_id=g.tenant_id,
                    is_deleted=False
                ).order_by(Order.id.desc()).first()

            # 创建换电记录
            exchange_record = ExchangeRecord(
                record_no=f"EX{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id:04d}",
                user_id=user_id,
                order_id=rented_order.id if rented_order else None,
                old_battery_id=old_battery.id,
                new_battery_id=new_battery_id,
                station_id=station_id,
                cabinet_id=cabinet_id,
                tenant_id=g.tenant_id
            )

            now = datetime.now()

            # 更新旧电池状态：回收到当前换电站/电柜
            old_battery.current_user_id = None
            old_battery.status = 'available'
            old_battery.current_station_id = station_id
            old_battery.current_cabinet_id = cabinet_id
            old_battery.expected_return_at = None
            old_battery.last_return_time = now

            # 更新新电池状态：交付给用户
            new_battery.current_user_id = user_id
            new_battery.status = 'rented'
            new_battery.current_station_id = None
            new_battery.current_cabinet_id = None
            new_battery.rented_at = now
            new_battery.expected_return_at = now + timedelta(hours=24)
            new_battery.last_rent_time = now

            if rented_order:
                rented_order.battery_id = new_battery.id
                rented_order.station_id = station_id
                rented_order.cabinet_id = cabinet_id
                rented_order.return_latitude = latitude
                rented_order.return_longitude = longitude

            db.session.add(exchange_record)
            db.session.commit()

            return True, {
                'exchange_record_id': exchange_record.id,
                'order_id': rented_order.id if rented_order else None,
                'order_status': rented_order.status if rented_order else None,
                'old_battery_id': old_battery.id,
                'old_battery_code': old_battery.battery_code,
                'new_battery_id': new_battery.id,
                'new_battery_code': new_battery.battery_code,
                'exchange_time': exchange_record.created_at.isoformat(),
                'new_battery_power': new_battery.power_level,
                'exchange_fee': float(exchange_record.exchange_fee or 0),
                'station_id': station_id,
                'cabinet_id': cabinet_id,
                'new_battery': {
                    'id': new_battery.id,
                    'battery_code': new_battery.battery_code,
                    'model': new_battery.model,
                    'power_level': new_battery.power_level,
                    'voltage': float(new_battery.voltage) if new_battery.voltage else None,
                    'rented_at': new_battery.rented_at.isoformat() if new_battery.rented_at else None,
                }
            }

        except Exception as e:
            db.session.rollback()
            return False, f"换电失败: {str(e)}"

    @staticmethod
    def get_exchange_history(user_id, page=1, per_page=20):
        """
        获取用户换电历史
        
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
        
        Returns:
            分页结果
        """
        try:
            pagination = ExchangeRecord.query.filter_by(
                user_id=user_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).order_by(ExchangeRecord.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return {
                'items': [record.to_dict() for record in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

        except Exception as e:
            return {
                'items': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0,
                'error': str(e)
            }

    @staticmethod
    def get_exchange_statistics(start_date=None, end_date=None):
        """
        获取换电统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            统计数据
        """
        try:
            query = ExchangeRecord.query.filter_by(
                tenant_id=g.tenant_id,
                is_deleted=False
            )

            if start_date:
                query = query.filter(ExchangeRecord.created_at >= start_date)
            if end_date:
                query = query.filter(ExchangeRecord.created_at <= end_date)

            total_exchanges = query.count()
            
            # 获取最活跃的用户
            from sqlalchemy import func
            active_users = db.session.query(
                ExchangeRecord.user_id,
                func.count(ExchangeRecord.id).label('exchange_count')
            ).filter(
                ExchangeRecord.tenant_id == g.tenant_id,
                ExchangeRecord.is_deleted == False
            ).group_by(ExchangeRecord.user_id).order_by(
                func.count(ExchangeRecord.id).desc()
            ).limit(10).all()

            return {
                'total_exchanges': total_exchanges,
                'active_users': [
                    {'user_id': user_id, 'exchange_count': count}
                    for user_id, count in active_users
                ]
            }

        except Exception as e:
            return {
                'total_exchanges': 0,
                'active_users': [],
                'error': str(e)
            }

"""
数据统计服务
"""
from datetime import datetime, timedelta
from flask import g, request
from flask_jwt_extended import get_jwt
from ..models import Order, User, Battery, ExchangeRecord, Payment, Station
from .. import db
from sqlalchemy import func, case

class StatisticsService:
    """数据统计服务类"""

    @staticmethod
    def _is_global_admin_scope():
        try:
            claims = get_jwt()
        except Exception:
            claims = {}
        return bool(claims.get('is_super_admin')) or getattr(g, 'tenant_id', 1) == 1

    @staticmethod
    def _scoped_query(model):
        query = model.query.filter_by(is_deleted=False)
        if StatisticsService._is_global_admin_scope():
            tenant_id = request.args.get('tenant_id', type=int)
            if tenant_id:
                query = query.filter(model.tenant_id == tenant_id)
        else:
            query = query.filter(model.tenant_id == g.tenant_id)
        return query

    @staticmethod
    def _apply_scope(query, model):
        query = query.filter(model.is_deleted == False)
        if StatisticsService._is_global_admin_scope():
            tenant_id = request.args.get('tenant_id', type=int)
            if tenant_id:
                query = query.filter(model.tenant_id == tenant_id)
        else:
            query = query.filter(model.tenant_id == g.tenant_id)
        return query

    @staticmethod
    def get_revenue_statistics(start_date=None, end_date=None, period='day'):
        """
        获取营收统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            period: 统计周期 (day/week/month/year)
        
        Returns:
            营收统计数据
        """
        try:
            if not start_date:
                if period == 'day':
                    start_date = datetime.now().date()
                elif period == 'week':
                    start_date = (datetime.now() - timedelta(days=7)).date()
                elif period == 'month':
                    start_date = (datetime.now() - timedelta(days=30)).date()
                else:  # year
                    start_date = (datetime.now() - timedelta(days=365)).date()

            if not end_date:
                end_date = datetime.now().date()

            # 获取完成的订单
            completed_orders = StatisticsService._apply_scope(Order.query, Order).filter(
                Order.status == 'completed',
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).all()

            total_revenue = sum(float(order.total_amount or 0) for order in completed_orders)
            order_count = len(completed_orders)

            # 按日期分组统计
            daily_stats = {}
            for order in completed_orders:
                date_key = order.created_at.strftime('%Y-%m-%d')
                if date_key not in daily_stats:
                    daily_stats[date_key] = {'revenue': 0, 'count': 0}
                daily_stats[date_key]['revenue'] += float(order.total_amount or 0)
                daily_stats[date_key]['count'] += 1

            return {
                'total_revenue': round(total_revenue, 2),
                'order_count': order_count,
                'average_order_value': round(total_revenue / order_count, 2) if order_count > 0 else 0,
                'daily_stats': daily_stats,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }

        except Exception as e:
            return {
                'total_revenue': 0,
                'order_count': 0,
                'average_order_value': 0,
                'daily_stats': {},
                'error': str(e)
            }

    @staticmethod
    def get_order_statistics(start_date=None, end_date=None):
        """
        获取订单统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            订单统计数据
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).date()
            if not end_date:
                end_date = datetime.now().date()

            query = StatisticsService._apply_scope(Order.query, Order).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )

            total_orders = query.count()
            pending_orders = query.filter_by(status='pending').count()
            paid_orders = query.filter_by(status='paid').count()
            rented_orders = query.filter_by(status='rented').count()
            completed_orders = query.filter_by(status='completed').count()
            cancelled_orders = query.filter_by(status='cancelled').count()

            # 按订单类型统计
            rental_orders = query.filter_by(order_type='rental').count()
            purchase_orders = query.filter_by(order_type='purchase').count()
            exchange_orders = query.filter_by(order_type='exchange').count()

            return {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'paid_orders': paid_orders,
                'rented_orders': rented_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'by_type': {
                    'rental': rental_orders,
                    'purchase': purchase_orders,
                    'exchange': exchange_orders
                },
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }

        except Exception as e:
            return {
                'total_orders': 0,
                'pending_orders': 0,
                'paid_orders': 0,
                'rented_orders': 0,
                'completed_orders': 0,
                'cancelled_orders': 0,
                'by_type': {},
                'error': str(e)
            }

    @staticmethod
    def get_battery_statistics():
        """
        获取电池统计
        
        Returns:
            电池统计数据
        """
        try:
            battery_query = StatisticsService._scoped_query(Battery)
            total_batteries = battery_query.count()

            available_batteries = StatisticsService._scoped_query(Battery).filter(Battery.status == 'available').count()

            rented_batteries = StatisticsService._scoped_query(Battery).filter(Battery.status.in_(['rented', 'in_use', 'charging'])).count()

            maintenance_batteries = StatisticsService._scoped_query(Battery).filter(Battery.status == 'maintenance').count()
            offline_batteries = StatisticsService._scoped_query(Battery).filter(Battery.status.in_(['offline', 'scrapped'])).count()

            # 计算使用率
            utilization_rate = (rented_batteries / total_batteries * 100) if total_batteries > 0 else 0

            # 获取电池平均电量
            avg_power = StatisticsService._apply_scope(
                db.session.query(func.avg(Battery.power_level)),
                Battery
            ).scalar() or 0

            return {
                'total_batteries': total_batteries,
                'available_batteries': available_batteries,
                'rented_batteries': rented_batteries,
                'maintenance_batteries': maintenance_batteries,
                'offline_batteries': offline_batteries,
                'utilization_rate': round(utilization_rate, 2),
                'average_power_level': round(float(avg_power), 2)
            }

        except Exception as e:
            return {
                'total_batteries': 0,
                'available_batteries': 0,
                'rented_batteries': 0,
                'maintenance_batteries': 0,
                'offline_batteries': 0,
                'utilization_rate': 0,
                'average_power_level': 0,
                'error': str(e)
            }

    @staticmethod
    def get_user_statistics():
        """
        获取用户统计
        
        Returns:
            用户统计数据
        """
        try:
            user_query = StatisticsService._scoped_query(User)
            total_users = user_query.count()

            active_users = StatisticsService._scoped_query(User).filter(
                User.last_login_at >= datetime.now() - timedelta(days=30),
            ).count()

            verified_users = StatisticsService._scoped_query(User).filter(User.is_verified == True).count()

            # 获取新用户（最近7天）
            new_users = StatisticsService._scoped_query(User).filter(
                User.created_at >= datetime.now() - timedelta(days=7),
            ).count()

            return {
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'new_users': new_users,
                'verification_rate': round(verified_users / total_users * 100, 2) if total_users > 0 else 0
            }

        except Exception as e:
            return {
                'total_users': 0,
                'active_users': 0,
                'verified_users': 0,
                'new_users': 0,
                'verification_rate': 0,
                'error': str(e)
            }

    @staticmethod
    def get_dashboard_summary():
        try:
            today = datetime.now().date()
            this_month = today.replace(day=1)

            today_orders = StatisticsService._scoped_query(Order).filter(
                Order.created_at >= today,
            ).count()
            total_orders = StatisticsService._scoped_query(Order).count()

            today_revenue = StatisticsService._apply_scope(
                db.session.query(func.sum(Order.total_amount)),
                Order
            ).filter(
                Order.status == 'completed',
                Order.created_at >= today
            ).scalar() or 0
            month_revenue = StatisticsService._apply_scope(
                db.session.query(func.sum(Order.total_amount)),
                Order
            ).filter(
                Order.status == 'completed',
                Order.created_at >= this_month
            ).scalar() or 0

            station_query = StatisticsService._scoped_query(Station)
            station_total = station_query.count()
            station_active = StatisticsService._scoped_query(Station).filter(Station.status == 'active').count()
            station_stats = {
                'total_stations': station_total,
                'active_stations': station_active,
                'inactive_stations': max(station_total - station_active, 0)
            }

            station_usage_query = db.session.query(
                Station.name,
                func.count(Battery.id).label('total'),
                func.sum(case((Battery.status.in_(['rented', 'in_use', 'charging']), 1), else_=0)).label('busy')
            ).outerjoin(
                Battery,
                (Battery.current_station_id == Station.id) & (Battery.is_deleted == False)
            )
            station_usage_rows = StatisticsService._apply_scope(
                station_usage_query,
                Station
            ).group_by(Station.id, Station.name).all()
            station_usage = []
            for row in station_usage_rows:
                total = int(row.total or 0)
                busy = int(row.busy or 0)
                station_usage.append({
                    'name': row.name,
                    'usage_rate': round(busy / total * 100, 1) if total else 0
                })
            station_usage = sorted(station_usage, key=lambda x: x['usage_rate'], reverse=True)[:5]

            battery_stats = StatisticsService.get_battery_statistics()
            user_stats = StatisticsService.get_user_statistics()

            revenue_trend = []
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                daily_revenue = StatisticsService._apply_scope(
                    db.session.query(func.sum(Order.total_amount)),
                    Order
                ).filter(
                    Order.status == 'completed',
                    func.date(Order.created_at) == date
                ).scalar() or 0
                revenue_trend.append(round(float(daily_revenue), 2))

            order_trend = []
            for i in range(29, -1, -1):
                date = today - timedelta(days=i)
                daily_orders = StatisticsService._scoped_query(Order).filter(
                    func.date(Order.created_at) == date,
                ).count()
                order_trend.append(daily_orders)

            return {
                'today_orders': today_orders,
                'total_orders': total_orders,
                'today_revenue': round(float(today_revenue), 2),
                'month_revenue': round(float(month_revenue), 2),
                'battery_stats': battery_stats,
                'station_stats': station_stats,
                'station_usage': station_usage,
                'user_stats': user_stats,
                'revenue_trend': revenue_trend,
                'order_trend': order_trend,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'today_orders': 0,
                'total_orders': 0,
                'today_revenue': 0,
                'month_revenue': 0,
                'battery_stats': {},
                'station_stats': {},
                'station_usage': [],
                'user_stats': {},
                'revenue_trend': [0] * 7,
                'order_trend': [0] * 30,
                'error': str(e)
            }

"""
推荐服务
"""
from datetime import datetime, timedelta
from flask import g
from ..models import User, Order, Battery, ExchangeRecord, Package, Station, UserPackage
from .. import db
from sqlalchemy import func

class RecommendService:
    """推荐服务类"""

    @staticmethod
    def get_user_recommendations(user_id, limit=10):
        """
        获取用户推荐电池 (不再使用协同过滤，直接返回最近热门或所有可用电池)
        """
        try:
            return RecommendService._get_popular_batteries(limit)
        except Exception as e:
            print(f"获取推荐失败: {str(e)}")
            return []

    @staticmethod
    def _get_popular_batteries(limit=10):
        """
        获取热门电池（简单冷启动推荐）
        """
        try:
            # 获取最近30天租赁最多的电池
            thirty_days_ago = datetime.now() - timedelta(days=30)

            popular_battery_ids = db.session.query(Order.battery_id).filter(
                Order.battery_id.isnot(None),
                Order.created_at >= thirty_days_ago,
                Order.tenant_id == g.tenant_id,
                Order.is_deleted == False
            ).group_by(Order.battery_id).order_by(
                func.count(Order.id).desc()
            ).limit(limit).all()

            battery_ids = [b[0] for b in popular_battery_ids]

            if not battery_ids:
                # 如果没有历史数据，返回所有可用电池
                batteries = Battery.query.filter_by(
                    status='available',
                    tenant_id=g.tenant_id,
                    is_deleted=False
                ).limit(limit).all()
            else:
                batteries = Battery.query.filter(
                    Battery.id.in_(battery_ids),
                    Battery.tenant_id == g.tenant_id,
                    Battery.is_deleted == False
                ).all()

            return [battery.to_dict() for battery in batteries]

        except Exception as e:
            print(f"获取热门电池失败: {str(e)}")
            return []

    @staticmethod
    def get_station_recommendations(user_id, limit=5):
        """
        获取用户推荐站点
        """
        try:
            user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id, is_deleted=False).first()
            if not user:
                return []

            # 如果用户有位置信息，推荐附近的站点
            if user.latitude and user.longitude:
                from .station_service import StationService
                return StationService.get_nearby_stations(
                    float(user.latitude),
                    float(user.longitude),
                    radius_km=10
                )[:limit]

            # 否则推荐热门站点
            return RecommendService._get_popular_stations(limit)

        except Exception as e:
            print(f"获取站点推荐失败: {str(e)}")
            return []

    @staticmethod
    def _get_popular_stations(limit=5):
        """获取热门站点"""
        try:
            # 获取最近30天换电最多的站点
            thirty_days_ago = datetime.now() - timedelta(days=30)

            popular_station_ids = db.session.query(ExchangeRecord.station_id).filter(
                ExchangeRecord.station_id.isnot(None),
                ExchangeRecord.created_at >= thirty_days_ago,
                ExchangeRecord.tenant_id == g.tenant_id,
                ExchangeRecord.is_deleted == False
            ).group_by(ExchangeRecord.station_id).order_by(
                func.count(ExchangeRecord.id).desc()
            ).limit(limit).all()

            station_ids = [s[0] for s in popular_station_ids]

            if not station_ids:
                stations = Station.query.filter_by(
                    tenant_id=g.tenant_id,
                    is_deleted=False
                ).limit(limit).all()
            else:
                stations = Station.query.filter(
                    Station.id.in_(station_ids),
                    Station.tenant_id == g.tenant_id,
                    Station.is_deleted == False
                ).all()

            return [station.to_dict() for station in stations]

        except Exception as e:
            print(f"获取热门站点失败: {str(e)}")
            return []

    @staticmethod
    def get_package_recommendations(user_id, limit=3):
        """
        获取用户推荐套餐 (基于用户购买记录的协同过滤 UBCF)
        """
        try:
            # 获取用户已经购买过的套餐ID
            user_packages = UserPackage.query.filter_by(
                user_id=user_id,
                tenant_id=g.tenant_id,
                is_deleted=False
            ).all()

            purchased_package_ids = [up.package_id for up in user_packages if up.package_id]

            if not purchased_package_ids:
                # 冷启动：推荐最受欢迎的套餐
                return RecommendService._get_popular_packages(limit)

            # 协同过滤核心：找到购买过相同套餐的其他用户 (找相似用户)
            similar_users_query = db.session.query(
                UserPackage.user_id,
                func.count(UserPackage.id).label('similarity')
            ).filter(
                UserPackage.package_id.in_(purchased_package_ids),
                UserPackage.user_id != user_id,
                UserPackage.tenant_id == g.tenant_id,
                UserPackage.is_deleted == False
            ).group_by(
                UserPackage.user_id
            ).order_by(
                func.count(UserPackage.id).desc()
            ).limit(20).all()

            similar_user_ids = [u.user_id for u in similar_users_query]

            if not similar_user_ids:
                return RecommendService._get_popular_packages(limit)

            # 获取这些相似用户购买过的，但当前用户没买过的套餐，按照购买频次排序
            recommended_packages_query = db.session.query(
                UserPackage.package_id
            ).filter(
                UserPackage.user_id.in_(similar_user_ids),
                ~UserPackage.package_id.in_(purchased_package_ids),
                UserPackage.package_id.isnot(None),
                UserPackage.tenant_id == g.tenant_id,
                UserPackage.is_deleted == False
            ).group_by(
                UserPackage.package_id
            ).order_by(
                func.count(UserPackage.id).desc()
            ).limit(limit).all()

            package_ids = [p[0] for p in recommended_packages_query]

            if not package_ids:
                return RecommendService._get_popular_packages(limit)

            # 获取套餐详情并保证是上架状态
            packages = Package.query.filter(
                Package.id.in_(package_ids),
                Package.is_active == True,
                Package.tenant_id == g.tenant_id,
                Package.is_deleted == False
            ).all()

            if not packages:
                return RecommendService._get_popular_packages(limit)

            return [p.to_dict() for p in packages]

        except Exception as e:
            print(f"获取套餐协同过滤推荐失败: {str(e)}")
            return RecommendService._get_popular_packages(limit)

    @staticmethod
    def _get_popular_packages(limit=3):
        """
        获取热门套餐（作为协同过滤冷启动策略）
        """
        try:
            # 统计最近购买最多的套餐
            thirty_days_ago = datetime.now() - timedelta(days=30)
            popular_package_ids = db.session.query(
                UserPackage.package_id
            ).filter(
                UserPackage.package_id.isnot(None),
                UserPackage.created_at >= thirty_days_ago,
                UserPackage.tenant_id == g.tenant_id,
                UserPackage.is_deleted == False
            ).group_by(
                UserPackage.package_id
            ).order_by(
                func.count(UserPackage.id).desc()
            ).limit(limit).all()

            package_ids = [p[0] for p in popular_package_ids]

            if not package_ids:
                packages = Package.query.filter_by(
                    tenant_id=g.tenant_id,
                    is_active=True,
                    is_deleted=False
                ).order_by(Package.created_at.desc()).limit(limit).all()
            else:
                # 补充可能不够的数量
                packages = Package.query.filter(
                    Package.id.in_(package_ids),
                    Package.is_active == True,
                    Package.tenant_id == g.tenant_id,
                    Package.is_deleted == False
                ).all()

                # 如果数量不足，用最新的补齐
                if len(packages) < limit:
                    existing_ids = [p.id for p in packages]
                    more_packages = Package.query.filter(
                        ~Package.id.in_(existing_ids),
                        Package.is_active == True,
                        Package.tenant_id == g.tenant_id,
                        Package.is_deleted == False
                    ).order_by(Package.created_at.desc()).limit(limit - len(packages)).all()
                    packages.extend(more_packages)

            return [p.to_dict() for p in packages[:limit]]

        except Exception as e:
            print(f"获取热门套餐失败: {str(e)}")
            return []

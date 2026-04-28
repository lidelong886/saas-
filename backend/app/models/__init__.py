"""
数据库模型包初始化
"""
from .base import BaseModel
from .user import User
from .battery import Battery
from .station import Station
from .cabinet import Cabinet, CabinetStatus
from .order import Order
from .payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from .tenant import Tenant
from .tenant_application import TenantApplication
from .rbac import AdminUser, Role, Permission, admin_user_roles, role_permissions
from .package import Package
from .user_package import UserPackage
from .wallet_transaction import WalletTransaction
from .exchange_record import ExchangeRecord
from .operation_log import OperationLog
from .system_config import SystemConfig
from .fault_report import FaultReport
from .notification import Notification
from .rider_reservation import RiderReservation
from .user_behavior_log import UserBehaviorLog

__all__ = [
    'BaseModel',
    'Tenant',
    'TenantApplication',
    'User',
    'AdminUser',
    'Role',
    'Permission',
    'admin_user_roles',
    'role_permissions',
    'Battery',
    'Station',
    'Cabinet',
    'CabinetStatus',
    'Order',
    'Payment',
    'PaymentType',
    'PaymentMethod',
    'PaymentStatus',
    'Package',
    'UserPackage',
    'WalletTransaction',
    'ExchangeRecord',
    'OperationLog',
    'SystemConfig',
    'FaultReport',
    'Notification',
    'RiderReservation',
    'UserBehaviorLog'
]

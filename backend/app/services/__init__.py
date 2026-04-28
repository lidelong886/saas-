"""
服务包初始化
"""

from .auth_service import AuthService
from .battery_service import BatteryService
from .order_service import OrderService
from .payment_service import PaymentService
from .recommend_service import RecommendService
from .user_service import UserService
from .wallet_service import WalletService
from .exchange_service import ExchangeService
from .admin_auth_service import AdminAuthService

__all__ = [
    'AuthService',
    'BatteryService',
    'OrderService',
    'PaymentService',
    'RecommendService',
    'UserService',
    'WalletService',
    'ExchangeService',
    'AdminAuthService'
]

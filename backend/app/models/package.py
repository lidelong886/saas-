"""
套餐模型
"""
from .base import BaseModel
from .. import db


class Package(BaseModel):
    """套餐模型"""
    __tablename__ = 'packages'

    name = db.Column(db.String(100), nullable=False, comment='套餐名称')
    package_type = db.Column(db.String(20), default='rental', comment='套餐类型 rental/purchase/exchange/rider_unlimited')
    battery_model = db.Column(db.String(100), comment='适配电池型号')
    hours = db.Column(db.Integer, default=24, comment='时长')
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='套餐价格')
    deposit_amount = db.Column(db.Numeric(10, 2), default=0.00, comment='押金')
    exchange_fee = db.Column(db.Numeric(10, 2), default=0.00, comment='换电费用')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    description = db.Column(db.String(255), comment='描述')
    rider_exclusive = db.Column(db.Boolean, default=False, comment='是否为骑手专属套餐')
    validity_days = db.Column(db.Integer, comment='有效天数（骑手套餐用）')

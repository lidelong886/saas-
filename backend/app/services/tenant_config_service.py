"""
租户级运营配置
"""
from .. import db
from ..models.system_config import SystemConfig


class TenantConfigService:
    DEFAULTS = {
        'rental_price_per_hour': 0.5,
        'overtime_rate': 1.5,
        'deposit_amount': 50.0,
        'order_timeout_minutes': 15,
        'exchange_fee': 3.0,
    }

    @staticmethod
    def key(tenant_id, field):
        return f'tenant:{tenant_id}:{field}'

    @classmethod
    def get_value(cls, tenant_id, field):
        default = cls.DEFAULTS[field]
        record = SystemConfig.query.filter_by(key=cls.key(tenant_id, field)).first()
        raw = record.value if record else default
        try:
            if field == 'order_timeout_minutes':
                return max(int(raw), 1)
            return max(float(raw), 0)
        except (TypeError, ValueError):
            return default

    @classmethod
    def get_settings(cls, tenant_id):
        return {field: cls.get_value(tenant_id, field) for field in cls.DEFAULTS}

    @classmethod
    def set_settings(cls, tenant_id, data):
        for field in cls.DEFAULTS:
            if field not in data:
                continue
            value = cls.get_value_from_payload(field, data.get(field))
            key = cls.key(tenant_id, field)
            record = SystemConfig.query.filter_by(key=key).first()
            if record:
                record.value = str(value)
                record.description = '租户级运营配置'
            else:
                db.session.add(SystemConfig(key=key, value=str(value), description='租户级运营配置'))

    @classmethod
    def get_value_from_payload(cls, field, raw):
        if field == 'order_timeout_minutes':
            return max(int(raw or cls.DEFAULTS[field]), 1)
        return max(round(float(raw or 0), 2), 0)

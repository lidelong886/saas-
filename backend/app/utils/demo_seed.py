"""
Demo data bootstrap for local/Docker defense runs.
"""
from .. import db
from ..models import AdminUser, Battery, Package, Station, Tenant, User


def ensure_demo_data(app=None):
    """Create minimal demo data when the database is empty."""
    default_tenant = Tenant.query.filter_by(id=1, is_deleted=False).first()
    if not default_tenant:
        default_tenant = Tenant(
            name='默认运营商',
            code='DEFAULT',
            contact_name='系统管理员',
            contact_phone='13800000000',
            contact_email='admin@example.com',
            status='active',
            tenant_id=1,
        )
        db.session.add(default_tenant)
        db.session.flush()
        default_tenant.tenant_id = default_tenant.id

    admin = AdminUser.query.filter_by(username='admin', is_deleted=False).first()
    if not admin:
        admin = AdminUser(
            username='admin',
            phone='admin',
            email='admin@example.com',
            nickname='系统管理员',
            is_active=True,
            is_super_admin=True,
            tenant_id=default_tenant.id,
        )
        admin.password = 'admin123'
        db.session.add(admin)

    if not User.query.filter_by(phone='13800000001', tenant_id=default_tenant.id, is_deleted=False).first():
        user = User(
            username='demo_user',
            phone='13800000001',
            email='demo@example.com',
            nickname='演示用户',
            tenant_id=default_tenant.id,
        )
        user.password = 'user12345'
        user.balance = 188.00
        db.session.add(user)

    station = Station.query.filter_by(station_code='STN0010001', tenant_id=default_tenant.id, is_deleted=False).first()
    if not station:
        station = Station(
            station_code='STN0010001',
            name='演示换电站',
            type='street',
            status='active',
            latitude=39.9042000,
            longitude=116.4074000,
            address='北京市东城区演示路 1 号',
            city='北京',
            district='东城区',
            phone='400-100-0001',
            business_hours='08:00-22:00',
            total_cabinets=2,
            total_slots=24,
            available_slots=18,
            total_batteries=8,
            available_batteries=6,
            tenant_id=default_tenant.id,
        )
        db.session.add(station)
        db.session.flush()
        station.tenant_id = default_tenant.id

    if not Battery.query.filter_by(battery_code='BAT001000001', tenant_id=default_tenant.id, is_deleted=False).first():
        battery = Battery(
            battery_code='BAT001000001',
            model='60V20Ah 标准电池',
            battery_type='lithium_ion',
            capacity=20000,
            voltage_type='60V',
            status='available',
            power_level=92,
            current_station_id=station.id,
            rental_price_per_hour=0.50,
            deposit_amount=50.00,
            selling_price=899.00,
            tenant_id=default_tenant.id,
        )
        db.session.add(battery)

    if not Package.query.filter_by(name='演示月卡套餐', tenant_id=default_tenant.id, is_deleted=False).first():
        package = Package(
            name='演示月卡套餐',
            package_type='rider_unlimited',
            battery_model='60V20Ah 标准电池',
            hours=720,
            price=99.00,
            deposit_amount=50.00,
            exchange_fee=0.00,
            validity_days=30,
            rider_exclusive=True,
            is_active=True,
            description='答辩演示套餐，支持骑手换电流程展示',
            tenant_id=default_tenant.id,
        )
        db.session.add(package)

    db.session.commit()
    if app:
        app.logger.info('演示数据初始化完成，后台账号：admin / admin123')

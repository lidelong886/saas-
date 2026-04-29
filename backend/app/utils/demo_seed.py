from datetime import datetime, timedelta
from decimal import Decimal

from .. import db
from ..models import (
    AdminUser,
    Battery,
    Cabinet,
    CabinetStatus,
    ExchangeRecord,
    FaultReport,
    Notification,
    Order,
    Package,
    Payment,
    PaymentMethod,
    PaymentStatus,
    PaymentType,
    RiderReservation,
    Station,
    Tenant,
    User,
    UserPackage,
    WalletTransaction,
)


def _set_tenant(obj, tenant_id):
    obj.tenant_id = tenant_id
    return obj


def _commit_flush():
    db.session.flush()


def _tenant(code, name, **kwargs):
    tenant = Tenant.query.filter_by(code=code, is_deleted=False).first()
    if not tenant:
        tenant = Tenant(code=code, name=name, tenant_id=1)
        db.session.add(tenant)
        _commit_flush()
    tenant.name = name
    tenant.brand_name = kwargs.get('brand_name', name)
    tenant.contact_name = kwargs.get('contact_name', '运营负责人')
    tenant.contact_phone = kwargs.get('contact_phone', '13800000000')
    tenant.contact_email = kwargs.get('contact_email', f'{code.lower()}@example.com')
    tenant.status = kwargs.get('status', 'active')
    tenant.max_users = kwargs.get('max_users', 500)
    tenant.max_stations = kwargs.get('max_stations', 50)
    tenant.max_batteries = kwargs.get('max_batteries', 2000)
    tenant.remarks = kwargs.get('remarks', '答辩演示运营商')
    tenant.tenant_id = tenant.id
    return tenant


def _admin(username, phone, tenant_id, password, nickname, super_admin=False):
    admin = AdminUser.query.filter_by(username=username, is_deleted=False).first()
    if not admin:
        admin = AdminUser(username=username, phone=phone, tenant_id=tenant_id)
        db.session.add(admin)
    admin.phone = phone
    admin.email = f'{username}@example.com'
    admin.nickname = nickname
    admin.is_active = True
    admin.is_super_admin = super_admin
    admin.tenant_id = tenant_id
    admin.password = password
    return admin


def _user(username, phone, tenant_id, password, **kwargs):
    user = User.query.filter_by(phone=phone, is_deleted=False).first()
    if not user:
        user = User.query.filter_by(username=username, is_deleted=False).first()
    if not user:
        user = User(username=username, phone=phone, email=kwargs.get('email', f'{username}@example.com'), tenant_id=tenant_id)
        db.session.add(user)
    user.username = username
    user.email = kwargs.get('email', f'{username}@example.com')
    user.nickname = kwargs.get('nickname', username)
    user.real_name = kwargs.get('real_name')
    user.id_card_no = kwargs.get('id_card_no')
    user.realname_status = kwargs.get('realname_status', 'verified')
    user.is_active = True
    user.is_verified = kwargs.get('is_verified', True)
    user.is_rider = kwargs.get('is_rider', False)
    user.rider_level = kwargs.get('rider_level', 'silver')
    user.work_status = kwargs.get('work_status', 'online')
    user.points = kwargs.get('points', 860)
    user.balance = Decimal(str(kwargs.get('balance', '188.00')))
    user.latitude = kwargs.get('latitude', Decimal('39.9042000'))
    user.longitude = kwargs.get('longitude', Decimal('116.4074000'))
    user.location_updated_at = datetime.now()
    user.preferences = kwargs.get('preferences', {'theme': 'bright', 'notify': True})
    user.tenant_id = tenant_id
    user.password = password
    return user


def _station(code, tenant_id, **kwargs):
    station = Station.query.filter_by(station_code=code, is_deleted=False).first()
    if not station:
        station = Station(
            station_code=code,
            name=kwargs['name'],
            latitude=kwargs['latitude'],
            longitude=kwargs['longitude'],
            address=kwargs['address'],
            tenant_id=tenant_id,
        )
        db.session.add(station)
    station.name = kwargs['name']
    station.type = kwargs.get('type', 'street')
    station.status = kwargs.get('status', 'active')
    station.latitude = kwargs['latitude']
    station.longitude = kwargs['longitude']
    station.address = kwargs['address']
    station.city = kwargs.get('city', '北京')
    station.district = kwargs.get('district', '朝阳区')
    station.phone = kwargs.get('phone', '400-100-0001')
    station.business_hours = kwargs.get('business_hours', '08:00-22:00')
    station.is_24_hour = kwargs.get('is_24_hour', False)
    station.total_cabinets = kwargs.get('total_cabinets', 2)
    station.total_slots = kwargs.get('total_slots', 24)
    station.available_slots = kwargs.get('available_slots', 18)
    station.total_batteries = kwargs.get('total_batteries', 8)
    station.available_batteries = kwargs.get('available_batteries', 6)
    station.charging_batteries = kwargs.get('charging_batteries', 2)
    station.monthly_rentals = kwargs.get('monthly_rentals', 126)
    station.monthly_revenue = Decimal(str(kwargs.get('monthly_revenue', '3688.00')))
    station.network_status = kwargs.get('network_status', True)
    station.last_heartbeat = datetime.now()
    station.firmware_version = kwargs.get('firmware_version', 'v1.2.8')
    station.images = kwargs.get('images', [])
    station.tenant_id = tenant_id
    return station


def _cabinet(code, tenant_id, station, **kwargs):
    cabinet = Cabinet.query.filter_by(cabinet_code=code, is_deleted=False).first()
    if not cabinet:
        cabinet = Cabinet(cabinet_code=code, name=kwargs['name'], station_id=station.id, total_slots=kwargs.get('total_slots', 12), occupied_slots=kwargs.get('occupied_slots', 0), tenant_id=tenant_id)
        db.session.add(cabinet)
    cabinet.name = kwargs['name']
    cabinet.model = kwargs.get('model', 'BC-24S')
    cabinet.station_id = station.id
    cabinet.status = kwargs.get('status', CabinetStatus.ONLINE)
    cabinet.temperature = Decimal(str(kwargs.get('temperature', '28.5')))
    cabinet.humidity = Decimal(str(kwargs.get('humidity', '45.0')))
    cabinet.total_slots = kwargs.get('total_slots', 12)
    cabinet.occupied_slots = kwargs.get('occupied_slots', 8)
    cabinet.available_slots = cabinet.total_slots - cabinet.occupied_slots
    cabinet.battery_count = kwargs.get('battery_count', 8)
    cabinet.imei = kwargs.get('imei', f'IMEI{code}')
    cabinet.ip_address = kwargs.get('ip_address', '192.168.1.10')
    cabinet.mac_address = kwargs.get('mac_address', '00:11:22:33:44:55')
    cabinet.firmware_version = kwargs.get('firmware_version', 'v2.3.1')
    cabinet.network_signal = kwargs.get('network_signal', 92)
    cabinet.last_heartbeat = datetime.now()
    cabinet.is_online = kwargs.get('is_online', True)
    cabinet.latitude = station.latitude
    cabinet.longitude = station.longitude
    cabinet.tenant_id = tenant_id
    return cabinet


def _battery(code, tenant_id, station, cabinet=None, **kwargs):
    battery = Battery.query.filter_by(battery_code=code, is_deleted=False).first()
    if not battery:
        battery = Battery(battery_code=code, model=kwargs.get('model', '60V20Ah 标准电池'), capacity=kwargs.get('capacity', 20000), tenant_id=tenant_id)
        db.session.add(battery)
    battery.battery_type = kwargs.get('battery_type', 'lithium_ion')
    battery.model = kwargs.get('model', '60V20Ah 标准电池')
    battery.capacity = kwargs.get('capacity', 20000)
    battery.voltage_type = kwargs.get('voltage_type', '60V')
    battery.status = kwargs.get('status', 'available')
    battery.power_level = kwargs.get('power_level', 90)
    battery.voltage = Decimal(str(kwargs.get('voltage', '60.8')))
    battery.temperature = Decimal(str(kwargs.get('temperature', '30.5')))
    battery.current_station_id = station.id if station else None
    battery.current_cabinet_id = cabinet.id if cabinet else None
    battery.slot_position = kwargs.get('slot_position')
    battery.current_user_id = kwargs.get('current_user_id')
    battery.rented_at = kwargs.get('rented_at')
    battery.expected_return_at = kwargs.get('expected_return_at')
    battery.selling_price = Decimal(str(kwargs.get('selling_price', '899.00')))
    battery.purchase_date = kwargs.get('purchase_date')
    battery.warranty_period = kwargs.get('warranty_period', 24)
    battery.total_usage_hours = kwargs.get('total_usage_hours', 120)
    battery.cycle_count = kwargs.get('cycle_count', 46)
    battery.rental_price_per_hour = Decimal(str(kwargs.get('rental_price_per_hour', '0.50')))
    battery.deposit_amount = Decimal(str(kwargs.get('deposit_amount', '50.00')))
    battery.imei = kwargs.get('imei', f'BATIMEI{code}')
    battery.bluetooth_mac = kwargs.get('bluetooth_mac', 'AA:BB:CC:DD:EE:FF')
    battery.firmware_version = kwargs.get('firmware_version', 'v1.0.6')
    battery.tenant_id = tenant_id
    return battery


def _package(name, tenant_id, **kwargs):
    package = Package.query.filter_by(name=name, tenant_id=tenant_id, is_deleted=False).first()
    if not package:
        package = Package(name=name, price=kwargs.get('price', Decimal('99.00')), tenant_id=tenant_id)
        db.session.add(package)
    package.package_type = kwargs.get('package_type', 'rider_unlimited')
    package.battery_model = kwargs.get('battery_model', '60V20Ah 标准电池')
    package.hours = kwargs.get('hours', 720)
    package.price = Decimal(str(kwargs.get('price', '99.00')))
    package.deposit_amount = Decimal(str(kwargs.get('deposit_amount', '50.00')))
    package.exchange_fee = Decimal(str(kwargs.get('exchange_fee', '0.00')))
    package.is_active = kwargs.get('is_active', True)
    package.description = kwargs.get('description', '答辩演示套餐')
    package.rider_exclusive = kwargs.get('rider_exclusive', False)
    package.validity_days = kwargs.get('validity_days', 30)
    package.tenant_id = tenant_id
    return package


def _order(order_no, tenant_id, user, **kwargs):
    order = Order.query.filter_by(order_no=order_no, is_deleted=False).first()
    if not order:
        order = Order(order_no=order_no, order_type=kwargs.get('order_type', 'rental'), user_id=user.id, tenant_id=tenant_id)
        db.session.add(order)
    order.order_type = kwargs.get('order_type', 'rental')
    order.status = kwargs.get('status', 'completed')
    order.source = kwargs.get('source', 'mini_program')
    order.user_id = user.id
    order.battery_id = kwargs.get('battery_id')
    order.station_id = kwargs.get('station_id')
    order.cabinet_id = kwargs.get('cabinet_id')
    order.package_id = kwargs.get('package_id')
    order.rental_start_time = kwargs.get('rental_start_time')
    order.rental_end_time = kwargs.get('rental_end_time')
    order.expected_return_time = kwargs.get('expected_return_time')
    order.actual_return_time = kwargs.get('actual_return_time')
    order.rental_hours = float(kwargs.get('rental_hours', 0) or 0)
    order.unit_price = Decimal(str(kwargs.get('unit_price', '0.50')))
    order.rental_fee = Decimal(str(kwargs.get('rental_fee', '0.00')))
    order.deposit_fee = Decimal(str(kwargs.get('deposit_fee', '0.00')))
    order.total_amount = Decimal(str(kwargs.get('total_amount', '0.00')))
    order.exchange_fee = Decimal(str(kwargs.get('exchange_fee', '0.00')))
    order.pricing_snapshot = kwargs.get('pricing_snapshot', {})
    order.payment_method = kwargs.get('payment_method', 'balance')
    order.payment_time = kwargs.get('payment_time')
    order.transaction_id = kwargs.get('transaction_id')
    order.refund_status = kwargs.get('refund_status', 'none')
    order.refund_amount = Decimal(str(kwargs.get('refund_amount', '0.00')))
    order.pickup_location = kwargs.get('pickup_location')
    order.return_location = kwargs.get('return_location')
    order.pickup_latitude = kwargs.get('pickup_latitude')
    order.pickup_longitude = kwargs.get('pickup_longitude')
    order.return_latitude = kwargs.get('return_latitude')
    order.return_longitude = kwargs.get('return_longitude')
    order.remarks = kwargs.get('remarks', '答辩演示订单')
    order.created_at = kwargs.get('created_at', order.created_at)
    order.updated_at = kwargs.get('updated_at', datetime.now())
    order.tenant_id = tenant_id
    return order


def _payment(payment_no, tenant_id, user, order=None, **kwargs):
    payment = Payment.query.filter_by(payment_no=payment_no, is_deleted=False).first()
    if not payment:
        payment = Payment(payment_no=payment_no, user_id=user.id, amount=kwargs.get('amount', Decimal('0.00')), tenant_id=tenant_id)
        db.session.add(payment)
    payment.payment_type = kwargs.get('payment_type', PaymentType.ORDER_PAYMENT)
    payment.payment_method = kwargs.get('payment_method', PaymentMethod.BALANCE)
    payment.status = kwargs.get('status', PaymentStatus.SUCCESS)
    payment.user_id = user.id
    payment.order_id = order.id if order else kwargs.get('order_id')
    payment.amount = Decimal(str(kwargs.get('amount', '0.00')))
    payment.refund_amount = Decimal(str(kwargs.get('refund_amount', '0.00')))
    payment.transaction_id = kwargs.get('transaction_id', f'TXN{payment_no}')
    payment.out_trade_no = kwargs.get('out_trade_no', payment_no)
    payment.refund_status = kwargs.get('refund_status', 'none')
    payment.payment_time = kwargs.get('payment_time', datetime.now())
    payment.callback_time = kwargs.get('callback_time', payment.payment_time)
    payment.payment_params = kwargs.get('payment_params', {'demo': True})
    payment.callback_data = kwargs.get('callback_data', {'trade_state': 'SUCCESS'})
    payment.remarks = kwargs.get('remarks', '毕设演示模式支付记录')
    payment.tenant_id = tenant_id
    return payment


def _wallet(user, tenant_id, transaction_type, amount, before, after, **kwargs):
    exists = WalletTransaction.query.filter_by(user_id=user.id, tenant_id=tenant_id, remarks=kwargs.get('remarks'), is_deleted=False).first()
    if exists:
        return exists
    tx = WalletTransaction(
        user_id=user.id,
        order_id=kwargs.get('order_id'),
        payment_id=kwargs.get('payment_id'),
        transaction_type=transaction_type,
        direction=kwargs.get('direction', 'expense'),
        amount=Decimal(str(amount)),
        balance_before=Decimal(str(before)),
        balance_after=Decimal(str(after)),
        status='success',
        remarks=kwargs.get('remarks', '答辩演示流水'),
        tenant_id=tenant_id,
    )
    db.session.add(tx)
    return tx


def ensure_demo_data(app=None):
    """Create a complete, repeatable defense-demo data set."""
    now = datetime.now()

    default_tenant = _tenant(
        'DEFAULT',
        '默认运营商',
        brand_name='青桔换电',
        contact_name='系统管理员',
        contact_phone='13800000000',
        contact_email='admin@example.com',
        remarks='系统默认运营商，用于后台总览和小程序默认服务',
    )
    fast_tenant = _tenant(
        'FASTPOWER',
        '闪电换电',
        brand_name='闪电换电',
        contact_name='李经理',
        contact_phone='13900000002',
        contact_email='fastpower@example.com',
        remarks='多租户切换演示运营商',
    )

    default_tenant = db.session.get(Tenant, 1) or default_tenant

    _admin('admin', '18888888888', default_tenant.id, 'admin123', '系统管理员', True)
    _admin('tenant_admin', '18888880001', fast_tenant.id, 'tenant123', '闪电换电管理员', True)

    demo_user = _user(
        'demo_user',
        '13800000001',
        default_tenant.id,
        'user12345',
        nickname='演示骑手',
        real_name='张三',
        id_card_no='110101199901010011',
        is_rider=True,
        rider_level='gold',
        balance='188.00',
        points=1280,
    )
    normal_user = _user(
        'normal_user',
        '13800000002',
        default_tenant.id,
        'user12345',
        nickname='普通用户',
        real_name='李四',
        balance='66.00',
        points=360,
    )
    fast_user = _user(
        'fast_user',
        '13900000001',
        fast_tenant.id,
        'user12345',
        nickname='闪电骑手',
        real_name='王五',
        is_rider=True,
        balance='120.00',
        points=720,
    )

    station_main = _station(
        'STN0010001',
        default_tenant.id,
        name='中关村演示换电站',
        latitude=Decimal('39.9835000'),
        longitude=Decimal('116.3157000'),
        address='北京市海淀区中关村大街 1 号',
        district='海淀区',
        phone='400-100-0001',
        total_cabinets=2,
        total_slots=24,
        available_slots=16,
        total_batteries=10,
        available_batteries=7,
        charging_batteries=2,
        monthly_rentals=186,
        monthly_revenue='5688.00',
    )
    station_sub = _station(
        'STN0010002',
        default_tenant.id,
        name='望京商圈换电站',
        latitude=Decimal('39.9968000'),
        longitude=Decimal('116.4805000'),
        address='北京市朝阳区望京街 9 号',
        district='朝阳区',
        is_24_hour=True,
        business_hours='24小时营业',
        total_cabinets=1,
        total_slots=12,
        available_slots=7,
        total_batteries=6,
        available_batteries=4,
        charging_batteries=1,
        monthly_rentals=96,
        monthly_revenue='2680.00',
    )
    fast_station = _station(
        'STN0020001',
        fast_tenant.id,
        name='闪电国贸换电站',
        latitude=Decimal('39.9149000'),
        longitude=Decimal('116.4572000'),
        address='北京市朝阳区国贸演示点 A 座',
        district='朝阳区',
        phone='400-200-0001',
        total_cabinets=1,
        total_slots=12,
        available_slots=8,
        total_batteries=5,
        available_batteries=4,
        charging_batteries=1,
        monthly_rentals=72,
        monthly_revenue='1988.00',
    )
    _commit_flush()

    cabinet_main_a = _cabinet('CAB0010001', default_tenant.id, station_main, name='中关村 1 号柜', occupied_slots=9, battery_count=9, ip_address='192.168.10.11')
    cabinet_main_b = _cabinet('CAB0010002', default_tenant.id, station_main, name='中关村 2 号柜', occupied_slots=7, battery_count=7, ip_address='192.168.10.12')
    cabinet_sub = _cabinet('CAB0010003', default_tenant.id, station_sub, name='望京 1 号柜', occupied_slots=5, battery_count=5, ip_address='192.168.20.11')
    fast_cabinet = _cabinet('CAB0020001', fast_tenant.id, fast_station, name='闪电国贸 1 号柜', occupied_slots=5, battery_count=5, ip_address='192.168.30.11')
    _commit_flush()

    battery_available = _battery('BAT001000001', default_tenant.id, station_main, cabinet_main_a, slot_position='01', power_level=96, status='available', total_usage_hours=80, cycle_count=32)
    battery_charging = _battery('BAT001000002', default_tenant.id, station_main, cabinet_main_a, slot_position='02', power_level=48, status='charging', voltage='58.4', temperature='32.0', total_usage_hours=156, cycle_count=68)
    battery_rented = _battery(
        'BAT001000003',
        default_tenant.id,
        station_main,
        cabinet_main_b,
        slot_position=None,
        power_level=76,
        status='rented',
        current_user_id=demo_user.id,
        rented_at=now - timedelta(hours=2),
        expected_return_at=now + timedelta(hours=22),
        total_usage_hours=230,
        cycle_count=96,
    )
    old_battery = _battery('BAT001000004', default_tenant.id, station_sub, cabinet_sub, slot_position='03', power_level=18, status='maintenance', voltage='55.2', temperature='36.5', total_usage_hours=420, cycle_count=210)
    new_battery = _battery('BAT001000005', default_tenant.id, station_sub, cabinet_sub, slot_position='04', power_level=99, status='available', total_usage_hours=45, cycle_count=18)
    _battery('BAT001000006', default_tenant.id, station_main, cabinet_main_b, slot_position='05', power_level=88, status='available')
    _battery('BAT001000007', default_tenant.id, station_sub, cabinet_sub, slot_position='06', power_level=67, status='available')
    _battery('BAT001720001', default_tenant.id, station_main, cabinet_main_b, slot_position='07', model='72V32Ah 长续航旗舰电池', capacity=32000, voltage_type='72V', voltage='73.6', power_level=97, status='available', selling_price='1699.00', deposit_amount='120.00', rental_price_per_hour='0.80', total_usage_hours=38, cycle_count=12)
    _battery('BAT001720002', default_tenant.id, station_sub, cabinet_sub, slot_position='07', model='72V38Ah 城配高能电池', capacity=38000, voltage_type='72V', voltage='74.1', power_level=92, status='available', selling_price='2199.00', deposit_amount='150.00', rental_price_per_hour='0.90', total_usage_hours=66, cycle_count=24)
    _battery('BAT001720003', default_tenant.id, station_main, cabinet_main_a, slot_position='08', model='72V45Ah ?? Pro ??', capacity=45000, voltage_type='72V', voltage='73.8', power_level=86, status='available', selling_price='2799.00', deposit_amount='180.00', rental_price_per_hour='1.00', total_usage_hours=92, cycle_count=31)
    fast_battery = _battery('BAT002000001', fast_tenant.id, fast_station, fast_cabinet, slot_position='01', power_level=91, status='available')
    _battery('BAT002000002', fast_tenant.id, fast_station, fast_cabinet, slot_position='02', power_level=62, status='charging')
    _battery('BAT002720001', fast_tenant.id, fast_station, fast_cabinet, slot_position='03', model='72V35Ah 闪电极速版电池', capacity=35000, voltage_type='72V', voltage='73.9', power_level=95, status='available', selling_price='1999.00', deposit_amount='150.00', rental_price_per_hour='0.88')
    _commit_flush()

    month_package = _package(
        '骑手月卡套餐',
        default_tenant.id,
        package_type='rider_unlimited',
        hours=720,
        price='99.00',
        deposit_amount='50.00',
        exchange_fee='0.00',
        rider_exclusive=True,
        validity_days=30,
        description='适合外卖骑手的 30 天不限次换电套餐',
    )
    day_package = _package(
        '日租体验套餐',
        default_tenant.id,
        package_type='rental',
        hours=24,
        price='12.00',
        deposit_amount='50.00',
        exchange_fee='3.00',
        rider_exclusive=False,
        validity_days=1,
        description='普通用户 24 小时体验套餐',
    )
    fast_package = _package('闪电骑手月卡', fast_tenant.id, package_type='rider_unlimited', hours=720, price='89.00', exchange_fee='0.00', rider_exclusive=True, validity_days=30)
    _commit_flush()

    package_order = _order(
        'ORD-DEMO-PACKAGE-001',
        default_tenant.id,
        demo_user,
        order_type='purchase',
        status='completed',
        package_id=month_package.id,
        total_amount='99.00',
        payment_method='balance',
        payment_time=now - timedelta(days=3),
        transaction_id='TXN-DEMO-PACKAGE-001',
        remarks='购买骑手月卡套餐',
        created_at=now - timedelta(days=3),
    )
    rental_order = _order(
        'ORD-DEMO-RENT-001',
        default_tenant.id,
        demo_user,
        order_type='rental',
        status='rented',
        battery_id=battery_rented.id,
        station_id=station_main.id,
        cabinet_id=cabinet_main_b.id,
        rental_start_time=now - timedelta(hours=2),
        expected_return_time=now + timedelta(hours=22),
        rental_hours='24',
        unit_price='0.50',
        rental_fee='12.00',
        deposit_fee='50.00',
        total_amount='62.00',
        payment_method='package_free',
        payment_time=now - timedelta(hours=2),
        pickup_location=station_main.name,
        pickup_latitude=station_main.latitude,
        pickup_longitude=station_main.longitude,
        remarks='当前进行中的租电订单',
        created_at=now - timedelta(hours=2),
    )
    exchange_order = _order(
        'ORD-DEMO-EXCHANGE-001',
        default_tenant.id,
        demo_user,
        order_type='exchange',
        status='completed',
        battery_id=new_battery.id,
        station_id=station_sub.id,
        cabinet_id=cabinet_sub.id,
        total_amount='0.00',
        exchange_fee='0.00',
        payment_method='package_free',
        payment_time=now - timedelta(days=1, hours=2),
        pickup_location=station_sub.name,
        return_location=station_sub.name,
        remarks='套餐内免费换电记录',
        created_at=now - timedelta(days=1, hours=2),
    )
    normal_order = _order(
        'ORD-DEMO-NORMAL-001',
        default_tenant.id,
        normal_user,
        order_type='rental',
        status='completed',
        battery_id=battery_available.id,
        station_id=station_main.id,
        cabinet_id=cabinet_main_a.id,
        rental_start_time=now - timedelta(days=2, hours=4),
        rental_end_time=now - timedelta(days=2),
        expected_return_time=now - timedelta(days=1, hours=4),
        actual_return_time=now - timedelta(days=2),
        rental_hours='4',
        unit_price='0.50',
        rental_fee='2.00',
        deposit_fee='50.00',
        total_amount='52.00',
        payment_method='balance',
        payment_time=now - timedelta(days=2, hours=4),
        remarks='普通用户已完成租电订单',
        created_at=now - timedelta(days=2, hours=4),
    )
    fast_order = _order(
        'ORD-DEMO-FAST-001',
        fast_tenant.id,
        fast_user,
        order_type='rental',
        status='completed',
        battery_id=fast_battery.id,
        station_id=fast_station.id,
        cabinet_id=fast_cabinet.id,
        rental_hours='3',
        rental_fee='1.50',
        deposit_fee='50.00',
        total_amount='51.50',
        payment_method='balance',
        payment_time=now - timedelta(days=1),
        remarks='闪电换电租户演示订单',
        created_at=now - timedelta(days=1),
    )
    _commit_flush()

    _payment('PAY-DEMO-PACKAGE-001', default_tenant.id, demo_user, package_order, amount='99.00', payment_time=package_order.payment_time)
    _payment('PAY-DEMO-RENT-001', default_tenant.id, demo_user, rental_order, amount='0.00', payment_method=PaymentMethod.BALANCE, payment_time=rental_order.payment_time, remarks='套餐抵扣支付')
    _payment('PAY-DEMO-NORMAL-001', default_tenant.id, normal_user, normal_order, amount='52.00', payment_time=normal_order.payment_time)
    _payment('PAY-DEMO-FAST-001', fast_tenant.id, fast_user, fast_order, amount='51.50', payment_time=fast_order.payment_time)
    _commit_flush()

    if not UserPackage.query.filter_by(user_id=demo_user.id, package_id=month_package.id, tenant_id=default_tenant.id, is_deleted=False).first():
        user_package = UserPackage(
            user_id=demo_user.id,
            package_id=month_package.id,
            order_id=package_order.id,
            status='active',
            package_name=month_package.name,
            package_type=month_package.package_type,
            total_hours=month_package.hours,
            activated_at=now - timedelta(days=3),
            expires_at=now + timedelta(days=27),
            tenant_id=default_tenant.id,
        )
        db.session.add(user_package)

    if not ExchangeRecord.query.filter_by(record_no='EXC-DEMO-001', is_deleted=False).first():
        exchange = ExchangeRecord(
            record_no='EXC-DEMO-001',
            user_id=demo_user.id,
            order_id=exchange_order.id,
            station_id=station_sub.id,
            cabinet_id=cabinet_sub.id,
            old_battery_id=old_battery.id,
            new_battery_id=new_battery.id,
            exchange_fee=Decimal('0.00'),
            status='completed',
            operator_type='user',
            remarks='骑手扫码完成换电，套餐内免费',
            tenant_id=default_tenant.id,
        )
        exchange.created_at = now - timedelta(days=1, hours=2)
        db.session.add(exchange)

    _wallet(demo_user, default_tenant.id, 'recharge', '200.00', '0.00', '200.00', direction='income', remarks='演示用户余额充值')
    _wallet(demo_user, default_tenant.id, 'pay', '99.00', '200.00', '101.00', order_id=package_order.id, direction='expense', remarks='购买骑手月卡套餐')
    _wallet(normal_user, default_tenant.id, 'pay', '52.00', '118.00', '66.00', order_id=normal_order.id, direction='expense', remarks='普通租电订单支付')
    _wallet(fast_user, fast_tenant.id, 'pay', '51.50', '171.50', '120.00', order_id=fast_order.id, direction='expense', remarks='闪电租户租电支付')

    notifications = [
        (demo_user, default_tenant.id, 'system', '欢迎使用青桔换电', '当前服务运营商：默认运营商，可在我的页面切换运营商。', 'none', None, True),
        (demo_user, default_tenant.id, 'order', '套餐购买成功', '骑手月卡套餐已生效，剩余 27 天。', 'order', package_order.id, False),
        (demo_user, default_tenant.id, 'exchange', '换电完成', '你已在望京商圈换电站完成一次免费换电。', 'exchange', 'EXC-DEMO-001', False),
        (fast_user, fast_tenant.id, 'system', '闪电换电通知', '闪电国贸换电站今日设备运行正常。', 'none', None, False),
    ]
    for user, tenant_id, noti_type, title, content, link_type, link_id, is_read in notifications:
        exists = Notification.query.filter_by(user_id=user.id, title=title, tenant_id=tenant_id, is_deleted=False).first()
        if not exists:
            db.session.add(Notification(user_id=user.id, noti_type=noti_type, title=title, content=content, link_type=link_type, link_id=str(link_id) if link_id else None, is_read=is_read, tenant_id=tenant_id))

    if not FaultReport.query.filter_by(report_no='FLT-DEMO-001', is_deleted=False).first():
        fault = FaultReport(
            report_no='FLT-DEMO-001',
            user_id=demo_user.id,
            station_id=station_sub.id,
            battery_id=old_battery.id,
            fault_type='battery_low',
            description='演示故障：电池电量异常偏低，已提交后台处理。',
            contact_phone=demo_user.phone,
            status='processing',
            admin_remarks='后台已派维护人员检查，答辩演示数据。',
            tenant_id=default_tenant.id,
        )
        db.session.add(fault)

    if not RiderReservation.query.filter_by(user_id=demo_user.id, station_id=station_main.id, tenant_id=default_tenant.id, status='confirmed', is_deleted=False).first():
        db.session.add(RiderReservation(
            user_id=demo_user.id,
            station_id=station_main.id,
            battery_id=battery_available.id,
            reserved_at=now - timedelta(minutes=5),
            expires_at=now + timedelta(minutes=25),
            status='confirmed',
            timeout_job_id='demo-reservation-job',
            tenant_id=default_tenant.id,
        ))

    db.session.commit()
    if app:
        app.logger.info('演示数据初始化完成：后台 admin/admin123，小程序 13800000001/user12345')



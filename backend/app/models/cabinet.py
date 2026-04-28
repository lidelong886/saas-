"""
柜子模型
"""
from enum import Enum
from .base import BaseModel
from .. import db

class CabinetStatus(Enum):
    """柜子状态枚举"""
    ONLINE = 'online'         # 在线
    OFFLINE = 'offline'       # 离线
    MAINTENANCE = 'maintenance'  # 维护中
    FAULT = 'fault'           # 故障

class Cabinet(BaseModel):
    """
    电池柜子模型
    """
    __tablename__ = 'cabinets'

    # 基本信息
    cabinet_code = db.Column(db.String(50), unique=True, nullable=False, comment='柜子编码')
    name = db.Column(db.String(100), nullable=False, comment='柜子名称')
    model = db.Column(db.String(50), comment='柜子型号')

    # 关联信息
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False, comment='所属站点ID')

    # 状态信息
    status = db.Column(db.Enum(CabinetStatus), default=CabinetStatus.ONLINE, comment='柜子状态')
    temperature = db.Column(db.Numeric(5, 1), comment='柜内温度(°C)')
    humidity = db.Column(db.Numeric(5, 1), comment='柜内湿度(%)')

    # 插槽信息
    total_slots = db.Column(db.Integer, default=20, comment='总插槽数')
    occupied_slots = db.Column(db.Integer, default=0, comment='已占用插槽数')
    available_slots = db.Column(db.Integer, default=20, comment='可用插槽数')

    # 电池统计
    battery_count = db.Column(db.Integer, default=0, comment='电池数量')

    # 设备信息
    imei = db.Column(db.String(50), comment='IMEI号')
    ip_address = db.Column(db.String(20), comment='IP地址')
    mac_address = db.Column(db.String(20), comment='MAC地址')
    firmware_version = db.Column(db.String(20), comment='固件版本')

    # 网络状态
    network_signal = db.Column(db.Integer, comment='网络信号强度(0-100)')
    last_heartbeat = db.Column(db.DateTime, comment='最后心跳时间')
    is_online = db.Column(db.Boolean, default=True, comment='是否在线')

    # 地理位置（如果与站点不同）
    latitude = db.Column(db.Numeric(10, 7), comment='纬度')
    longitude = db.Column(db.Numeric(10, 7), comment='经度')

    # 关联对象
    station = db.relationship('Station', backref='cabinets')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.available_slots = self.total_slots - self.occupied_slots

    def is_operational(self):
        """
        检查柜子是否正常运行
        """
        return (self.status == CabinetStatus.ONLINE and
                self.is_online and
                self.tenant_id == getattr(__import__('flask').g, 'tenant_id', 1))

    def get_slot_info(self):
        """
        获取插槽信息
        """
        slots = []
        occupied_positions = set()

        # 获取已占用的插槽位置
        for battery in self.batteries:
            if battery.slot_position:
                occupied_positions.add(battery.slot_position)

        # 生成所有插槽信息
        for i in range(1, self.total_slots + 1):
            position = f"{i:02d}"  # 格式化为两位数
            slots.append({
                'position': position,
                'is_occupied': position in occupied_positions,
                'battery_code': None
            })

        # 填充电池信息
        for battery in self.batteries:
            if battery.slot_position:
                for slot in slots:
                    if slot['position'] == battery.slot_position:
                        slot['battery_code'] = battery.battery_code
                        break

        return slots

    def find_available_slot(self):
        """
        查找可用插槽
        """
        occupied_positions = {battery.slot_position for battery in self.batteries
                            if battery.slot_position}

        for i in range(1, self.total_slots + 1):
            position = f"{i:02d}"
            if position not in occupied_positions:
                return position

        return None

    def place_battery(self, battery, position=None):
        """
        放入电池
        """
        if not self.is_operational():
            return False, "柜子不可用"

        if position is None:
            position = self.find_available_slot()

        if not position:
            return False, "没有可用插槽"

        # 检查位置是否已被占用
        existing_battery = next(
            (b for b in self.batteries if b.slot_position == position), None
        )
        if existing_battery:
            return False, "该位置已被占用"

        battery.current_cabinet_id = self.id
        battery.current_station_id = self.station_id
        battery.slot_position = position
        battery.save()

        self.update_slot_stats()
        return True, f"电池已放入位置 {position}"

    def remove_battery(self, battery_code):
        """
        取出电池
        """
        battery = next(
            (b for b in self.batteries if b.battery_code == battery_code), None
        )

        if not battery:
            return False, "电池不在此柜子中"

        position = battery.slot_position
        battery.current_cabinet_id = None
        battery.slot_position = None
        battery.save()

        self.update_slot_stats()
        return True, f"电池已从位置 {position} 取出"

    def update_slot_stats(self):
        """
        更新插槽统计
        """
        self.occupied_slots = len([b for b in self.batteries if b.slot_position])
        self.available_slots = self.total_slots - self.occupied_slots
        self.battery_count = len(self.batteries)
        self.save()

        # 更新站点统计
        if self.station:
            self.station.update_slot_stats()
            self.station.update_battery_stats()

    def update_status(self, status=None, temperature=None, humidity=None,
                     network_signal=None, is_online=None):
        """
        更新柜子状态
        """
        if status is not None:
            self.status = status
        if temperature is not None:
            self.temperature = temperature
        if humidity is not None:
            self.humidity = humidity
        if network_signal is not None:
            self.network_signal = network_signal
        if is_online is not None:
            self.is_online = is_online

        self.last_heartbeat = __import__('datetime').datetime.now()
        self.save()

    def to_dict(self):
        """
        转换为字典
        """
        data = super().to_dict()
        data['status'] = self.status.value if self.status else None
        data['slot_info'] = self.get_slot_info()
        return data

    @classmethod
    def get_by_code(cls, cabinet_code):
        """
        根据柜子编码获取柜子
        """
        tenant_id = getattr(__import__('flask').g, 'tenant_id', 1)
        return cls.query.filter_by(
            cabinet_code=cabinet_code,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()

    @classmethod
    def get_operational_cabinets(cls, station_id=None):
        """
        获取正常运行的柜子
        """
        tenant_id = getattr(__import__('flask').g, 'tenant_id', 1)
        query = cls.query.filter_by(
            tenant_id=tenant_id,
            status=CabinetStatus.ONLINE,
            is_online=True,
            is_deleted=False
        )

        if station_id:
            query = query.filter_by(station_id=station_id)

        return query.all()


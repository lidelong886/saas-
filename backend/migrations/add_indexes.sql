-- 为常用查询字段添加索引以提升性能

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_user_phone ON user(phone);
CREATE INDEX IF NOT EXISTS idx_user_role ON user(role);

-- 电池表索引
CREATE INDEX IF NOT EXISTS idx_battery_code ON battery(battery_code);
CREATE INDEX IF NOT EXISTS idx_battery_status ON battery(status);
CREATE INDEX IF NOT EXISTS idx_battery_station ON battery(station_id);

-- 订单表索引
CREATE INDEX IF NOT EXISTS idx_order_user ON "order"(user_id);
CREATE INDEX IF NOT EXISTS idx_order_battery ON "order"(battery_id);
CREATE INDEX IF NOT EXISTS idx_order_status ON "order"(status);
CREATE INDEX IF NOT EXISTS idx_order_created ON "order"(created_at);

-- 支付表索引
CREATE INDEX IF NOT EXISTS idx_payment_order ON payment(order_id);
CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(status);
CREATE INDEX IF NOT EXISTS idx_payment_created ON payment(created_at);

-- 站点表索引
CREATE INDEX IF NOT EXISTS idx_station_location ON station(latitude, longitude);

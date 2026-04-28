"""
添加骑手功能相关表和字段
执行方式: python migrations/add_rider_features.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def migrate():
    app = create_app()
    with app.app_context():
        try:
            print("开始迁移骑手功能相关表和字段...")

            # 1. 检查并添加 packages 表的新字段
            result = db.session.execute(db.text("PRAGMA table_info(packages)"))
            package_columns = [row[1] for row in result]

            if 'rider_exclusive' not in package_columns:
                print("添加 packages.rider_exclusive 字段...")
                db.session.execute(db.text(
                    "ALTER TABLE packages ADD COLUMN rider_exclusive BOOLEAN DEFAULT 0"
                ))
                print("[OK] 成功添加 rider_exclusive 字段")

            if 'validity_days' not in package_columns:
                print("添加 packages.validity_days 字段...")
                db.session.execute(db.text(
                    "ALTER TABLE packages ADD COLUMN validity_days INTEGER"
                ))
                print("[OK] 成功添加 validity_days 字段")

            # 2. 创建 rider_reservations 表
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='rider_reservations'"
            ))
            if not result.fetchone():
                print("创建 rider_reservations 表...")
                db.session.execute(db.text("""
                    CREATE TABLE rider_reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        station_id INTEGER NOT NULL,
                        battery_id INTEGER,
                        reserved_at DATETIME NOT NULL,
                        expires_at DATETIME NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        timeout_job_id VARCHAR(100),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0,
                        tenant_id INTEGER NOT NULL DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (station_id) REFERENCES stations(id),
                        FOREIGN KEY (battery_id) REFERENCES batteries(id)
                    )
                """))
                print("[OK] 成功创建 rider_reservations 表")
            else:
                print("[OK] rider_reservations 表已存在")

            # 3. 创建 user_behavior_logs 表
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user_behavior_logs'"
            ))
            if not result.fetchone():
                print("创建 user_behavior_logs 表...")
                db.session.execute(db.text("""
                    CREATE TABLE user_behavior_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        action_type VARCHAR(50) NOT NULL,
                        station_id INTEGER,
                        extra_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0,
                        tenant_id INTEGER NOT NULL DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (station_id) REFERENCES stations(id)
                    )
                """))
                print("[OK] 成功创建 user_behavior_logs 表")
            else:
                print("[OK] user_behavior_logs 表已存在")

            # 4. 创建索引以提高查询性能
            print("创建索引...")

            # rider_reservations 索引
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_rider_reservations_user_id ON rider_reservations(user_id)"
            ))
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_rider_reservations_station_id ON rider_reservations(station_id)"
            ))
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_rider_reservations_status ON rider_reservations(status)"
            ))
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_rider_reservations_expires_at ON rider_reservations(expires_at)"
            ))

            # user_behavior_logs 索引
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_user_behavior_logs_user_id ON user_behavior_logs(user_id)"
            ))
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_user_behavior_logs_action_type ON user_behavior_logs(action_type)"
            ))
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_user_behavior_logs_created_at ON user_behavior_logs(created_at)"
            ))

            print("[OK] 成功创建索引")

            db.session.commit()
            print("\n[OK] 骑手功能迁移完成！")

        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] 迁移失败: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()

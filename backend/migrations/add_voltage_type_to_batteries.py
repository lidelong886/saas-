"""
添加 voltage_type 字段到 batteries 表
执行方式: python migrations/add_voltage_type_to_batteries.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # 检查字段是否已存在
            result = db.session.execute(db.text("PRAGMA table_info(batteries)"))
            columns = [row[1] for row in result]

            if 'voltage_type' in columns:
                print("✓ voltage_type 字段已存在，无需迁移")
                return

            print("开始添加 voltage_type 字段...")

            # 添加 voltage_type 字段，默认值为 '60V'
            db.session.execute(db.text(
                "ALTER TABLE batteries ADD COLUMN voltage_type VARCHAR(10) DEFAULT '60V'"
            ))

            db.session.commit()
            print("✓ 成功添加 voltage_type 字段")

        except Exception as e:
            db.session.rollback()
            print(f"✗ 迁移失败: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()

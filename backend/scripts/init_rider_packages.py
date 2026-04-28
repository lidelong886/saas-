"""
初始化骑手套餐数据
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Package

def init_rider_packages():
    """初始化骑手专属套餐"""
    app = create_app()

    with app.app_context():
        # 检查是否已存在骑手套餐
        existing = Package.query.filter_by(rider_exclusive=True, is_deleted=False).first()
        if existing:
            print("骑手套餐已存在，跳过初始化")
            return

        # 创建4个骑手套餐
        packages = [
            {
                'name': '骑手月卡',
                'package_type': 'rider_unlimited',
                'price': 299.00,
                'validity_days': 30,
                'rider_exclusive': True,
                'is_active': True,
                'description': '30天无限次换电，适合短期体验的骑手'
            },
            {
                'name': '骑手季卡',
                'package_type': 'rider_unlimited',
                'price': 699.00,
                'validity_days': 90,
                'rider_exclusive': True,
                'is_active': True,
                'description': '90天无限次换电，享78折优惠，适合季节性工作的骑手'
            },
            {
                'name': '骑手半年卡',
                'package_type': 'rider_unlimited',
                'price': 1299.00,
                'validity_days': 180,
                'rider_exclusive': True,
                'is_active': True,
                'description': '180天无限次换电，享72折优惠，适合长期工作的骑手'
            },
            {
                'name': '骑手年卡',
                'package_type': 'rider_unlimited',
                'price': 2399.00,
                'validity_days': 365,
                'rider_exclusive': True,
                'is_active': True,
                'description': '365天无限次换电，享67折优惠，最划算的选择'
            }
        ]

        created_count = 0
        for pkg_data in packages:
            package = Package(**pkg_data)
            db.session.add(package)
            created_count += 1
            print(f"创建套餐: {pkg_data['name']} - {pkg_data['price']}元 - {pkg_data['validity_days']}天")

        db.session.commit()
        print(f"\n成功创建 {created_count} 个骑手套餐！")

if __name__ == '__main__':
    init_rider_packages()

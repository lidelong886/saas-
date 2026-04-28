"""数据库迁移管理入口"""
import os

from app import create_app, db
from flask_migrate import Migrate


app = create_app(os.getenv('FLASK_ENV') or 'development')
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run()

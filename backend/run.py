"""
应用启动文件
"""
import os
from dotenv import load_dotenv
from app import create_app, socketio

# 加载环境变量
load_dotenv()

app = create_app(os.getenv('FLASK_ENV') or 'development')

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True
    )

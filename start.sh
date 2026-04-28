#!/bin/bash

# 电池SaaS平台一键启动脚本 (Bash)

echo "正在启动电池SaaS平台..."

# 1. 启动后端服务
echo "[1/2] 正在后台启动后端服务 (Flask)..."
cd backend
if [ -d "venv" ]; then
    source venv/Scripts/activate || source venv/bin/activate
fi
python run.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 2. 启动管理后台
echo "[2/2] 正在启动管理后台 (Vue)..."
echo "管理后台启动后，请访问: http://localhost:8080"
echo "后端接口地址: http://127.0.0.1:5000"
echo "提示: 按 Ctrl+C 可以停止管理后台，但后端服务可能仍在后台运行(PID: $BACKEND_PID)"

cd frontend_admin
npm run serve

@echo off
title 电池SaaS平台一键启动
echo 正在启动电池SaaS平台...

:: 1. 启动后端服务
echo [1/2] 正在启动后端服务 (Flask)...
start /b cmd /c "cd backend && if exist venv (call venv\Scripts\activate) && python run.py > ..\backend.log 2>&1"

:: 2. 启动管理后台
echo [2/2] 正在启动管理后台 (Vue)...
echo 管理后台启动后，请访问: http://localhost:8083
echo 后端接口地址: http://127.0.0.1:5000
echo ---------------------------------------------------

cd frontend_admin
npm run serve

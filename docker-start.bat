@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo �?                                                           �?
echo �?             电池SaaS平台 - Docker一键启�?               �?
echo �?                                                           �?
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Docker，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 检查Docker是否运行
docker ps >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker未运行，请启动Docker Desktop
    pause
    exit /b 1
)

echo [1/4] 停止旧容�?..
docker-compose down >nul 2>&1

echo [2/4] 构建镜像...
docker-compose build

echo [3/4] 启动服务...
docker-compose up -d

echo [4/4] 等待服务就绪...
timeout /t 10 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo �?                    启动成功�?                            �?
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 访问地址�?
echo   管理后台: http://localhost:8083
echo   后端API:  http://localhost:5000
echo.
echo.
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo.

REM 自动打开浏览�?
start http://localhost:8083

pause

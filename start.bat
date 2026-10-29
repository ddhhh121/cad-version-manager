@echo off
title CAD 版本管理器
echo ========================================
echo CAD 版本管理器 - 启动中...
echo ========================================
echo.

REM 启动后端
echo Starting backend server...
start /B "CAD Backend" "backend\dist\cad-backend.exe"

REM 等待后端启动
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

REM 检查后端是否启动
curl -s http://localhost:8000/api/health >nul 2>nul
if %errorlevel% equ 0 (
    echo Backend started successfully!
) else (
    echo Waiting a bit more...
    timeout /t 2 /nobreak >nul
)

REM 打开浏览器
echo.
echo Opening browser...
start http://localhost:8000

echo.
echo ========================================
echo CAD 版本管理器已启动！
echo.
echo 访问地址: http://localhost:8000
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 保持窗口打开
pause >nul

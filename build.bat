@echo off
echo ========================================
echo CAD 版本管理器 - 构建脚本
echo ========================================
echo.

REM 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python first.
    pause
    exit /b 1
)

echo [1/5] Installing root dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install root dependencies
    pause
    exit /b 1
)
echo.

echo [2/5] Installing frontend dependencies...
cd frontend
call npm install
cd ..
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo.

echo [3/5] Building frontend...
cd frontend
call npm run build
cd ..
if %errorlevel% neq 0 (
    echo ERROR: Failed to build frontend
    pause
    exit /b 1
)
echo.

echo [4/5] Building backend...
cd backend
call build.bat
cd ..
if %errorlevel% neq 0 (
    echo ERROR: Failed to build backend
    pause
    exit /b 1
)
echo.

echo [5/5] Building Electron app...
call npm run dist:win
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Electron app
    pause
    exit /b 1
)
echo.

echo ========================================
echo Build complete!
echo Output: release\CAD版本管理器 Setup 1.0.0.exe
echo ========================================
pause

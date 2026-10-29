@echo off
echo Building CAD Backend...
echo.

REM 安装依赖
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller openpyxl reportlab

REM 清理旧的构建
echo Cleaning old builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM 使用 PyInstaller 打包
echo Building with PyInstaller...
pyinstaller --onefile --name cad-backend app/main.py

echo.
if exist dist\cad-backend.exe (
    echo Build successful!
    echo Output: dist\cad-backend.exe
) else (
    echo Build failed!
)

pause

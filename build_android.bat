@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   CAD 版本管理器 - Android APK 构建
echo ========================================
echo.

set "ROOT_DIR=%CD%"
set "TOOLS_DIR=%ROOT_DIR%\build-tools"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

REM 创建工具目录
if not exist "%TOOLS_DIR%" mkdir "%TOOLS_DIR%"

REM ===== 第一步：检查/安装 Java =====
echo [1/4] 检查 Java 环境...
set "JAVA_FOUND=0"

REM 检查系统 Java
where java >nul 2>&1
if %errorlevel% equ 0 (
    set "JAVA_FOUND=1"
    echo   - 使用系统 Java
)

REM 检查本地 Java
if exist "%TOOLS_DIR%\jdk-17\bin\java.exe" (
    set "JAVA_HOME=%TOOLS_DIR%\jdk-17"
    set "PATH=%JAVA_HOME%\bin;%PATH%"
    set "JAVA_FOUND=1"
    echo   - 使用本地 Java
)

if "%JAVA_FOUND%"=="0" (
    echo   - 未找到 Java，正在下载 OpenJDK 17...
    if not exist "%TOOLS_DIR%\openjdk17.zip" (
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/download-jdk/microsoft-jdk-17.0.12-windows-x64.zip' -OutFile '%TOOLS_DIR%\openjdk17.zip'"
    )
    echo   - 正在解压...
    powershell -Command "Expand-Archive -Path '%TOOLS_DIR%\openjdk17.zip' -DestinationPath '%TOOLS_DIR%' -Force"
    for /d %%i in (%TOOLS_DIR%\jdk-17*) do set "JAVA_HOME=%%i"
    set "PATH=!JAVA_HOME!\bin;!PATH!"
    echo   - Java 安装完成: !JAVA_HOME!
)

java -version 2>&1
echo.

REM ===== 第二步：检查/安装 Android SDK =====
echo [2/4] 检查 Android SDK...
set "ANDROID_HOME=%TOOLS_DIR%\android-sdk"

if not exist "%ANDROID_HOME%\cmdline-tools" (
    echo   - 未找到 Android SDK，正在下载 Command Line Tools...
    if not exist "%TOOLS_DIR%\cmdline-tools.zip" (
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip' -OutFile '%TOOLS_DIR%\cmdline-tools.zip'"
    )
    echo   - 正在解压...
    if not exist "%ANDROID_HOME%\cmdline-tools" mkdir "%ANDROID_HOME%\cmdline-tools"
    powershell -Command "Expand-Archive -Path '%TOOLS_DIR%\cmdline-tools.zip' -DestinationPath '%ANDROID_HOME%\cmdline-tools' -Force"
    ren "%ANDROID_HOME%\cmdline-tools\cmdline-tools" "latest"
    echo   - Android SDK 工具已安装
)

set "PATH=%ANDROID_HOME%\cmdline-tools\latest\bin;%ANDROID_HOME%\platform-tools;%PATH%"

REM 接受许可证并安装必要组件
echo   - 安装 Android SDK 组件...
echo y | sdkmanager --sdk_root="%ANDROID_HOME%" "platform-tools" "platforms;android-34" "build-tools;34.0.0" >nul 2>&1
echo   - Android SDK 就绪
echo.

REM ===== 第三步：准备 Android 项目 =====
echo [3/4] 准备 Android 项目...

cd /d "%FRONTEND_DIR%"

REM 更新 capacitor 配置
echo   - 配置 Capacitor...

REM 添加 Android 平台
if not exist "android" (
    echo   - 添加 Android 平台...
    set "CAPACITOR_ANDROID_SDK_ROOT=%ANDROID_HOME%"
    call npx cap add android 2>&1
)

REM 同步 Web 内容
echo   - 同步 Web 内容...
call npx cap sync android 2>&1
echo.

REM ===== 第四步：构建 APK =====
echo [4/4] 构建 APK...

cd /d "%FRONTEND_DIR%\android"

REM 设置环境变量
set "ANDROID_HOME=%TOOLS_DIR%\android-sdk"
set "ANDROID_SDK_ROOT=%ANDROID_HOME%"

REM 构建
echo   - 正在编译...
call gradlew.bat assembleDebug 2>&1

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   构建成功！
    echo ========================================
    echo.

    REM 复制 APK 到根目录
    copy "app\build\outputs\apk\debug\app-debug.apk" "%ROOT_DIR%\CAD-Manager.apk" >nul

    echo   APK 文件: %ROOT_DIR%\CAD-Manager.apk
    echo.
    echo   安装方法:
    echo   1. 将 CAD-Manager.apk 传到手机
    echo   2. 在手机上打开文件进行安装
    echo   3. 首次使用需要输入服务器地址
    echo.
) else (
    echo.
    echo ========================================
    echo   构建失败
    echo ========================================
    echo   请检查上方的错误信息。
    echo.
)

cd /d "%ROOT_DIR%"
pause

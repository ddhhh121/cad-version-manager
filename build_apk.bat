@echo off
echo ========================================
echo CAD 版本管理器 - Android APK 构建工具
echo ========================================
echo.

REM 检查 Java
where java >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未检测到 Java，正在下载...
    echo.

    REM 下载 OpenJDK 17
    if not exist "tools" mkdir "tools"
    if not exist "tools\jdk17.zip" (
        echo 正在下载 JDK 17...
        powershell -Command "Invoke-WebRequest -Uri 'https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_windows-x64_bin.zip' -OutFile 'tools\jdk17.zip'"
    )

    echo 正在解压 JDK...
    powershell -Command "Expand-Archive -Path 'tools\jdk17.zip' -DestinationPath 'tools' -Force"

    REM 设置 Java 环境
    set JAVA_HOME=%CD%\tools\jdk-17.0.2
    set PATH=%JAVA_HOME%\bin;%PATH%
    echo Java 已安装: %JAVA_HOME%
)

REM 检查 Android SDK
if not exist "%LOCALAPPDATA%\Android\Sdk" (
    echo [提示] 未检测到 Android SDK
    echo.
    echo 请手动安装 Android SDK:
    echo 1. 下载 Android Studio: https://developer.android.com/studio
    echo 2. 或下载 Command Line Tools: https://developer.android.com/studio#command-line-tools-only
    echo.
    echo 安装后请重新运行此脚本。
    pause
    exit /b 1
)

set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
set PATH=%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools;%PATH%

echo ========================================
echo 开始构建 APK...
echo ========================================

cd /d "D:\CAD管理模块\frontend"

REM 添加 Android 平台
echo 添加 Android 平台...
call npx cap add android

REM 同步 Web 内容
echo 同步 Web 内容...
call npx cap sync android

REM 构建 APK
echo 构建 APK...
cd android
call gradlew assembleDebug

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 构建成功！
    echo APK 位置: android\app\build\outputs\apk\debug\app-debug.apk
    echo ========================================
    copy app\build\outputs\apk\debug\app-debug.apk ..\..\CAD-Manager.apk
    echo 已复制到: D:\CAD管理模块\frontend\CAD-Manager.apk
) else (
    echo.
    echo 构建失败，请检查错误信息。
)

pause

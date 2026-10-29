# CAD 版本管理器 - 构建说明

## 环境要求

- **Node.js**: 18+ (推荐 20 LTS)
- **Python**: 3.10+
- **npm**: 9+

## 快速开始

### 开发模式

```bash
# 安装依赖
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# 启动开发服务器
cd ../frontend && npm run dev
```

### 构建桌面版

```bash
# 1. 构建前端
cd frontend && npm run build

# 2. 构建后端（含桌面窗口）
cd ../backend
pip install pyinstaller pywebview
python -m PyInstaller cad_desktop.spec --clean

# 3. 输出位置
# backend/dist/CAD-Desktop.exe
```

### 构建手机版 APK

```bash
# 双击运行 build_android.bat
# 自动下载 Java 和 Android SDK 并构建

# 输出: CAD-Manager.apk
```

## 输出文件

```
CAD管理模块/
├── CAD_Desktop/
│   └── CAD-Desktop.exe        # 桌面版 (双击直接打开)
├── CAD-Manager.apk            # 手机版 (需运行 build_android.bat 生成)
├── frontend/                  # Vue 3 前端
├── backend/                   # FastAPI 后端
└── build_android.bat          # Android 构建脚本
```

## 项目结构

```
CAD管理模块/
├── backend/                   # FastAPI 后端
│   ├── app/                   # 应用代码
│   │   ├── main.py            # 主入口
│   │   ├── desktop_app.py     # 桌面应用入口 (PyWebView)
│   │   ├── routes/            # API 路由
│   │   └── services/          # 业务服务
│   └── cad_desktop.spec       # PyInstaller 打包配置
├── frontend/                  # Vue 3 前端
│   ├── src/                   # 源代码
│   ├── public/                # 静态资源 (含 PWA 配置)
│   └── capacitor.config.ts    # Capacitor 配置
├── CAD_Desktop/               # 桌面版输出目录
├── build_android.bat          # Android 构建脚本
└── BUILD.md                   # 本文件
```

## 常见问题

### Q: 桌面版启动慢？

A: 首次启动需要初始化 WebView2，后续会更快。

### Q: 手机 App 无法连接？

A: 确保手机和电脑在同一 WiFi 下，输入正确的电脑 IP 地址。

### Q: 如何获取电脑 IP？

A: 在命令提示符运行 `ipconfig`，找到 "IPv4 地址"。

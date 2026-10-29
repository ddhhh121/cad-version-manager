# CAD 版本管理器

## 使用方式

### 桌面版（Windows）

双击 `CAD_Desktop/CAD-Desktop.exe` 即可打开。

会弹出一个原生窗口，直接显示软件界面，无需浏览器。

### 手机版（Android）

1. 运行 `build_android.bat` 生成 APK
2. 将 `CAD-Manager.apk` 传到手机
3. 安装并打开 App
4. 输入电脑的 IP 地址（如 `192.168.1.100`）
5. 点击连接

**前提条件：** 手机和电脑在同一 WiFi 下，且电脑端已启动。

## 功能特性

- 项目/系列/版本管理
- DWG/DXF 文件上传和版本控制
- **智能上传：** 拖拽文件到首页，自动识别并归类
- 版本对比和差异查看
- 版本标签和备注
- 文件预览（DXF 转 SVG）
- 数据导出（Excel/PDF）
- 数据备份和恢复
- 删除历史记录

## 系统要求

### 桌面版
- Windows 10/11
- 无需安装 Python 或 Node.js

### 手机版
- Android 8.0+
- 需与电脑在同一局域网

## 端口说明

默认端口：8000

## 数据存储

- 数据库：`backend/cadver.db`
- 上传文件：`backend/uploads/`
- 备份文件：`backend/backups/`

## 常见问题

### Q: 桌面版启动后没有窗口？

A: 等待几秒钟，WebView2 初始化需要时间。

### Q: 手机 App 无法连接？

A: 检查：
1. 手机和电脑是否在同一 WiFi
2. 电脑端是否已启动 CAD-Desktop.exe
3. IP 地址是否正确

### Q: 如何获取电脑 IP？

A: 按 Win+R，输入 cmd 回车，输入 `ipconfig`，找到 "IPv4 地址"。

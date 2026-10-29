# CAD 图纸版本管理器

面向机械工程师（毕设 / 日常工程）的图纸版本管理系统：管理 DWG/DXF 图纸文件的版本链，跟踪最新版本、对比版本差异，防止误用旧版本。提供 Web 端 + Windows 桌面端 + Android 手机端。

## 功能特性

- 项目 / 图纸系列 / 版本 三级管理，最新版本置顶并高亮「当前」标签
- DWG/DXF 文件上传与版本控制：SHA256 去重、图纸编号自动提取归类（自动剥离 `_bak`、`_副本`、`_copy` 等后缀）
- 版本对比与差异查看（Diff 表）、旧版本点击提醒
- 文件预览（DXF → SVG 回退占位图）、Ctrl+滚轮四级缩略图缩放
- 数据导出（Excel / PDF）、备份与恢复、删除历史记录
- 桌面端（Windows，免安装直接运行）与手机端（Android APK，局域网连接）

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 前端 | Vue 3 + Vite + Vue Router |
| 缩略图 | ODA File Converter / LibreCAD（失败回退 SVG 占位图） |
| DXF 解析 | ezdxf（提取 MTEXT 实体） |
| 桌面打包 | PyInstaller + PyWebView |
| 移动端 | Capacitor |

## 数据模型

```
Project (项目)
  └── DrawingSeries (图纸系列，按图纸编号分组)
        └── DrawingVersion (版本，按 version_number 降序)
```

- 版本去重：同一系列内 `file_hash`（SHA256）不可重复
- 级联删除：删除项目 → 删除所有系列和版本 + 磁盘文件

## 快速开始

### 开发模式

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### 构建桌面版（Windows）

```bash
cd backend
pip install pyinstaller pywebview
python -m PyInstaller cad_desktop.spec --clean
# 输出：backend/dist/CAD-Desktop.exe
```

### 构建手机版（Android）

```bash
# 双击运行 build_android.bat，自动下载 Java 与 Android SDK 并构建
# 输出：CAD-Manager.apk（手机与电脑需在同一 WiFi）
```

## 项目结构

```
CAD管理模块/
├── backend/            # FastAPI 后端（app/routes、app/services）
├── frontend/           # Vue 3 前端（src/views、src/api）
├── electron/           # 桌面端封装
├── CAD_Desktop/        # 桌面版输出目录（CAD-Desktop.exe）
├── build_android.bat   # Android 构建脚本
├── BUILD.md            # 构建说明
└── LICENSE.txt         # MIT License
```

## License

[MIT](./LICENSE.txt)

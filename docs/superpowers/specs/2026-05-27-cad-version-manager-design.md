# CAD 图纸版本管理器 — 设计文档

## 概述

面向机械工程师的 Web 应用，管理 DWG/DXF 图纸文件的版本。解决多个文件夹散落图纸副本、无法判断哪个是最新版的痛点。

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | FastAPI (Python 3.12) |
| 数据库 | SQLite |
| 文件存储 | 本地文件系统 |
| 前端 | Vue 3 + Vite |
| DXF 解析 | ezdxf |
| DWG 缩略图 | 外部命令调用（用户本机 AutoCAD/O DA File Converter） |

## 架构

```
浏览器 (Vue 3 SPA)
    │
    ▼
FastAPI 后端
    ├── SQLite (元数据: 项目、图纸系列、版本)
    ├── 文件存储 (projects/{id}/{series_id}/{version}/)
    └── 缩略图生成器 (调用外部工具)
```

## 数据模型

### Project
- id, name, description, created_at

### DrawingSeries（同一图号的版本链）
- id, project_id, drawing_number, created_at

### DrawingVersion
- id, series_id
- version_number (auto-increment within series: v1, v2, v3...)
- filename, file_hash (SHA256), file_path, file_size
- thumbnail_path (nullable)
- metadata (JSON: DXF 标题栏字段)
- change_note (用户填写)
- created_at

**约束**: 同一 DrawingSeries 下 file_hash 不可重复。

## 版本识别流程

```
上传文件
  → 计算 SHA256 → 同一 series 已存在？ → 拒绝（无变化）
  → 从文件名提取图号（正则匹配 A0-A4 + 零件名）
  → 匹配已有 DrawingSeries？ → 归入 / 新建
  → 尝试生成缩略图 → 存储 → 创建 DrawingVersion
```

## API（10 端点）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/projects | 项目列表 |
| POST | /api/projects | 创建项目 |
| GET | /api/projects/{id} | 项目详情 + 图纸系列列表 |
| POST | /api/projects/{id}/upload | 上传图纸 |
| GET | /api/series/{id} | 图纸系列详情 |
| GET | /api/series/{id}/versions | 版本列表 |
| POST | /api/series/{id}/versions/{vid}/note | 编辑变更说明 |
| GET | /api/versions/{id} | 版本详情 |
| GET | /api/versions/{id}/thumbnail | 缩略图 |
| GET | /api/versions/{id}/download | 下载原文件 |
| GET | /api/compare/{vid1}/{vid2} | 对比两个版本 |

## 前端页面（4 页）

### 1. 项目列表
卡片网格，每个项目显示名称、图纸系列数、最近更新时间。

### 2. 项目详情
- 左侧：图纸系列列表（按图号排序），每项显示最新版本缩略图 + "当前最新"标签
- 右侧：选中系列的所有版本时间线
- 上传按钮：拖拽或点击上传

### 3. 版本对比
- 新版在上（绿色顶条 + 实线边框 + "当前"标签）
- 旧版在下（灰色顶条 + 虚线边框 + "上一个"标签）
- 两张缩略图等大，并排展示
- 差异表：变化行红色标线 + 浅红背景，未变化行绿色标线
- 新版本信息始终在右侧，"──▶" 箭头指向新

### 4. 智能旧版拦截
- 点击非最新版本时弹出提示：当前是旧版 + 指向最新版位置
- 默认按钮"查看最新"，次要按钮"继续看当前"

## 错误处理

| 场景 | 行为 |
|---|---|
| 非 DWG/DXF 文件 | 拒绝，提示格式 |
| 缩略图生成失败 | 占位图标 |
| 重复 hash | 提示"版本已存在" |
| 文件 > 50MB | 拒绝上传 |
| DWG 解析失败 | 降级：纯文件级管理，不影响功能 |

## 测试策略

- 后端 API：pytest + httpx（上传、版本链、对比、边界情况）
- 核心逻辑：pytest（图号提取、hash 去重、版本递增）
- 前端：初期手动走通核心流程

## 不做什么

- 不尝试完整解析 DWG 内容（格式私有、不可靠）
- 不做实时协作
- 不做云端部署（第一版本地运行）
- 不做用户认证系统（单用户/小团队信任模式）

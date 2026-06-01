# CloudNest 使用文档

> **版本**: 1.0.0 | **最后更新**: 2026-06-01 | **技术栈**: Flask 3.x + Vue 3 + Naive UI

---

## 目录

1. [项目简介](#1-项目简介)
2. [环境要求](#2-环境要求)
3. [安装部署](#3-安装部署)
4. [配置说明](#4-配置说明)
5. [项目架构](#5-项目架构)
6. [功能模块详解](#6-功能模块详解)
7. [API 接口文档](#7-api-接口文档)
8. [数据库设计](#8-数据库设计)
9. [前端架构](#9-前端架构)
10. [安全机制](#10-安全机制)
11. [测试](#11-测试)
12. [Docker 部署](#12-docker-部署)
13. [常见问题](#13-常见问题)
14. [开发指南](#14-开发指南)

---

## 1. 项目简介

CloudNest 是一个基于 Flask + Vue 3 的现代化个人云端管理平台，提供文件管理、笔记系统、任务看板等核心功能，支持多用户注册登录、跨设备访问，UI 采用现代极简风格。

### 核心功能

| 模块 | 功能 |
|------|------|
| 用户系统 | 注册/登录/JWT 双令牌/头像/密码管理/设备管理/两步验证/账号注销 |
| 文件管理 | 上传/下载/文件夹/回收站/分享链接（密码+过期时间） |
| 笔记系统 | Markdown 编辑器/笔记本/标签/全文搜索/版本历史/导出 |
| 任务看板 | 看板列/任务卡片/拖拽排序/列表视图/日历视图/优先级 |
| 仪表盘 | 统计概览/今日待办/快速入口/最近笔记 |
| 设置中心 | 个人资料/账号安全/设备管理/主题切换/语言切换/数据导出 |

### 技术栈

| 层次 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 3.x |
| ORM | SQLAlchemy | 2.x |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） | - |
| 认证 | Flask-JWT-Extended + bcrypt | 4.7 / 4.3 |
| 前端框架 | Vue 3 (Composition API) | 3.5 |
| UI 组件 | Naive UI | 2.44 |
| 状态管理 | Pinia | 3.0 |
| 构建工具 | Vite | 5.x |
| HTTP 客户端 | Axios | 1.16 |

---

## 2. 环境要求

### 开发环境

| 依赖 | 最低版本 | 推荐版本 |
|------|----------|----------|
| Python | 3.10 | 3.12 |
| Node.js | 18.0 | 20.x |
| npm | 8.0 | 10.x |
| 操作系统 | Windows 10 / macOS 12 / Ubuntu 20.04 | - |

### 生产环境（Docker 部署）

| 依赖 | 最低版本 |
|------|----------|
| Docker | 20.10 |
| Docker Compose | 2.0 |

---

## 3. 安装部署

### 3.1 克隆项目

```bash
git clone <repository-url>
cd a_web
```

### 3.2 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 编辑 .env 文件，修改密钥
# SECRET_KEY=你的随机密钥（至少32位）
# JWT_SECRET_KEY=你的另一个随机密钥
```

### 3.3 前端安装

```bash
cd frontend

# 安装依赖
npm install
```

### 3.4 启动开发服务器

**后端**（终端 1）：
```bash
cd backend
flask run --port=5000
```

**前端**（终端 2）：
```bash
cd frontend
npm run dev
```

访问 http://localhost:5173

### 3.5 验证安装

```bash
# 检查后端
curl http://localhost:5000/api/v1/docs
# 应返回 OpenAPI JSON

# 检查前端
# 浏览器访问 http://localhost:5173 应看到着陆页
```

---

## 4. 配置说明

### 4.1 环境变量（backend/.env）

| 变量 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| `FLASK_APP` | Flask 入口 | 否 | `app.py` |
| `FLASK_ENV` | 运行环境 | 否 | `development` |
| `SECRET_KEY` | Flask 密钥 | **生产环境必填** | `dev-secret-key-change-in-production` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | **生产环境必填** | `jwt-secret-key-change-in-production` |
| `DATABASE_URL` | 数据库连接串 | 否 | `sqlite:///cloudnest.db` |

### 4.2 配置类说明

| 配置类 | 环境 | 特点 |
|--------|------|------|
| `DevelopmentConfig` | 开发 | DEBUG=True，SQLite 文件数据库 |
| `TestingConfig` | 测试 | 内存数据库，限流禁用 |
| `ProductionConfig` | 生产 | DEBUG=False，需配置 DATABASE_URL |

### 4.3 生成安全密钥

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

将输出的两串随机字符串分别填入 `.env` 的 `SECRET_KEY` 和 `JWT_SECRET_KEY`。

---

## 5. 项目架构

### 5.1 目录结构

```
a_web/
├── backend/                    # 后端
│   ├── app.py                  # Flask 应用工厂
│   ├── config.py               # 配置类
│   ├── extensions.py           # 扩展初始化
│   ├── models/                 # 数据模型
│   │   ├── user.py             # 用户模型
│   │   ├── file.py             # 文件/分享模型
│   │   ├── note.py             # 笔记/笔记本/标签模型
│   │   ├── task.py             # 任务/看板列模型
│   │   ├── login_record.py     # 登录记录模型
│   │   └── trusted_device.py   # 信任设备模型
│   ├── api/v1/                 # RESTful API
│   │   ├── auth.py             # 认证接口（8个）
│   │   ├── users.py            # 用户接口（8个）
│   │   ├── files.py            # 文件接口（14个）
│   │   ├── notes.py            # 笔记接口（15个）
│   │   ├── tasks.py            # 任务接口（13个）
│   │   ├── settings.py         # 设置接口（1个）
│   │   └── docs.py             # API 文档（2个）
│   ├── services/               # 业务逻辑层
│   ├── middleware/              # 中间件
│   ├── utils/                  # 工具函数
│   ├── tests/                  # 单元测试（31个）
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # 前端
│   ├── src/
│   │   ├── views/              # 页面组件（17个）
│   │   ├── components/         # 通用组件
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── api/                # Axios 封装
│   │   ├── router/             # 路由配置
│   │   ├── composables/        # 组合式函数
│   │   └── locales/            # 国际化
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

### 5.2 后端架构分层

```
请求 → 中间件(JWT/限流/错误处理) → API 路由 → Service 业务逻辑 → Model 数据模型 → 数据库
```

- **API 层**（`api/v1/`）：接收请求、参数校验、返回响应
- **Service 层**（`services/`）：业务逻辑处理
- **Model 层**（`models/`）：数据模型定义、ORM 映射
- **Middleware 层**（`middleware/`）：JWT 验证、限流、全局错误处理
- **Utils 层**（`utils/`）：验证器、TOTP、设备指纹等工具

### 5.3 前端架构

```
用户操作 → Vue 组件 → Pinia Store → Axios API → 后端
                ↑                          ↓
          Vue Router ←────── 响应数据 ←────┘
```

- **Views**：页面级组件
- **Components**：可复用 UI 组件
- **Stores**：Pinia 状态管理
- **API**：Axios 实例 + 请求/响应拦截器
- **Composables**：组合式函数（主题、i18n 等）

---

## 6. 功能模块详解

### 6.1 用户系统

#### 注册与登录

- **注册**：邮箱 + 用户名 + 密码，邮箱和用户名唯一
- **登录**：邮箱 + 密码，返回 JWT 双令牌
- **令牌策略**：
  - Access Token：30 分钟有效，用于 API 认证
  - Refresh Token：7 天有效，用于刷新 Access Token
  - 前端拦截器自动检测 401 → 调用 `/auth/refresh` → 续签

#### 两步验证（2FA）

1. 进入 **设置 → 账号安全 → 启用两步验证**
2. 系统生成 TOTP 密钥，显示 otpauth URI
3. 使用验证器 App（Google Authenticator、Authy 等）添加
4. 输入 App 显示的 6 位验证码
5. 验证成功后 2FA 启用

#### 设备管理

- 登录时自动记录 IP、User-Agent、设备指纹
- 可查看登录历史、信任设备列表
- 支持移除信任设备

#### 账号注销

- 注销后进入 7 天冷静期（软删除）
- 冷静期内数据保留，可联系管理员恢复

### 6.2 文件管理

#### 文件上传

- 支持拖拽上传、多文件同时上传
- 上传时显示进度条
- MIME 类型白名单 + 文件头魔数检测
- 最大文件大小：50MB

#### 文件夹管理

- 支持新建、重命名、删除文件夹
- 支持文件/文件夹移动
- 自引用树形结构（parent_id）

#### 回收站

- 删除的文件进入回收站（软删除）
- 支持恢复、永久删除
- 30 天自动清理（需 Celery）

#### 文件分享

- 生成分享链接（短码）
- 支持密码保护
- 支持设置过期时间
- 分享页面免登录访问

#### 存储统计

- 文件数量、文件夹数量、总占用空间

### 6.3 笔记系统

#### 编辑器

- Markdown 编辑 + 实时预览（左右分屏）
- 自动保存（防抖 2 秒）
- 版本历史（保留最近版本）
- 导出为 Markdown / HTML

#### 笔记本

- 笔记本分类管理
- 支持自定义颜色
- 笔记可归属到笔记本

#### 标签

- 标签管理（创建、删除）
- 笔记和任务共享标签系统
- 支持按标签筛选

#### 搜索

- 全文搜索（标题 + 内容）
- 支持按笔记本筛选

### 6.4 任务看板

#### 看板视图

- 自定义看板列（如：待办、进行中、已完成）
- 任务卡片支持拖拽排序
- 任务卡片显示优先级颜色、截止日期

#### 列表视图

- 表格形式展示所有任务
- 支持按优先级、状态筛选

#### 日历视图

- 月历展示，显示任务截止日期
- 支持月份切换
- 高亮今日

#### 任务属性

| 属性 | 说明 |
|------|------|
| 标题 | 必填 |
| 描述 | 可选 |
| 优先级 | 低(0) / 中(1) / 高(2) / 紧急(3) |
| 截止日期 | 可选，日历视图展示 |
| 看板列 | 所属列 |
| 排序位置 | 拖拽排序用 |

### 6.5 仪表盘

- **统计卡片**：文件数、笔记数、任务数、存储用量
- **快速操作**：上传文件、新建笔记、新建任务
- **今日待办**：显示今日到期的任务
- **最近笔记**：显示最近更新的 5 篇笔记
- **骨架屏**：加载时显示占位动画

### 6.6 设置中心

| 子页面 | 功能 |
|--------|------|
| 个人资料 | 修改用户名、简介、头像 |
| 账号安全 | 修改密码、两步验证、数据导出、账号注销 |
| 设备管理 | 信任设备列表、登录历史 |
| 界面偏好 | 主题切换（浅色/深色/跟随系统）、语言切换（中/英） |

---

## 7. API 接口文档

### 7.1 基础信息

- **Base URL**: `/api/v1`
- **认证方式**: Bearer Token（JWT）
- **请求格式**: `application/json`（文件上传用 `multipart/form-data`）
- **响应格式**: `application/json`

### 7.2 认证方式

```
Authorization: Bearer <access_token>
```

### 7.3 错误响应格式

```json
{
  "error": "错误描述信息"
}
```

| HTTP 状态码 | 含义 |
|-------------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 / 令牌无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如邮箱已注册） |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### 7.4 认证接口

#### POST /auth/register — 用户注册

**请求体**：
```json
{
  "email": "user@example.com",
  "username": "myname",
  "password": "123456"
}
```

**校验规则**：
- 邮箱：有效邮箱格式
- 用户名：3-20 位，仅字母数字下划线
- 密码：至少 6 位

**成功响应**（201）：
```json
{
  "message": "注册成功",
  "user": { "id": 1, "email": "...", "username": "...", ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

**限流**：5 次 / 5 分钟 / IP

#### POST /auth/login — 用户登录

**请求体**：
```json
{
  "email": "user@example.com",
  "password": "123456"
}
```

**成功响应**（200）：
```json
{
  "message": "登录成功",
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

**限流**：10 次 / 5 分钟 / IP

#### POST /auth/refresh — 刷新令牌

**请求头**：`Authorization: Bearer <refresh_token>`

**成功响应**（200）：
```json
{ "access_token": "eyJ..." }
```

#### POST /auth/logout — 登出

**请求头**：`Authorization: Bearer <refresh_token>`

**成功响应**（200）：
```json
{ "message": "已登出" }
```

#### GET /auth/me — 获取当前用户

**请求头**：`Authorization: Bearer <access_token>`

**成功响应**（200）：
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "myname",
    "avatar_url": "",
    "bio": "",
    "is_2fa_enabled": false,
    "is_active": true,
    "created_at": "2026-06-01T00:00:00",
    "updated_at": "2026-06-01T00:00:00"
  }
}
```

#### POST /auth/2fa/setup — 生成 2FA 密钥

**成功响应**（200）：
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "otpauth_uri": "otpauth://totp/CloudNest:user@example.com?secret=..."
}
```

#### POST /auth/2fa/verify — 验证并启用 2FA

**请求体**：`{ "code": "123456" }`

#### POST /auth/2fa/disable — 关闭 2FA

**请求体**：`{ "code": "123456" }`

### 7.5 用户接口

#### GET /users/profile — 获取个人资料

#### PUT /users/profile — 更新个人资料

**请求体**：
```json
{ "username": "newname", "bio": "我的简介" }
```

#### POST /users/avatar — 上传头像

**请求格式**：`multipart/form-data`，字段名 `avatar`

#### PUT /users/password — 修改密码

**请求体**：
```json
{
  "old_password": "原密码",
  "new_password": "新密码"
}
```

#### GET /users/login-history — 登录历史

**成功响应**（200）：
```json
{
  "records": [
    {
      "id": 1,
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "location": "",
      "is_new_device": true,
      "login_at": "2026-06-01T00:00:00"
    }
  ]
}
```

#### GET /users/devices — 信任设备列表

#### DELETE /users/devices/:device_id — 移除信任设备

#### DELETE /users/account — 注销账号

### 7.6 文件接口

#### GET /files — 文件列表

**查询参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| `parent_id` | integer | 父文件夹 ID，不传则为根目录 |

**成功响应**（200）：
```json
{
  "files": [
    {
      "id": 1,
      "name": "文档",
      "is_folder": true,
      "file_size": 0,
      "mime_type": "",
      "parent_id": null,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

#### POST /files — 上传文件

**请求格式**：`multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | File | 文件内容 |
| `parent_id` | integer | 可选，目标文件夹 ID |

#### POST /files/folder — 新建文件夹

**请求体**：
```json
{ "name": "我的文件夹", "parent_id": null }
```

#### GET /files/:id — 文件详情

#### PUT /files/:id — 重命名 / 移动

**请求体**：
```json
{ "name": "新名称", "parent_id": 5 }
```

#### DELETE /files/:id — 移入回收站

#### POST /files/:id/restore — 从回收站恢复

#### DELETE /files/:id/permanent — 永久删除

#### GET /files/:id/download — 下载文件

**响应**：文件二进制流

#### POST /files/:id/share — 创建分享链接

**请求体**：
```json
{ "expires_hours": 24, "password": "可选密码" }
```

**成功响应**（201）：
```json
{
  "share": {
    "id": 1,
    "share_code": "abc123",
    "expires_at": "...",
    "view_count": 0
  }
}
```

#### GET /files/stats — 存储统计

**成功响应**（200）：
```json
{ "file_count": 10, "folder_count": 3, "total_size": 1048576 }
```

#### GET /trash — 回收站列表

#### POST /trash/empty — 清空回收站

#### GET /share/:code — 访问分享（免登录）

**查询参数**：`password`（如果分享设置了密码）

### 7.7 笔记接口

#### GET /notes — 笔记列表

**查询参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| `notebook_id` | integer | 按笔记本筛选 |
| `search` | string | 全文搜索关键词 |
| `is_archived` | boolean | 是否归档 |

#### POST /notes — 创建笔记

**请求体**：
```json
{
  "title": "笔记标题",
  "content": "# Markdown 内容",
  "notebook_id": 1,
  "tags": [1, 2]
}
```

#### GET /notes/:id — 笔记详情（含内容）

#### PUT /notes/:id — 更新笔记

**请求体**：
```json
{
  "title": "新标题",
  "content": "新内容",
  "is_pinned": true
}
```

**行为**：每次更新自动创建版本快照

#### DELETE /notes/:id — 删除笔记

#### GET /notes/:id/versions — 版本历史

**成功响应**（200）：
```json
{
  "versions": [
    { "id": 1, "version_num": 1, "content": "...", "created_at": "..." },
    { "id": 2, "version_num": 2, "content": "...", "created_at": "..." }
  ]
}
```

#### POST /notes/:id/versions/:version_id/restore — 恢复版本

#### GET /notes/:id/export/:fmt — 导出笔记

**路径参数**：`fmt` = `markdown` 或 `html`

**响应**：文件下载

#### GET /notebooks — 笔记本列表

#### POST /notebooks — 创建笔记本

**请求体**：
```json
{ "name": "工作笔记", "color": "#6366f1" }
```

#### PUT /notebooks/:id — 更新笔记本

#### DELETE /notebooks/:id — 删除笔记本

#### GET /tags — 标签列表

#### POST /tags — 创建标签

**请求体**：
```json
{ "name": "重要", "color": "#ef4444" }
```

#### DELETE /tags/:id — 删除标签

### 7.8 任务接口

#### GET /tasks — 任务列表

**查询参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| `column_id` | integer | 按看板列筛选 |
| `priority` | integer | 按优先级筛选 |
| `due_date` | string | 按截止日期筛选，`today` 表示今日 |

#### POST /tasks — 创建任务

**请求体**：
```json
{
  "title": "完成报告",
  "description": "周五前提交",
  "column_id": 1,
  "priority": 2,
  "due_date": "2026-06-05"
}
```

#### GET /tasks/:id — 任务详情

#### PUT /tasks/:id — 更新任务

#### DELETE /tasks/:id — 删除任务

#### PUT /tasks/:id/move — 移动任务到其他列

**请求体**：
```json
{ "column_id": 2, "position": 0 }
```

#### PUT /tasks/reorder — 批量调整排序

**请求体**：
```json
{
  "items": [
    { "id": 1, "position": 2 },
    { "id": 2, "position": 1 }
  ]
}
```

#### GET /tasks/today — 今日待办

#### GET /tasks/stats — 任务统计

**成功响应**（200）：
```json
{ "total": 10, "today": 3, "overdue": 1, "by_status": { "pending": 5, "in_progress": 3, "done": 2 } }
```

#### GET /task-columns — 看板列列表

#### POST /task-columns — 创建看板列

**请求体**：
```json
{ "name": "待办", "color": "#6366f1" }
```

#### PUT /task-columns/:id — 更新看板列

#### DELETE /task-columns/:id — 删除看板列

### 7.9 设置接口

#### GET /settings/export — 导出所有数据

**响应**：JSON 文件下载，包含用户所有文件信息、笔记、任务

### 7.10 API 文档接口

#### GET /docs — OpenAPI JSON

返回完整的 OpenAPI 3.0 规范 JSON。

#### GET /docs/ui — Swagger UI

返回可交互的 Swagger UI 页面（需联网加载 CDN 资源）。

---

## 8. 数据库设计

### 8.1 ER 关系图

```
users ──┬── login_records
        ├── trusted_devices
        ├── files ──── file_shares
        │    └── files (自引用)
        ├── notebooks ──── notes ──── note_versions
        │                        └── note_tags ←── tags
        ├── task_columns ──── tasks ──── task_tags ←── tags
        └── refresh_tokens
```

### 8.2 表清单

| 表名 | 说明 | 记录数 |
|------|------|--------|
| `users` | 用户主表 | 用户数 |
| `login_records` | 登录记录 | 每次登录一条 |
| `trusted_devices` | 信任设备 | 每个设备一条 |
| `files` | 文件/文件夹 | 文件数+文件夹数 |
| `file_shares` | 分享链接 | 每个分享一条 |
| `notebooks` | 笔记本 | 用户创建的笔记本数 |
| `notes` | 笔记 | 笔记数 |
| `note_versions` | 笔记版本 | 每次保存一条 |
| `tags` | 标签 | 标签数 |
| `note_tags` | 笔记-标签关联 | 多对多 |
| `task_columns` | 看板列 | 默认 3 列 |
| `tasks` | 任务 | 任务数 |
| `task_tags` | 任务-标签关联 | 多对多 |

---

## 9. 前端架构

### 9.1 路由结构

```
/                           → 着陆页
/login                      → 登录页
/register                   → 注册页
/share/:code                → 分享文件查看（免登录）

/dashboard                  → 仪表盘布局
├── /                       → 仪表盘首页
├── /files                  → 文件管理
├── /files/:folderId        → 文件夹内浏览
├── /files/trash            → 回收站
├── /notes                  → 笔记列表
├── /notes/:id              → 笔记编辑
├── /tasks                  → 任务看板（重定向到 board）
├── /tasks/board            → 看板视图
├── /tasks/list             → 列表视图
├── /tasks/calendar         → 日历视图
├── /settings/profile       → 个人资料
├── /settings/account       → 账号安全
├── /settings/devices       → 设备管理
└── /settings/appearance    → 界面偏好
```

### 9.2 状态管理（Pinia Stores）

| Store | 文件 | 状态 |
|-------|------|------|
| `auth` | `stores/auth.js` | user, accessToken, refreshToken, isLoggedIn |
| `theme` | `stores/theme.js` | isDark |

### 9.3 API 拦截器

`src/api/index.js` 中的 Axios 拦截器实现：

- **请求拦截**：自动附加 `Authorization: Bearer <token>`
- **响应拦截**：检测 401 → 自动调用 `/auth/refresh` → 续签后重试原请求
- **刷新失败**：清除令牌 → 跳转登录页

### 9.4 主题系统

`composables/useTheme.js` 提供三种主题模式：

| 模式 | 说明 |
|------|------|
| `light` | 浅色主题 |
| `dark` | 深色主题 |
| `system` | 跟随操作系统设置 |

深色模式通过 Naive UI 的 `darkTheme` 实现，自动切换组件配色。

### 9.5 国际化

`locales/` 目录提供中英双语支持：

- `zh.js` — 中文语言包
- `en.js` — 英文语言包
- `index.js` — `useI18n()` 组合式函数

在设置 → 界面偏好中切换语言，选择保存在 `localStorage`。

---

## 10. 安全机制

### 10.1 认证安全

| 机制 | 说明 |
|------|------|
| 密码哈希 | bcrypt，自动加盐 |
| JWT 双令牌 | Access Token 30 分钟 + Refresh Token 7 天 |
| 令牌刷新 | 前端自动检测 401 并续签 |
| 两步验证 | TOTP（RFC 6238），纯 Python 实现 |

### 10.2 接口安全

| 机制 | 说明 |
|------|------|
| 请求限流 | 注册 5 次/5 分钟，登录 10 次/5 分钟（基于 IP） |
| CORS | 仅允许 `/api/*` 路径跨域 |
| 文件上传 | MIME 白名单 + 文件头魔数检测 + 50MB 大小限制 |
| SQL 注入 | SQLAlchemy ORM 参数化查询 |
| XSS | Vue 模板自动转义 |

### 10.3 设备安全

| 机制 | 说明 |
|------|------|
| 登录记录 | 每次登录记录 IP、User-Agent、时间 |
| 设备指纹 | MD5(User-Agent + IP) 生成设备标识 |
| 信任设备 | 用户可管理信任设备列表 |
| 异地检测 | 新设备/新 IP 登录时标记为新设备 |

---

## 11. 测试

### 11.1 运行测试

```bash
cd backend
pip install pytest
python -m pytest tests/ -v
```

### 11.2 测试覆盖

| 测试文件 | 测试数量 | 覆盖模块 |
|----------|----------|----------|
| `test_auth.py` | 9 | 注册、登录、令牌刷新、获取用户 |
| `test_files.py` | 7 | 文件夹、上传、列表、重命名、删除恢复、分享、统计 |
| `test_notes.py` | 8 | 笔记本、笔记 CRUD、搜索、版本、标签、删除、导出 |
| `test_tasks.py` | 7 | 看板列、任务 CRUD、移动、统计、排序 |
| **总计** | **31** | **全部通过** |

### 11.3 测试环境配置

测试使用内存 SQLite 数据库，自动创建和销毁，不影响开发数据库。

---

## 12. Docker 部署

### 12.1 快速部署

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env，修改 SECRET_KEY 和 JWT_SECRET_KEY

# 2. 构建并启动
docker compose up -d --build

# 3. 访问
# http://localhost
```

### 12.2 容器说明

| 容器 | 端口 | 说明 |
|------|------|------|
| `cloudnest-backend` | 5000 | Flask + Gunicorn（4 workers） |
| `cloudnest-frontend` | 80 | Nginx + Vue SPA |

### 12.3 Nginx 配置

- 静态资源：Vue SPA 路由（`try_files $uri /index.html`）
- API 代理：`/api/` → `http://backend:5000`
- 上传文件代理：`/uploads/` → `http://backend:5000`
- Gzip 压缩：JS/CSS/JSON/XML
- 静态资源缓存：30 天

### 12.4 数据持久化

- 上传文件：Docker Volume `uploads` → `/app/uploads`
- 数据库：SQLite 文件（可挂载外部卷）

### 12.5 常用命令

```bash
# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 重新构建
docker compose up -d --build

# 进入容器
docker exec -it cloudnest-backend bash
```

---

## 13. 常见问题

### Q: 启动报错 `ModuleNotFoundError: No module named 'flask'`

**A**: 确保已激活虚拟环境并安装依赖：
```bash
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Q: 前端无法连接后端 API

**A**: 检查以下几点：
1. 后端是否在 `localhost:5000` 运行
2. `vite.config.js` 中的代理配置是否正确
3. 浏览器控制台是否有 CORS 错误

### Q: 上传文件失败

**A**: 可能原因：
1. 文件超过 50MB 限制
2. 文件类型不在白名单内
3. 后端 `uploads/` 目录无写入权限

### Q: 两步验证验证码错误

**A**: 确保手机时间和服务器时间同步，TOTP 允许前后各 30 秒的偏差。

### Q: Docker 部署后无法访问

**A**: 检查：
1. `docker compose ps` 确认容器运行中
2. `docker compose logs` 查看错误日志
3. 确保端口 80 未被占用

### Q: 如何切换数据库到 PostgreSQL

**A**: 修改 `.env`：
```
DATABASE_URL=postgresql://user:password@localhost:5432/cloudnest
```
并安装 `psycopg2-binary`：
```bash
pip install psycopg2-binary
```

---

## 14. 开发指南

### 14.1 添加新的 API 接口

1. 在 `models/` 中定义数据模型
2. 在 `services/` 中实现业务逻辑
3. 在 `api/v1/` 中定义路由
4. 在 `api/v1/__init__.py` 中注册蓝图
5. 编写测试

### 14.2 添加新的前端页面

1. 在 `views/dashboard/` 中创建 Vue 组件
2. 在 `router/index.js` 中添加路由
3. 在 `stores/` 中管理状态
4. 在 `api/` 中封装 API 调用
5. 在 `components/layout/Sidebar.vue` 中添加菜单项

### 14.3 代码规范

- 后端：遵循 PEP 8，使用 type hints
- 前端：使用 `<script setup>` + Composition API
- 提交：每个子功能一个 commit
- 测试：每个 API 端点至少一个测试用例

### 14.4 Git 提交建议

```bash
# 功能
git commit -m "feat: 添加文件分享功能"

# 修复
git commit -m "fix: 修复登录限流器在测试中的问题"

# 文档
git commit -m "docs: 添加使用文档"

# 重构
git commit -m "refactor: 优化笔记版本存储逻辑"
```

---

## 附录 A：完整 API 端点列表

| # | 方法 | 路径 | 说明 |
|---|------|------|------|
| 1 | POST | /auth/register | 用户注册 |
| 2 | POST | /auth/login | 用户登录 |
| 3 | POST | /auth/refresh | 刷新令牌 |
| 4 | POST | /auth/logout | 登出 |
| 5 | GET | /auth/me | 获取当前用户 |
| 6 | POST | /auth/2fa/setup | 生成 2FA 密钥 |
| 7 | POST | /auth/2fa/verify | 验证 2FA |
| 8 | POST | /auth/2fa/disable | 关闭 2FA |
| 9 | GET | /users/profile | 获取个人资料 |
| 10 | PUT | /users/profile | 更新个人资料 |
| 11 | POST | /users/avatar | 上传头像 |
| 12 | PUT | /users/password | 修改密码 |
| 13 | GET | /users/login-history | 登录历史 |
| 14 | GET | /users/devices | 信任设备 |
| 15 | DELETE | /users/devices/:id | 移除设备 |
| 16 | DELETE | /users/account | 注销账号 |
| 17 | GET | /files | 文件列表 |
| 18 | POST | /files | 上传文件 |
| 19 | POST | /files/folder | 新建文件夹 |
| 20 | GET | /files/:id | 文件详情 |
| 21 | PUT | /files/:id | 重命名/移动 |
| 22 | DELETE | /files/:id | 移入回收站 |
| 23 | POST | /files/:id/restore | 恢复文件 |
| 24 | DELETE | /files/:id/permanent | 永久删除 |
| 25 | GET | /files/:id/download | 下载文件 |
| 26 | POST | /files/:id/share | 创建分享 |
| 27 | GET | /files/stats | 存储统计 |
| 28 | GET | /trash | 回收站列表 |
| 29 | POST | /trash/empty | 清空回收站 |
| 30 | GET | /share/:code | 访问分享 |
| 31 | GET | /notebooks | 笔记本列表 |
| 32 | POST | /notebooks | 创建笔记本 |
| 33 | PUT | /notebooks/:id | 更新笔记本 |
| 34 | DELETE | /notebooks/:id | 删除笔记本 |
| 35 | GET | /tags | 标签列表 |
| 36 | POST | /tags | 创建标签 |
| 37 | DELETE | /tags/:id | 删除标签 |
| 38 | GET | /notes | 笔记列表 |
| 39 | POST | /notes | 创建笔记 |
| 40 | GET | /notes/:id | 笔记详情 |
| 41 | PUT | /notes/:id | 更新笔记 |
| 42 | DELETE | /notes/:id | 删除笔记 |
| 43 | GET | /notes/:id/versions | 版本历史 |
| 44 | POST | /notes/:id/versions/:vid/restore | 恢复版本 |
| 45 | GET | /notes/:id/export/:fmt | 导出笔记 |
| 46 | GET | /task-columns | 看板列列表 |
| 47 | POST | /task-columns | 创建看板列 |
| 48 | PUT | /task-columns/:id | 更新看板列 |
| 49 | DELETE | /task-columns/:id | 删除看板列 |
| 50 | GET | /tasks | 任务列表 |
| 51 | POST | /tasks | 创建任务 |
| 52 | GET | /tasks/:id | 任务详情 |
| 53 | PUT | /tasks/:id | 更新任务 |
| 54 | DELETE | /tasks/:id | 删除任务 |
| 55 | PUT | /tasks/:id/move | 移动任务 |
| 56 | PUT | /tasks/reorder | 重排任务 |
| 57 | GET | /tasks/today | 今日待办 |
| 58 | GET | /tasks/stats | 任务统计 |
| 59 | GET | /settings/export | 导出数据 |
| 60 | GET | /docs | API 文档 JSON |
| 61 | GET | /docs/ui | Swagger UI |

**共 61 个 API 端点**

---

> **CloudNest** — 个人云端工作台
> 
> 文档版本：1.0.0 | 更新日期：2026-06-01

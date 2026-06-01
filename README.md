# 🐍 CloudNest — 个人云端工作台

一个基于 Flask + Vue3 的现代化个人云端管理平台，支持文件管理、笔记系统、任务看板等核心功能。

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端 | Flask 3.x + SQLAlchemy 2.x + JWT |
| 前端 | Vue 3 + Vite + Naive UI + Pinia |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 部署 | Docker + Nginx + Gunicorn |

## 功能模块

- **用户系统** — 注册/登录/JWT双令牌/头像/密码管理/设备管理/账号注销
- **文件管理** — 上传/下载/文件夹/回收站/分享链接（密码+过期时间）
- **笔记系统** — Markdown编辑器/笔记本/标签/全文搜索/版本历史/导出
- **任务看板** — 看板列/任务卡片/拖拽排序/列表视图/日历视图/优先级
- **仪表盘** — 统计概览/今日待办/快速入口
- **设置中心** — 个人资料/账号安全/设备管理/主题切换

## 快速开始

### 本地开发

```bash
# 1. 后端
cd backend
python -m venv .venv
# Windows
.venv\Scripts\pip install -r requirements.txt
# macOS/Linux
# .venv/bin/pip install -r requirements.txt

cp .env.example .env
# 编辑 .env 修改 SECRET_KEY 和 JWT_SECRET_KEY

.venv\Scripts\python -m flask run --port=5000

# 2. 前端（新终端）
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### Docker 部署

```bash
# 1. 复制并修改配置
cp backend/.env.example backend/.env
# 编辑 .env，修改 SECRET_KEY 和 JWT_SECRET_KEY

# 2. 启动
docker compose up -d --build

# 3. 访问
# http://localhost
```

## 运行测试

```bash
cd backend
.venv\Scripts\pip install pytest
.venv\Scripts\python -m pytest tests/ -v
```

## 项目结构

```
a_web/
├── backend/
│   ├── app.py                 # Flask 应用工厂
│   ├── config.py              # 配置类
│   ├── extensions.py          # 扩展初始化
│   ├── models/                # 数据模型（user/file/note/task）
│   ├── api/v1/                # RESTful API（auth/users/files/notes/tasks）
│   ├── services/              # 业务逻辑层
│   ├── middleware/             # 中间件（JWT/错误处理）
│   ├── utils/                 # 工具函数
│   ├── tests/                 # 单元测试（31个）
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/               # Axios 封装
│   │   ├── router/            # 路由配置
│   │   └── composables/       # 组合式函数
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## API 文档

所有 API 以 `/api/v1` 为前缀，使用 JWT Bearer Token 认证。

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /auth/register | 注册 |
| POST | /auth/login | 登录 |
| POST | /auth/refresh | 刷新令牌 |
| GET | /auth/me | 获取当前用户 |

### 文件
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /files | 文件列表 |
| POST | /files | 上传文件 |
| POST | /files/folder | 新建文件夹 |
| DELETE | /files/:id | 移入回收站 |
| GET | /files/:id/download | 下载 |
| POST | /files/:id/share | 创建分享 |
| GET | /share/:code | 访问分享（免登录） |

### 笔记
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /notes | 笔记列表（支持搜索） |
| POST | /notes | 创建笔记 |
| PUT | /notes/:id | 更新笔记 |
| GET | /notes/:id/versions | 版本历史 |
| GET | /notes/:id/export/:fmt | 导出（markdown/html） |

### 任务
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /tasks | 任务列表 |
| POST | /tasks | 创建任务 |
| PUT | /tasks/:id/move | 移动任务 |
| GET | /tasks/stats | 任务统计 |
| GET | /task-columns | 看板列 |

## License

MIT

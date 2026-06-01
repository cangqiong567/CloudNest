# 🐍 Python Web 全栈项目 — 详细规划文档

## 项目名称
**CloudNest — 个人云端工作台**

## 一、项目概述
一个基于 Flask + Vue3 的现代化个人云端管理平台。支持多用户注册/登录、跨设备访问、文件笔记管理、任务看板等核心功能，UI采用现代极简风格。

## 二、技术选型

### 后端
| 层次 | 技术 | 理由 |
|------|------|------|
| Web框架 | Flask 3.x | 轻量灵活，适合中小项目 |
| ORM | SQLAlchemy 2.x | Python最成熟的ORM |
| 数据库 | SQLite(开发) / PostgreSQL(生产) | 开发零配置，生产可无缝切换 |
| 认证 | Flask-JWT-Extended + bcrypt | JWT令牌认证 + 密码哈希 |
| 跨域 | Flask-CORS | 前后端分离必需品 |
| 文件处理 | Pillow + python-magic | 图片处理 + 文件类型检测 |
| 任务队列 | Celery + Redis | 异步任务（邮件、备份等） |
| API文档 | Flasgger (Swagger) | 自动生成API文档 |

### 前端
| 层次 | 技术 | 理由 |
|------|------|------|
| 框架 | Vue 3 (Composition API) | 生态好，上手快 |
| 构建 | Vite 5 | 快，HMR体验好 |
| UI组件 | Tailwind CSS + shadcn-vue | 现代设计，组件可定制 |
| 状态管理 | Pinia | Vue3官方推荐 |
| 路由 | Vue Router 4 | 多级页面核心 |
| HTTP | Axios + 拦截器 | 请求封装，令牌自动刷新 |
| 图标 | Lucide Vue | 轻量现代图标库 |
| 动画 | GSAP + CSS transitions | 页面过渡+微交互 |

### 部署
| 项目 | 选择 |
|------|------|
| 服务器 | Nginx + Gunicorn |
| 容器化 | Docker + docker-compose |
| CI/CD | GitHub Actions（可选） |

## 三、功能模块设计

### 模块1：用户系统（User System）
```
├── 注册（邮箱+密码 / 手机号+验证码）
├── 登录（JWT双令牌：access 30min + refresh 7day）
├── 异地登录检测（IP/设备指纹 + 可选告警）
├── 账号安全中心
│   ├── 修改密码
│   ├── 绑定/更换邮箱
│   ├── 两步验证（TOTP）
│   └── 登录历史/设备管理
├── 个人资料（头像、昵称、简介）
└── 账号注销（软删除+7天冷静期）
```

### 模块2：文件管理（File Manager）
```
├── 网盘式文件浏览（列表/网格切换）
├── 上传（拖拽+多文件+进度条）
├── 文件夹管理（新建/重命名/删除/移动）
├── 文件预览（图片/PDF/文本）
├── 分享（生成分享链接+过期时间+密码）
├── 回收站（30天自动清空）
└── 存储空间统计
```

### 模块3：笔记系统（Notes）
```
├── Markdown编辑器（支持实时预览）
├── 富文本编辑器（Tiptap）
├── 笔记本/标签分类
├── 全文搜索
├── 置顶/归档
├── 版本历史（保留最近10版）
└── 导出（PDF/Markdown/HTML）
```

### 模块4：任务看板（Task Board）
```
├── 看板视图（待办/进行中/已完成 可自定义列）
├── 任务卡片（标题/描述/优先级/截止日期/标签）
├── 拖拽排序
├── 列表视图（表格+筛选+排序）
├── 日历视图
└── 任务提醒（浏览器通知）
```

### 模块5：仪表盘（Dashboard）
```
├── 概览卡片（文件数/笔记数/任务数/存储用量）
├── 最近活动时间线
├── 快速操作入口
├── 今日待办
└── 存储趋势小图表
```

### 模块6：设置中心（Settings）
```
├── 主题切换（浅色/深色/跟随系统）
├── 语言切换（中/英）
├── 界面偏好（默认首页/列表密度）
├── 通知设置
└── 数据导出（一键导出所有数据）
```

## 四、数据库设计（12张核心表）

```sql
-- 1. 用户表
users
  id            INTEGER PK
  email         VARCHAR(255) UNIQUE
  phone         VARCHAR(20) UNIQUE
  username      VARCHAR(50) UNIQUE
  password_hash VARCHAR(255)
  avatar_url    VARCHAR(500)
  is_active     BOOLEAN DEFAULT TRUE
  is_deleted    BOOLEAN DEFAULT FALSE
  deleted_at    DATETIME
  created_at    DATETIME
  updated_at    DATETIME

-- 2. 登录记录表（异地检测用）
login_records
  id            INTEGER PK
  user_id       INTEGER FK → users
  ip_address    VARCHAR(45)
  device_info   TEXT          -- User-Agent JSON
  location      VARCHAR(100)  -- IP归属地
  is_new_device BOOLEAN
  login_at      DATETIME

-- 3. 信任设备表
trusted_devices
  id            INTEGER PK
  user_id       INTEGER FK → users
  device_id     VARCHAR(64) UNIQUE  -- 设备指纹
  device_name   VARCHAR(100)
  last_used_at  DATETIME
  created_at    DATETIME

-- 4. 刷新令牌表
refresh_tokens
  id            INTEGER PK
  user_id       INTEGER FK → users
  token         VARCHAR(500) UNIQUE
  expires_at    DATETIME
  revoked       BOOLEAN DEFAULT FALSE
  created_at    DATETIME

-- 5. 文件/文件夹表
files
  id            INTEGER PK
  user_id       INTEGER FK → users
  parent_id     INTEGER FK → files (自引用，NULL=根目录)
  name          VARCHAR(255)
  is_folder     BOOLEAN DEFAULT FALSE
  file_size     BIGINT
  mime_type     VARCHAR(100)
  storage_path  VARCHAR(500)   -- 实际存储路径
  is_deleted    BOOLEAN DEFAULT FALSE
  deleted_at    DATETIME
  created_at    DATETIME
  updated_at    DATETIME

-- 6. 文件分享表
file_shares
  id            INTEGER PK
  file_id       INTEGER FK → files
  share_code    VARCHAR(32) UNIQUE  -- 分享码/短链
  password      VARCHAR(100)
  expires_at    DATETIME
  view_count    INTEGER DEFAULT 0
  created_at    DATETIME

-- 7. 笔记表
notes
  id            INTEGER PK
  user_id       INTEGER FK → users
  notebook_id   INTEGER FK → notebooks
  title         VARCHAR(500)
  content       TEXT           -- Markdown/HTML
  content_type  VARCHAR(20)    -- 'markdown'/'richtext'
  is_pinned     BOOLEAN DEFAULT FALSE
  is_archived   BOOLEAN DEFAULT FALSE
  created_at    DATETIME
  updated_at    DATETIME

-- 8. 笔记本表
notebooks
  id            INTEGER PK
  user_id       INTEGER FK → users
  name          VARCHAR(100)
  color         VARCHAR(7)     -- 十六进制颜色
  sort_order    INTEGER
  created_at    DATETIME

-- 9. 笔记版本历史表
note_versions
  id            INTEGER PK
  note_id       INTEGER FK → notes
  content       TEXT
  version_num   INTEGER
  created_at    DATETIME

-- 10. 标签表
tags
  id            INTEGER PK
  user_id       INTEGER FK → users
  name          VARCHAR(50)
  color         VARCHAR(7)

-- 11. 任务看板表
tasks
  id            INTEGER PK
  user_id       INTEGER FK → users
  column_id     INTEGER FK → task_columns
  title         VARCHAR(500)
  description   TEXT
  priority      INTEGER DEFAULT 0    -- 0低/1中/2高/3紧急
  due_date      DATE
  position      INTEGER              -- 排序位置
  created_at    DATETIME
  updated_at    DATETIME

-- 12. 看板列表
task_columns
  id            INTEGER PK
  user_id       INTEGER FK → users
  name          VARCHAR(100)
  position      INTEGER
  color         VARCHAR(7)

-- 关联表
note_tags (note_id, tag_id)    -- 多对多
task_tags (task_id, tag_id)    -- 多对多
```

## 五、API设计（RESTful）

### 认证
```
POST   /api/v1/auth/register          # 注册
POST   /api/v1/auth/login             # 登录 → 返回 access_token + refresh_token
POST   /api/v1/auth/refresh           # 刷新令牌
POST   /api/v1/auth/logout            # 登出（撤销refresh token）
GET    /api/v1/auth/me                # 获取当前用户信息
PUT    /api/v1/auth/password          # 修改密码
```

### 用户
```
GET    /api/v1/users/profile          # 获取个人资料
PUT    /api/v1/users/profile          # 更新个人资料
POST   /api/v1/users/avatar           # 上传头像
GET    /api/v1/users/login-history    # 登录历史
GET    /api/v1/users/devices          # 信任设备列表
DELETE /api/v1/users/devices/:id      # 移除信任设备
POST   /api/v1/users/2fa/enable       # 启用两步验证
POST   /api/v1/users/2fa/verify       # 验证两步验证码
DELETE /api/v1/users/account          # 注销账号
```

### 文件
```
GET    /api/v1/files                   # 文件列表(支持?parent_id=&type=&sort=)
POST   /api/v1/files                   # 上传文件(multipart)
POST   /api/v1/files/folder            # 新建文件夹
GET    /api/v1/files/:id               # 文件详情
PUT    /api/v1/files/:id               # 重命名/移动
DELETE /api/v1/files/:id               # 移入回收站
POST   /api/v1/files/:id/restore       # 从回收站恢复
DELETE /api/v1/files/:id/permanent     # 永久删除
GET    /api/v1/files/:id/download      # 下载
POST   /api/v1/files/:id/share         # 生成分享链接
GET    /api/v1/share/:code             # 通过分享码访问
GET    /api/v1/trash                   # 回收站列表
```

### 笔记
```
GET    /api/v1/notes                   # 笔记列表(支持?notebook=&tag=&search=&archived=)
POST   /api/v1/notes                   # 创建笔记
GET    /api/v1/notes/:id               # 笔记详情
PUT    /api/v1/notes/:id               # 更新笔记
DELETE /api/v1/notes/:id               # 删除笔记
GET    /api/v1/notes/:id/versions      # 版本历史
POST   /api/v1/notes/:id/restore/:v    # 恢复到指定版本
GET    /api/v1/notebooks               # 笔记本列表
POST   /api/v1/notebooks               # 创建笔记本
PUT    /api/v1/notebooks/:id           # 更新笔记本
DELETE /api/v1/notebooks/:id           # 删除笔记本
GET    /api/v1/tags                    # 标签列表
POST   /api/v1/tags                    # 创建标签
```

### 任务
```
GET    /api/v1/tasks                   # 任务列表(支持?column=&priority=&due=)
POST   /api/v1/tasks                   # 创建任务
GET    /api/v1/tasks/:id               # 任务详情
PUT    /api/v1/tasks/:id               # 更新任务
DELETE /api/v1/tasks/:id               # 删除任务
PUT    /api/v1/tasks/:id/move          # 移动任务到其他列
PUT    /api/v1/tasks/:id/reorder       # 调整排序
GET    /api/v1/task-columns            # 看板列
POST   /api/v1/task-columns            # 创建列
PUT    /api/v1/task-columns/:id        # 更新列
DELETE /api/v1/task-columns/:id        # 删除列
```

### 仪表盘
```
GET    /api/v1/dashboard/stats         # 统计概览
GET    /api/v1/dashboard/activities    # 最近活动
GET    /api/v1/dashboard/today-tasks   # 今日待办
```

### 设置
```
GET    /api/v1/settings                # 获取设置
PUT    /api/v1/settings                # 更新设置
POST   /api/v1/settings/export         # 导出数据
```

## 六、前端页面架构（多级路由）

```
/                           → 着陆页(Landing) / 自动跳转仪表盘
/login                      → 登录页
/register                   → 注册页
/forgot-password            → 忘记密码

/dashboard                  → 仪表盘（主页）
/dashboard/files            → 文件管理
/dashboard/files/:folderId  → 文件夹内浏览
/dashboard/files/trash      → 回收站
/dashboard/share/:code      → 分享文件查看（免登录）

/dashboard/notes            → 笔记列表
/dashboard/notes/:id        → 笔记详情/编辑
/dashboard/notes/new        → 新建笔记

/dashboard/tasks            → 任务看板
/dashboard/tasks/board      → 看板视图
/dashboard/tasks/list       → 列表视图
/dashboard/tasks/calendar   → 日历视图

/dashboard/settings         → 设置中心
/dashboard/settings/profile → 个人资料
/dashboard/settings/account → 账号安全
/dashboard/settings/devices → 设备管理
/dashboard/settings/appearance → 界面偏好
```

## 七、项目目录结构

```
cloudnest/
├── backend/
│   ├── app.py                    # Flask应用工厂入口
│   ├── config.py                 # 配置类(开发/测试/生产)
│   ├── extensions.py             # 扩展初始化(SQLAlchemy/JWT/CORS等)
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── file.py
│   │   ├── note.py
│   │   └── task.py
│   ├── api/                      # API蓝图
│   │   ├── __init__.py           # 蓝图注册
│   │   ├── v1/                   # v1版本
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── files.py
│   │   │   ├── notes.py
│   │   │   ├── tasks.py
│   │   │   ├── dashboard.py
│   │   │   └── settings.py
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── file_service.py
│   │   ├── note_service.py
│   │   └── task_service.py
│   ├── middleware/                # 中间件
│   │   ├── __init__.py
│   │   ├── auth.py               # JWT验证
│   │   ├── device_check.py       # 异地登录检测
│   │   └── error_handler.py      # 全局异常处理
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── validators.py          # 数据校验
│   │   ├── helpers.py             # 通用辅助
│   │   ├── pagination.py          # 分页
│   │   └── storage.py             # 文件存储
│   ├── tasks/                     # Celery异步任务
│   │   ├── __init__.py
│   │   ├── email_tasks.py
│   │   └── backup_tasks.py
│   ├── tests/                     # 测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_files.py
│   │   ├── test_notes.py
│   │   └── test_tasks.py
│   ├── migrations/                # 数据库迁移(Alembic)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── main.js                # Vue入口
│   │   ├── App.vue                # 根组件
│   │   ├── router/
│   │   │   └── index.js           # 路由配置（多级）
│   │   ├── stores/                # Pinia状态管理
│   │   │   ├── auth.js
│   │   │   ├── files.js
│   │   │   ├── notes.js
│   │   │   ├── tasks.js
│   │   │   └── settings.js
│   │   ├── api/                   # Axios封装
│   │   │   ├── index.js           # 实例+拦截器
│   │   │   ├── auth.js
│   │   │   ├── files.js
│   │   │   ├── notes.js
│   │   │   └── tasks.js
│   │   ├── views/                 # 页面组件
│   │   │   ├── Landing.vue
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Dashboard.vue      # 布局容器（侧栏+顶栏+内容区）
│   │   │   ├── dashboard/
│   │   │   │   ├── Home.vue       # 仪表盘首页
│   │   │   │   ├── files/         # 文件模块
│   │   │   │   │   ├── FileList.vue
│   │   │   │   │   ├── FileGrid.vue
│   │   │   │   │   └── Trash.vue
│   │   │   │   ├── notes/         # 笔记模块
│   │   │   │   │   ├── NoteList.vue
│   │   │   │   │   ├── NoteEditor.vue
│   │   │   │   │   └── NoteNew.vue
│   │   │   │   ├── tasks/         # 任务模块
│   │   │   │   │   ├── BoardView.vue
│   │   │   │   │   ├── ListView.vue
│   │   │   │   │   └── CalendarView.vue
│   │   │   │   └── settings/     # 设置模块
│   │   │   │       ├── Profile.vue
│   │   │   │       ├── Account.vue
│   │   │   │       ├── Devices.vue
│   │   │   │       └── Appearance.vue
│   │   ├── components/            # 通用组件
│   │   │   ├── ui/                # 基础UI组件
│   │   │   │   ├── Button.vue
│   │   │   │   ├── Input.vue
│   │   │   │   ├── Modal.vue
│   │   │   │   ├── Dropdown.vue
│   │   │   │   ├── Tabs.vue
│   │   │   │   ├── Avatar.vue
│   │   │   │   ├── Badge.vue
│   │   │   │   ├── Card.vue
│   │   │   │   └── Toast.vue
│   │   │   ├── layout/            # 布局组件
│   │   │   │   ├── Sidebar.vue
│   │   │   │   ├── Topbar.vue
│   │   │   │   └── PageHeader.vue
│   │   │   ├── files/
│   │   │   │   ├── FileIcon.vue
│   │   │   │   ├── FilePreview.vue
│   │   │   │   └── UploadZone.vue
│   │   │   ├── notes/
│   │   │   │   ├── MarkdownEditor.vue
│   │   │   │   └── NoteCard.vue
│   │   │   └── tasks/
│   │   │       ├── TaskCard.vue
│   │   │       ├── TaskColumn.vue
│   │   │       └── TaskModal.vue
│   │   ├── composables/           # 组合式函数
│   │   │   ├── useAuth.js
│   │   │   ├── useTheme.js
│   │   │   ├── useToast.js
│   │   │   └── useDragDrop.js
│   │   ├── assets/
│   │   │   ├── styles/
│   │   │   │   ├── main.css        # Tailwind入口
│   │   │   │   └── transitions.css # 页面过渡动画
│   │   │   └── images/
│   │   └── utils/
│   │       ├── format.js           # 日期/文件大小格式化
│   │       └── validators.js       # 前端表单校验
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml              # 一键部署
├── .gitignore
└── README.md
```

## 八、开发分阶段计划

### 🌱 Phase 1：基础骨架 (第1-3天)
```
□ 初始化Flask项目 + 配置 + 扩展
□ SQLAlchemy模型(users表)
□ Flask-JWT-Extended认证系统（注册/登录/刷新/登出）
□ JWT中间件 + 全局异常处理
□ 初始化Vue3 + Vite + Tailwind + shadcn-vue
□ Axios封装 + 认证拦截器
□ Router配置（含路由守卫）
□ Login/Register页面
□ Dashboard布局（Sidebar + Topbar + Content）
□ 主题切换（浅色/深色）
```

### 🌿 Phase 2：用户系统完善 (第4-5天)
```
□ 用户资料CRUD API + 页面
□ 头像上传（Pillow裁剪+压缩）
□ 修改密码
□ 登录记录(IP+设备指纹+归属地)
□ 异地登录检测（陌生IP/UA标记）
□ 信任设备管理
□ 账号注销流程
□ 两步验证（TOTP）
```

### 🌳 Phase 3：文件管理 (第6-8天)
```
□ 文件/文件夹模型
□ 文件上传API（分片+进度）
□ 文件夹CRUD
□ 文件列表（递归子目录）
□ 前端：文件浏览页（列表/网格双视图）
□ 前端：拖拽上传+进度条
□ 文件下载
□ 文件预览（图片/PDF内嵌）
□ 移动/重命名
□ 回收站 + 恢复 + 30天自动清理(Celery)
□ 文件分享（生成链接+密码+过期时间）
□ 分享页（免登录访问）
```

### 🌲 Phase 4：笔记系统 (第9-11天)
```
□ 笔记/笔记本/标签模型
□ 笔记CRUD API + 搜索API
□ 笔记本管理API
□ 标签管理API
□ Markdown编辑器前端组件
□ 笔记列表页 + 编辑页
□ 笔记本侧栏导航
□ 标签筛选
□ 全文搜索
□ 置顶/归档
□ 版本历史
□ 导出功能（PDF/Markdown）
```

### 🏗️ Phase 5：任务看板 (第12-13天)
```
□ 看板列/任务模型
□ 任务CRUD API
□ 列管理API
□ 拖拽排序（@vueuse/core useSortable）
□ 看板视图组件
□ 列表视图组件
□ 日历视图组件
□ 任务卡片（优先级颜色+截止日期高亮）
□ 浏览器通知（Notification API）
```

### 🎨 Phase 6：仪表盘 + UI打磨 (第14-15天)
```
□ 仪表盘统计API
□ 统计卡片组件（数字动画）
□ 最近活动时间线
□ 今日待办组件
□ 快速操作快捷入口
□ 所有页面微动画（GSAP/transitions）
□ 加载骨架屏
□ 空状态插图
□ 移动端响应式适配
□ 无障碍(A11y)检查
```

### 🚀 Phase 7：部署 + 收尾 (第16-17天)
```
□ Dockerfile（前后端各一）
□ docker-compose.yml
□ Nginx配置
□ .env管理
□ API文档(Swagger)
□ 数据导出功能
□ 单元测试(API核心接口)
□ README.md（安装/运行/部署说明）
```

## 九、关键设计决策

### 9.1 异地登录检测方案
```
每次登录时：
1. 记录 IP + User-Agent → 生成设备指纹(MD5)
2. 查询 login_records 表，检查：
   - IP归属地是否在常用城市列表内
   - 设备指纹是否在 trusted_devices 表中
3. 若两者均为"陌生" → 标记为"异地登录"
4. 发送邮件/站内通知告警（可选）
5. 用户可在"设备管理"页面下线可疑设备
```

### 9.2 JWT双令牌刷新策略
```
Access Token:  30分钟有效期，访问API用
Refresh Token: 7天有效期，存在数据库+httpOnly cookie
  
刷新流程:
  前端拦截器检测401 → 自动调用 /auth/refresh
  → 后端验证refresh token未撤销 → 签发新access token
  → 若refresh也过期 → 强制跳转登录页
```

### 9.3 文件存储策略
```
开发环境: backend/uploads/{user_id}/...
生产环境: 可选 MinIO / OSS / 本地磁盘
  
文件去重: 计算SHA256哈希，相同文件只存一份（引用计数）
上传安全: MIME类型白名单 + 扩展名校验 + 文件头魔数检测
```

### 9.4 前端设计系统
```
颜色:
  主色: #6366F1 (Indigo-500)
  成功: #10B981 (Emerald-500)
  警告: #F59E0B (Amber-500)
  错误: #EF4444 (Red-500)
  
字体: Inter (正文) / JetBrains Mono (代码)
圆角: 8px (卡片) / 6px (按钮) / full (头像)
阴影: 极简 — 只用0.5-2px的微妙阴影
间距: 基于4px的8px网格系统
```

## 十、核心代码骨架（给Claude Code的起点）

### 10.1 Flask应用工厂 (backend/app.py)
```python
from flask import Flask
from config import config_map
from extensions import db, jwt, cors, migrate

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)

    # 注册蓝图
    from api.v1 import api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    # 全局错误处理
    from middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    return app
```

### 10.2 Vue路由配置骨架 (frontend/src/router/index.js)
```javascript
const routes = [
  { path: '/', name: 'landing', component: () => import('@/views/Landing.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue') },
  { path: '/register', name: 'register', component: () => import('@/views/Register.vue') },
  {
    path: '/dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'home', component: () => import('@/views/dashboard/Home.vue') },
      { path: 'files', name: 'files', component: () => import('@/views/dashboard/files/FileList.vue') },
      { path: 'files/:folderId', name: 'files-folder', component: () => import('@/views/dashboard/files/FileList.vue') },
      { path: 'files/trash', name: 'trash', component: () => import('@/views/dashboard/files/Trash.vue') },
      { path: 'notes', name: 'notes', component: () => import('@/views/dashboard/notes/NoteList.vue') },
      { path: 'notes/new', name: 'note-new', component: () => import('@/views/dashboard/notes/NoteEditor.vue') },
      { path: 'notes/:id', name: 'note-edit', component: () => import('@/views/dashboard/notes/NoteEditor.vue') },
      { path: 'tasks', name: 'tasks', redirect: '/dashboard/tasks/board' },
      { path: 'tasks/board', name: 'tasks-board', component: () => import('@/views/dashboard/tasks/BoardView.vue') },
      { path: 'tasks/list', name: 'tasks-list', component: () => import('@/views/dashboard/tasks/ListView.vue') },
      { path: 'tasks/calendar', name: 'tasks-calendar', component: () => import('@/views/dashboard/tasks/CalendarView.vue') },
      { path: 'settings', name: 'settings', redirect: '/dashboard/settings/profile' },
      { path: 'settings/profile', name: 'settings-profile', component: () => import('@/views/dashboard/settings/Profile.vue') },
      { path: 'settings/account', name: 'settings-account', component: () => import('@/views/dashboard/settings/Account.vue') },
      { path: 'settings/devices', name: 'settings-devices', component: () => import('@/views/dashboard/settings/Devices.vue') },
      { path: 'settings/appearance', name: 'settings-appearance', component: () => import('@/views/dashboard/settings/Appearance.vue') },
    ]
  }
]
```

## 十一、给Claude Code的执行建议

1. **严格按Phase顺序开发**，每完成一个Phase先验证再继续
2. **先搭数据模型，再写API，最后写前端页面** — 这是铁律
3. **每个功能写完立即测试**，用 `curl` 或 `Postman` 验证API
4. **前后端对接时**，用 `npm run dev`(前端) + `flask run`(后端) 同时跑
5. **不要一口气实现所有功能**，先做出MVP（Phase 1完成就能注册登录看到仪表盘）
6. **Git提交策略**：每个子功能一个commit，方便回滚

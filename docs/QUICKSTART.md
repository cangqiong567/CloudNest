# CloudNest 快速上手指南

> 5 分钟从零开始运行 CloudNest

---

## 你需要什么

- Python 3.10+
- Node.js 18+
- 一个终端

---

## 第一步：启动后端

```bash
cd backend

# 创建虚拟环境（仅首次）
python -m venv .venv

# 激活
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装依赖（仅首次）
pip install -r requirements.txt

# 配置环境变量（仅首次）
cp .env.example .env

# 启动
flask run --port=5000
```

看到 `Running on http://127.0.0.1:5000` 就成功了。

---

## 第二步：启动前端

新开一个终端：

```bash
cd frontend

# 安装依赖（仅首次）
npm install

# 启动
npm run dev
```

看到 `Local: http://localhost:5173` 就成功了。

---

## 第三步：使用

1. 打开浏览器访问 **http://localhost:5173**
2. 点击 **注册** 创建账号
3. 登录后进入仪表盘

---

## 功能速览

| 页面 | 做什么 |
|------|--------|
| 仪表盘 | 查看文件/笔记/任务统计、快速入口 |
| 文件管理 | 上传文件、创建文件夹、下载、分享 |
| 笔记系统 | 写 Markdown 笔记、搜索、版本历史 |
| 任务看板 | 拖拽任务卡片、切换看板/列表/日历视图 |
| 设置 | 改密码、开两步验证、切换主题/语言、导出数据 |

---

## Docker 一键部署

如果你有 Docker：

```bash
# 配置
cp backend/.env.example backend/.env

# 启动
docker compose up -d --build

# 访问 http://localhost
```

---

## 常用命令

| 命令 | 作用 |
|------|------|
| `flask run --port=5000` | 启动后端 |
| `npm run dev` | 启动前端 |
| `python -m pytest tests/ -v` | 运行测试 |
| `docker compose up -d --build` | Docker 构建启动 |
| `docker compose logs -f` | 查看日志 |
| `docker compose down` | 停止服务 |

---

## API 文档

后端运行时访问：

- **JSON 格式**: http://localhost:5000/api/v1/docs
- **Swagger UI**: http://localhost:5000/api/v1/docs/ui

---

## 遇到问题？

| 问题 | 解决 |
|------|------|
| `ModuleNotFoundError` | 确认虚拟环境已激活，运行 `pip install -r requirements.txt` |
| 前端连不上后端 | 确认后端在 5000 端口运行 |
| 端口被占用 | `flask run --port=5001` 或 `npm run dev -- --port 5174` |
| Docker 启动失败 | `docker compose logs` 查看错误 |

详细文档见 [USAGE.md](USAGE.md)

---

> **CloudNest** — 个人云端工作台

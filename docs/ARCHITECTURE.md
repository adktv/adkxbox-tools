# adkxbox-tools 架构设计

> 面向开发者 / IT 从业者的在线工具箱，基于 IT-Tools 前端（fork）+ FastAPI 后端深度定制

## 1. 总体架构

```
┌─────────────────────────────────────────────────────┐
│                  Browser (用户)                      │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────┐
│  Caddy (反向代理 + 自动 HTTPS + 限流)                │
│  域名: tools.adkxbox.dpdns.org                        │
│  端口: 443                                          │
└────────┬──────────────────────────────┬─────────────┘
         │ /                          │ /api/
         ▼                            ▼
┌──────────────────┐         ┌────────────────────────┐
│  Frontend        │         │  Backend (FastAPI)       │
│  Vue 3 + Vite    │         │  Python 3.12+           │
│  Fork IT-Tools   │         │  Port 8000 (内部)        │
│  Port 3000       │         │  - JWT 鉴权             │
│  (Nginx/Caddy    │         │  - slowapi 限流         │
│   static serve)  │         │  - SQLModel ORM         │
└──────────────────┘         │  - SQLAlchemy Async     │
                             └────┬──────────┬────────┘
                                  │          │
                                  ▼          ▼
                          ┌──────────┐  ┌─────────┐
                          │  SQLite  │  │  Redis  │
                          │ (dev)    │  │ 限流+   │
                          │ Postgres │  │ session │
                          │ (prod)   │  │ 缓存    │
                          └──────────┘  └─────────┘
```

## 2. 技术栈

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4 | 主框架 |
| Vite | ^5.0 | 构建工具 |
| TypeScript | ^5.3 | 类型 |
| Pinia | ^2.1 | 状态管理 |
| vue-router | ^4.3 | 路由 |
| Naive UI / shadcn-vue | latest | UI 组件 |
| vue-i18n | ^9 | 国际化（中/英）|
| **fork 自** | CorentinTh/it-tools | UI 起点 |

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | ^0.115 | Web 框架 |
| Pydantic | ^2.9 | 数据验证 |
| SQLModel | ^0.0.22 | ORM（合并 SQLAlchemy + Pydantic）|
| Alembic | ^1.13 | 数据库迁移 |
| uvicorn | ^0.32 | ASGI 服务器 |
| python-jose | ^3.3 | JWT |
| passlib[bcrypt] | ^1.7 | 密码哈希 |
| slowapi | ^0.1.9 | 限流 |
| redis | ^5.2 | 缓存 / 限流存储 |
| httpx | ^0.27 | 异步 HTTP（调外部 API）|
| pytest | ^8.3 | 测试 |

### 基础设施
| 组件 | 用途 |
|------|------|
| Caddy | 反代 + 自动 HTTPS |
| Docker Compose | 一键启动 |
| GitHub Actions | CI/CD |
| CCS VPS (192.227.241.20) | 生产环境 |
| OpenClaw 主机 (161.118.202.158) | 备援 / 公网入口 |

## 3. 目录结构

```
adkxbox-tools/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置（pydantic-settings）
│   │   ├── database.py         # DB session
│   │   ├── deps.py             # 依赖注入
│   │   ├── models/             # SQLModel 模型
│   │   │   ├── user.py
│   │   │   ├── tool.py
│   │   │   └── usage.py
│   │   ├── routers/            # API 路由
│   │   │   ├── auth.py         # /api/auth/*
│   │   │   ├── tools.py        # /api/tools/*
│   │   │   ├── admin.py        # /api/admin/*
│   │   │   └── tools/          # 具体工具
│   │   │       ├── base64.py
│   │   │       ├── json_format.py
│   │   │       ├── regex.py
│   │   │       ├── vps_calculator.py
│   │   │       ├── currency.py
│   │   │       ├── iptv_probe.py
│   │   │       └── ...
│   │   ├── core/               # 核心
│   │   │   ├── security.py     # JWT / 密码
│   │   │   ├── rate_limit.py   # slowapi
│   │   │   └── exceptions.py
│   │   └── utils/
│   ├── tests/                  # pytest
│   ├── alembic/                # DB 迁移
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # Vue 3 前端（fork IT-Tools）
│   ├── src/
│   │   ├── tools/              # 工具组件
│   │   ├── views/
│   │   ├── components/
│   │   ├── api/                # FastAPI 调用
│   │   ├── stores/
│   │   └── router/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env.example
├── docker/                     # 容器配置
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── Caddyfile
│   └── init-db.sql
├── docs/                       # 文档
│   ├── ARCHITECTURE.md         # 本文件
│   ├── API.md                  # API 文档
│   ├── TOOLS.md                # 工具列表
│   └── DEPLOY.md               # 部署指南
├── .github/
│   └── workflows/
│       ├── ci.yml              # 测试
│       └── deploy.yml          # 部署
├── README.md
├── LICENSE
└── .gitignore
```

## 4. 数据模型（核心）

```python
# User
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_admin: bool = False
    is_active: bool = True
    api_key: str | None = Field(default=None, index=True)  # 用于 API 调用
    created_at: datetime
    last_login: datetime | None

# Tool（后台可配置启用/禁用）
class Tool(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g. "base64", "vps-calculator"
    name_zh: str
    name_en: str
    description_zh: str
    description_en: str
    category: str
    enabled: bool = True
    order: int = 0
    is_new: bool = False
    # 工具的具体配置（路由路径、所需权限等）
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))

# Usage（使用统计，可选）
class Usage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None
    tool_id: str
    ip: str
    user_agent: str
    timestamp: datetime
    duration_ms: int
    success: bool
```

## 5. API 设计

### 鉴权
```
POST /api/auth/register    # 注册
POST /api/auth/login       # 登录（返回 JWT）
POST /api/auth/refresh     # 刷新 token
GET  /api/auth/me          # 当前用户信息
```

### 工具（无需鉴权的工具 /api/tools/...）
```
GET  /api/tools                       # 工具列表
GET  /api/tools/{tool_id}             # 工具详情
POST /api/tools/{tool_id}/execute     # 执行工具
GET  /api/tools/{tool_id}/history     # 历史记录（需鉴权）
```

### 工具样例
```
POST /api/tools/base64/encode         # {"text": "hello"}
POST /api/tools/base64/decode         # {"text": "aGVsbG8="}
POST /api/tools/json/format           # {"text": "{...}", "indent": 2}
POST /api/tools/regex/match           # {"pattern": "...", "text": "..."}
POST /api/tools/vps-calculator/calc   # {"price": 20, "cycle": "year", ...}
POST /api/tools/currency/convert      # {"from": "USD", "to": "CNY", "amount": 100}
POST /api/tools/iptv-probe            # {"url": "http://..."}
```

### 后台管理（admin 权限）
```
GET    /api/admin/users
POST   /api/admin/users
PATCH  /api/admin/users/{id}
DELETE /api/admin/users/{id}
GET    /api/admin/tools
PATCH  /api/admin/tools/{id}     # 启用/禁用/排序
GET    /api/admin/usage          # 使用统计
GET    /api/admin/settings
PATCH  /api/admin/settings
```

## 6. 鉴权与限流

### JWT
- **Access Token**: 30 分钟，HS256
- **Refresh Token**: 7 天
- **API Key**（可选）: 长期，用于第三方调用
- 密码 bcrypt 哈希（cost=12）

### 限流（slowapi）
| 端点 | 限制 |
|------|------|
| `/api/auth/*` | 10/分钟/IP |
| `/api/tools/*/execute`（未登录）| 30/分钟/IP |
| `/api/tools/*/execute`（登录）| 300/分钟/User |
| `/api/admin/*` | 60/分钟/User |
| 全局 | 1000/分钟/IP |

## 7. 部署（CCS VPS）

### 一键启动（开发）
```bash
cd adkxbox-tools
docker compose -f docker/docker-compose.dev.yml up
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 生产（CCS）
```bash
ssh root@192.227.241.20
cd /opt/adkxbox-tools
git pull
docker compose -f docker/docker-compose.yml up -d
```

### 域名
- `tools.adkxbox.dpdns.org`（Caddy 自动 HTTPS + Let's Encrypt）

## 8. 工具清单（初始 10 个）

| # | 工具 ID | 中文名 | 类型 | 鉴权 |
|---|---------|--------|------|------|
| 1 | base64 | Base64 编/解码 | 客户端 | ❌ |
| 2 | json-format | JSON 格式化 / 差异 | 客户端 | ❌ |
| 3 | regex-tester | 正则表达式测试 | 客户端 | ❌ |
| 4 | url-codec | URL 编/解码 | 客户端 | ❌ |
| 5 | timestamp | Unix 时间戳转换 | 客户端 | ❌ |
| 6 | color-picker | 颜色选择器 / 转换 | 客户端 | ❌ |
| 7 | uuid-gen | UUID 生成 | 客户端 | ❌ |
| 8 | **vps-calculator** | VPS 剩余价值计算 | 服务端 | ❌ |
| 9 | **iptv-probe** | IPTV 频道延迟测试 | 服务端 | ❌ |
| 10 | **currency-convert** | 货币换算（实时汇率）| 服务端 | ❌ |

> **加粗 = 大哥定制**：和原版 IT-Tools 不同的特色功能，对应 Woodll 里的 VPS 计算器

## 9. 路线图

### 阶段 1（当前）— 骨架 ✅
- 仓库结构、Docker 配置、CI、文档

### 阶段 2 — 鉴权 + 限流
- JWT 实现、slowapi 集成、CORS 配置
- Fork IT-Tools → 改 API 调用为 FastAPI

### 阶段 3 — 10 个核心工具
- 客户端工具直接用 IT-Tools 现有组件
- 服务端工具：VPS 计算器 / IPTV 探针 / 货币换算

### 阶段 4 — 部署 + 文档
- Docker compose
- Caddy HTTPS
- CCS 部署 + 域名
- 文档站点

## 10. 关键决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 前端框架 | Vue 3 / React / Svelte | **Vue 3** | IT-Tools 原版，零迁移成本 |
| 后端框架 | FastAPI / Flask / Django | **FastAPI** | 异步 + 类型 + 自动文档 |
| ORM | SQLAlchemy / SQLModel / Tortoise | **SQLModel** | FastAPI 作者写的，简洁 |
| DB（dev） | SQLite / Postgres | **SQLite** | 零配置，dev 够用 |
| DB（prod） | Postgres / MySQL | **Postgres** | 生态最好 |
| 缓存 / 限流 | Redis / Memcached / 内存 | **Redis** | 限流标准方案 |
| 鉴权 | JWT / Session / OAuth | **JWT** | API 友好，无状态 |
| 部署 | Docker Compose / K8s | **Compose** | 单机足够，简单 |
| 反代 | Caddy / Nginx / Traefik | **Caddy** | 自动 HTTPS，零配置 |
| UI 起点 | 自己写 / Fork IT-Tools | **Fork IT-Tools** | 50K stars，省 90% 工作 |

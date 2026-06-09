# adkxbox-tools

> 面向开发者 / IT 从业者的在线工具箱，基于 [IT-Tools](https://github.com/CorentinTh/it-tools) 前端 + FastAPI 后端深度定制

## 特色

- 🎨 **完整汉化** + 全新浅色/深色 UI
- 🚀 **企业级后端**：FastAPI + JWT + 限流 + 后台管理
- 🐳 **一键部署**：Docker Compose + Caddy
- 🇨🇳 **国内优化**：依赖镜像、CCS 部署文档
- 💎 **特色工具**：VPS 剩余价值计算器 / IPTV 频道探针 / 实时汇率

## 在线体验

- **生产**：`https://tools.adkxbox.dpdns.org`（待部署）
- **开发**：`http://localhost:3000`

## 快速开始

### Docker Compose（一键）

```bash
git clone https://github.com/<your-username>/adkxbox-tools.git
cd adkxbox-tools
docker compose -f docker/docker-compose.yml up -d
```

### 本地开发

```bash
# 后端
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

打开 http://localhost:3000

## 工具列表

| 工具 | 描述 |
|------|------|
| Base64 编/解码 | 文本与 Base64 互转 |
| JSON 格式化 | 美化、压缩、差异比较 |
| 正则测试 | 实时匹配高亮 |
| URL 编/解码 | URL 安全编码 |
| 时间戳转换 | Unix 时间戳 ↔ 人类时间 |
| 颜色选择器 | HEX / RGB / HSL 互转 |
| UUID 生成 | v1 / v4 / v7 |
| **VPS 算价** | 续费金额、溢价、剩余价值（特色）|
| **IPTV 探针** | HLS 流延迟、可用性测试（特色）|
| **货币换算** | 实时汇率（特色）|

## 文档

- [架构设计](docs/ARCHITECTURE.md)
- [API 文档](docs/API.md)（运行后访问 `/docs`）
- [部署指南](docs/DEPLOY.md)
- [工具开发](docs/TOOLS.md)

## 技术栈

**前端**: Vue 3 + Vite + TypeScript + Tailwind + Naive UI（fork IT-Tools）
**后端**: FastAPI + SQLModel + SQLite/Postgres + Redis
**部署**: Docker Compose + Caddy

## 贡献

欢迎 PR！详见 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 许可

MIT

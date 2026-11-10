# gaokao-600

🎯 高考冲刺 600 分:面向高三学生的 AI 网页学习伴侣——智能作文批改、错题间隔重复、个性化学习计划

## Business Context

- **Category:** education product
- **Audience:** learners, teachers, parents, and education operators who need a clearer learning or exam-prep workflow.
- **Repository status:** Public repository. Keep examples, docs, and issues free of credentials, private data, and machine-specific paths.
- **Topics:** ai, edtech, education, fastapi, gaokao, gemini, nextjs, spaced-repetition, typescript

## What This Project Is For

- 🎯 高考冲刺 600 分:面向高三学生的 AI 网页学习伴侣——智能作文批改、错题间隔重复、个性化学习计划.
- Give users a concrete learning workflow instead of a loose collection of content.
- Make practice, feedback, review, or recommendation steps easier to repeat.

## Where It Fits

This repository supports productized learning workflows: diagnostic input, guided practice, review loops, and clearer handoff between learner, teacher, and software.

## Technical Overview

- **Primary language:** TypeScript
- **Detected stack:** TypeScript, Node.js, Python dependencies, Docker, Next.js, React, Tailwind CSS
- **Default branch:** `main`
- **Visibility:** `PUBLIC`
- **License:** MIT License

## Repository Map

- `backend`
- `frontend`
- `.env.example`
- `Dockerfile`
- `LICENSE`
- `README.md`
- `SECURITY.md`

## Quick Start

Use the commands that match the current project state:

```bash
cd frontend
npm install --registry=https://registry.npmjs.org
npm run dev
npm start
npm run build
npm run lint
```

| Command | Purpose |
|---|---|
| `npm install --registry=https://registry.npmjs.org` | Install frontend dependencies (run from `frontend`). |
| `npm run dev` | next dev |
| `npm start` | next start |
| `npm run build` | next build |
| `npm run lint` | eslint . |

| 变量 | 说明 |
|------|------|
| `GEMINI_API_KEY` | Google Gemini API 密钥（[在此获取](https://aistudio.google.com/apikey)） |
| `NEXT_PUBLIC_API_URL` | 前端调用的后端地址（默认 `http://localhost:8000`） |
| `ALLOWED_ORIGINS` | 后端允许的跨域来源，逗号分隔（默认 `http://localhost:3000`，生产填真实前端域名） |
| `GEMINI_MODEL` | 可选，覆盖默认模型（默认 `gemini-2.5-flash`） |
| `DATABASE_URL` | 可选，PostgreSQL/Supabase 连接串；不设则用本地 SQLite |
| `DEFAULT_USER_ID` | 可选，单用户模式下的默认用户 id（默认 `1`） |

## Operating Notes

- Keep real credentials out of the repository. Use local environment files, GitHub repository secrets, or the deployment platform secret manager.
- If a `.env.example` file exists, treat it as documentation only; never commit filled-in `.env` files.
- Before publishing screenshots, demos, or client examples, remove private names, internal paths, account IDs, and API endpoints.
- The `Repository Hygiene` workflow is a lightweight guardrail, not a replacement for product-specific tests.

## Delivery Checklist

- [ ] README describes the user, business outcome, and operating boundary.
- [ ] Setup or preview commands are current and do not rely on private machine state.
- [ ] No real secrets, private user data, or machine-local state are tracked.
- [ ] Screenshots, demos, or sample outputs are safe to share publicly when the repository is public.
- [ ] Product-specific tests or smoke checks are documented before production use.

## Roadmap

- Tighten the fastest path from clone to useful demo.
- Add project-specific screenshots, sample outputs, or a short walkthrough where useful.
- Promote repeated manual steps into scripts, tests, or documented workflows.
- Keep security, privacy, and licensing boundaries explicit as the project evolves.

## Maintainer Notes

### 部署

- **前端 — Vercel**：导入仓库，根目录设为 `frontend`，配置 `NEXT_PUBLIC_API_URL`。
- **后端 — Railway / Render / Docker**：仓库内已含 `Dockerfile`、`railway.json` 与 `Procfile`，可直接部署。

## 🤝 关于与连接

作者 **Tony（盛）** 是一名中文培训师，累计服务 6000+ 学员，长期用 AI 打造中文教学与备考工具。这个项目是其中之一——把一线教学经验沉淀成学生每天都能用上的提分工具。

如果它对你或你的学生有帮助，欢迎 ⭐ **[Star 本仓库](https://github.com/shengdabai/gaokao-600)** 并关注 **[@shengdabai](https://github.com/shengdabai)**，这是对作者持续投入最大的鼓励。

**相关项目**

- [gaokao-study-materials](https://github.com/shengdabai/gaokao-study-materials) — 高考备考资料
- [gaokao-review](https://github.com/shengdabai/gaokao-review) — 高考复习工具
- [gaokao-assistant](https://github.com/shengdabai/gaokao-assistant) — 高考备考助手

## ⚠️ 安全说明 / Security

本项目当前为**单用户模式**，便于个人使用与本地演示：

- **无认证机制**：所有接口都归属同一个默认用户（`DEFAULT_USER_ID`，默认 `1`），没有登录 / token / session。**请勿在未加认证的情况下把它作为多用户服务公开部署**，否则任何访问者都能读写同一份数据。
- **CORS 来源限制**：后端允许的跨域来源由环境变量 `ALLOWED_ORIGINS` 控制（逗号分隔，默认 `http://localhost:3000`）。生产部署时务必设置为你的真实前端域名，不要放开为 `*`。
- **API 密钥**：`GEMINI_API_KEY` 只在后端读取，不会下发到前端；请通过环境变量配置，切勿提交进仓库。

如需多人使用，需自行扩展 `User` 表与认证层（详见 `backend/app/config.py`）。

## License

本项目采用 [MIT License](./LICENSE) 开源。

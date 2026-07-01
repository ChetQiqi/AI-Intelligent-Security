# AI Intelligent Security

AI Intelligent Security 是一个 AI 智慧安防 Demo/MVP，围绕安防事件中心、数据驾驶舱、自然语言查数、RAG 知识库和 Agent 自动分析构建。项目目标是展示一个可落地的安防分析平台原型，而不是单一的人脸识别算法仓库。

仓库地址：<https://github.com/ChetQiqi/AI-Intelligent-Security>

## 项目定位

本项目适合作为 Demo 或 MVP 展示，核心能力包括：

- 安防驾驶舱：展示事件总览、摄像头活跃度、陌生人趋势、最近事件等关键指标。
- 事件中心：管理已知人员识别事件、陌生人事件、摄像头和人员基础数据。
- NL2SQL 查数：用自然语言查询安防事件数据，并返回 SQL、表格结果和解释。
- RAG 知识库：上传安防制度、处置流程、运维手册等文档，支持问答和引用来源。
- Agent 安防分析：自动调用统计工具、知识库和规则引擎，生成结构化安防分析报告。
- React 前端：包含首页、驾驶舱、最近事件、陌生人事件、NL2SQL、知识库和 Agent 分析页面。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 API | FastAPI, SQLAlchemy 2.x, Pydantic |
| 数据库 | PostgreSQL, Alembic |
| 前端 | React 19, TypeScript, Vite, Ant Design, Recharts |
| 智能能力 | NL2SQL, RAG, Agent 工具调用与规则分析 |
| 部署辅助 | Docker Compose |

## 目录结构

```text
AI-Intelligent-Security/
├── app/                    # 安防事件中心、NL2SQL、RAG、Agent 后端
│   ├── api/                # FastAPI 路由
│   ├── core/               # 配置
│   ├── db/                 # 数据库连接与初始化
│   ├── models/             # SQLAlchemy ORM
│   ├── schemas/            # Pydantic Schema
│   ├── scripts/            # 示例数据脚本
│   └── services/           # 业务服务
├── alembic/                # 数据库迁移
├── docs/rag_seed/          # 示例知识库文档
├── frontend/               # React 前端
├── docker-compose.yml      # PostgreSQL 本地数据库
├── requirements.txt        # Python 依赖
├── run.py                  # 本地启动入口
└── .env.example            # 环境变量示例
```

## 快速启动

以下步骤用于启动安防事件中心和 React Demo 页面。

### 1. 克隆仓库

```bash
git clone https://github.com/ChetQiqi/AI-Intelligent-Security.git
cd AI-Intelligent-Security
```

### 2. 准备 Python 环境

推荐 Python 3.10。

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

如果你使用的是本项目开发环境，也可以使用已有 Conda 环境。

### 3. 配置环境变量

```bash
copy .env.example .env
```

macOS / Linux：

```bash
cp .env.example .env
```

默认 `.env.example` 已经匹配 `docker-compose.yml` 中的 PostgreSQL 用户名和密码。

### 4. 启动数据库

```bash
docker compose up -d event-db
```

### 5. 初始化数据库表

```bash
alembic upgrade head
```

### 6. 写入示例数据

```bash
python -m app.scripts.seed_data
```

示例数据会生成摄像头、人员、识别事件和陌生人事件，方便直接查看驾驶舱和 Agent 分析效果。

### 7. 启动后端

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

后端地址：

```text
http://127.0.0.1:8001
```

API 文档：

```text
http://127.0.0.1:8001/docs
```

### 8. 启动前端

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：

```text
http://127.0.0.1:3000
```

## RAG 知识库示例

仓库保留了示例知识库文档：

```text
docs/rag_seed/
```

可以在前端知识库页面上传这些 Markdown 文件并向量化。默认配置中：

```text
RAG_LOCAL_DEMO_MODE=true
```

因此即使没有配置外部 LLM 或 Embedding 服务，也可以进行本地 Demo 级别的知识库问答。正式效果建议接入 OpenAI-compatible Chat Completions 和 Embeddings 服务。

## Demo 可问问题示例

NL2SQL 页面：

```text
最近 7 天每个摄像头的陌生人事件数量
南门摄像头最近一周的识别事件
研发部人员最近一周出现次数排行
```

Agent 分析页面：

```text
分析最近一周整体安防情况
分析最近一周南门安防情况
分析最近一周研发部人员的识别情况
```

Agent 会根据问题意图选择不同分析路径：

- 整体安防：全局事件、陌生人趋势、摄像头热点。
- 摄像头/区域：指定摄像头或区域，例如南门摄像头。
- 部门人员：指定部门人员识别情况，例如研发部。

## 关于模型权重

本仓库不包含人脸识别模型权重文件，例如：

```text
weights/*.pt
weights/*.pth
weights/*.onnx
```

原因：

- 权重文件体积较大，不适合直接放入 Git 仓库。
- 部分权重可能涉及第三方模型许可证和再分发限制。
- HR 或面试官查看 Demo/MVP 时，重点通常是产品能力、工程结构和功能闭环。

如需完整本地识别演示，可以单独提供权重下载方式，下载后放入 `weights/` 目录。

## 当前 Demo 范围

已上传到 GitHub 的主要是 AI 智慧安防平台的运行代码和示例知识库，包括：

- 安防事件中心后端
- React 数据看板和交互页面
- NL2SQL 查数能力
- RAG 知识库能力
- Agent 安防分析能力
- PostgreSQL Docker 配置
- 示例数据脚本

未上传内容：

- 测试代码
- 非 `docs/rag_seed/` 的设计文档和过程文档
- 本地模型权重
- 本地数据库、缓存、生成文件

## 常见问题

### 1. 为什么拉取后不能直接做人脸识别？

仓库没有上传模型权重和本地人脸数据库。安防事件中心和数据分析 Demo 可以按上面的步骤启动；完整人脸识别推理需要单独准备权重和识别数据。

### 2. 为什么 RAG 或 NL2SQL 的回答比较简单？

默认开启本地 Demo 模式，便于无密钥运行。要获得更强效果，需要在 `.env` 中配置：

```text
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
EMBEDDING_BASE_URL=
EMBEDDING_API_KEY=
EMBEDDING_MODEL=
```

## License

本项目用于学习、研究和 Demo 展示。使用第三方模型、权重或数据集时，请遵守其对应许可证。

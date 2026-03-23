# rag-xxmall

基于 FastAPI + LangChain + Chroma 的 RAG（检索增强生成）AI 客服后端系统。

## 项目简介

本项目是一个为前端应用提供接口的 AI 智能客服后端系统，采用 RAG 技术架构，结合向量检索与大语言模型，实现基于知识库的智能问答服务。

**远程仓库**: https://gitee.com/yindong-wen/rag-xxmall.git

## 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| RAG 框架 | LangChain |
| 向量数据库 | ChromaDB |
| 大模型服务 | 阿里云 DashScope（灵积）|
| 嵌入模型 | text-embedding-v4 |
| 对话模型 | qwen3-max |
| 数据验证 | Pydantic + Pydantic-Settings |
| 文本分割 | LangChain-Text-Splitters |

## 项目结构

```
rag-xxmall/
├── app/
│   ├── api/                     # API 接口层
│   │   ├── __init__.py          # 路由聚合
│   │   └── v1/                  # API v1 版本
│   │       ├── chat/            # 聊天接口
│   │       │   ├── router.py    # 流式/非流式对话接口
│   │       │   └── schema.py    # 请求/响应模型
│   │       ├── history/         # 历史记录接口
│   │       │   ├── router.py    # 查询对话历史
│   │       │   └── schema.py
│   │       └── knowledge/       # 知识库接口
│   │           ├── router.py    # 知识库 CRUD
│   │           └── schema.py
│   ├── common/                  # 公共工具模块
│   │   ├── md5.py              # MD5 去重工具
│   │   └── record.py           # 记录管理工具
│   └── core/                    # 核心业务逻辑
│       ├── config.py           # 配置管理（支持多环境）
│       ├── history_store.py    # 对话历史存储（文件存储）
│       ├── knowledge_base.py   # 知识库核心实现
│       ├── rag.py              # RAG 链实现
│       └── vector_store.py     # 向量存储服务
├── data/                        # 数据存储目录（已 gitignore）
│   ├── chat_history/           # 对话历史文件
│   ├── chroma_db/              # Chroma 向量数据库
│   ├── knowledge_base/         # 知识库记录和 MD5 索引
│   └── prompt/                 # 提示词模板
├── main.py                      # 应用入口
├── requirements.txt             # Python 依赖
└── README.md                    # 项目说明
```

## 功能特性

### 1. 智能对话
- 支持流式（SSE）和非流式两种对话模式
- 基于对话历史的上下文理解
- 自动保存会话记录

### 2. 知识库管理
支持三种知识类型：
- **文件**: 文档类知识（如帮助文档、FAQ）
- **商品**: 商品信息知识
- **推荐**: 推荐内容知识

提供完整的 CRUD 操作：
- 上传知识到知识库
- 分页查询知识库内容
- 更新知识内容（自动检测变更）
- 删除知识
- 获取知识分类列表

### 3. 对话历史
- 按 session_id 查询历史记录
- 支持限制返回消息数量
- 自动记录时间戳

### 4. 记录管理系统
本项目采用**记录文件 + 向量数据库**的双层架构管理知识库，而非直接使用文件管理：

**设计优势：**
- **解耦业务与存储**：`records.json` 维护业务元数据，Chroma 负责向量检索，各司其职
- **映射管理**：记录知识条目 ID 与多个向量块（chunks）的映射关系（`chroma_ids`），支持精准更新/删除
- **快速查询**：列表查询直接读取 JSON 文件，无需访问向量数据库，提升管理接口性能
- **元数据扩展**：保存 URL、分类、时间戳等 Chroma 不存储或不便于检索的元数据
- **多类型统一**：统一抽象文件、商品、推荐等不同类型的知识来源

**记录结构：**
```json
{
  "id": "唯一标识",
  "category": "file/goods/recommend",
  "url": ["关联资源URL列表"],
  "md5": "内容MD5值",
  "chroma_ids": ["向量块ID列表"],
  "create_time": "创建时间",
  "update_time": "更新时间"
}
```

### 5. 数据去重
- MD5 内容去重机制
- 防止重复内容入库

### 6. 跨域支持
- 内置 CORS 中间件
- 支持本地开发和生产环境

## 部署步骤

### 1. 环境要求
- Python 3.10+
- pip 包管理器

### 2. 克隆项目
```bash
git clone https://gitee.com/yindong-wen/rag-xxmall.git
cd rag-xxmall
```

### 3. 创建虚拟环境
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 配置环境变量

在 `app/core/settings/` 目录下创建 `.env.dev`（开发环境）或 `.env.prod`（生产环境）：

```env
# 必需配置
DASHSCOPE_API_KEY=your_dashscope_api_key

# 可选配置（有默认值）
APP_HOST=0.0.0.0
APP_PORT=8000
COLLECTION_NAME=rag
CHUNK_SIZE=500
CHUNK_OVERLAP=50
SIMILARITY_SEARCH_K=3
EMBEDDING_MODEL_NAME=text-embedding-v4
CHAT_MODEL_NAME=qwen3-max
```

获取 DashScope API Key：[阿里云灵积模型服务](https://dashscope.aliyun.com/)

### 6. 启动服务

开发模式（热重载）：
```bash
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)"
```

生产模式：
```bash
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000)"
```

或者直接使用 uvicorn 命令：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. 访问接口文档

启动后访问自动生成的 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口概览

| 接口 | 路径 | 说明 |
|------|------|------|
| 流式对话 | POST /v1/chat/stream | SSE 流式响应 |
| 非流式对话 | POST /v1/chat/completion | JSON 完整响应 |
| 查询历史 | POST /v1/history/query | 获取对话历史 |
| 上传知识 | POST /v1/knowledge/upload | 添加知识到知识库 |
| 查询知识 | POST /v1/knowledge/query | 分页查询知识库 |
| 获取分类 | GET /v1/knowledge/category | 获取知识分类 |
| 更新知识 | POST /v1/knowledge/update | 更新知识内容 |
| 删除知识 | POST /v1/knowledge/delete | 删除知识 |

## 更新日志

### 2026-03-23
- 🎉 更新: 更新项目说明文件
- ✨ 新增: 新增项目介绍
  - 新增项目依赖文件
  - 新增项目说明文件

### 2026-03-22
- 🎉 更新: 调整项目结构：将 MD5 和记录相关方法抽离到 common 目录

### 2026-03-19
- 🎉 更新: 统一知识库上传接口的创建和更新时间

### 2026-03-18
- ✨ 新增: 知识库查询
  - 新增知识库查询 schema
  - 新增知识库查询接口新增分页操作
- 🎉 更新: 简化知识库查询接口：分类不为空
- 🎉 更新: 更新知识库功能
  - 更新查询接口路由
  - 更新知识库类型定义

### 2026-03-17
- ✨ 新增: 新增 MD5 去重功能
- 🎉 更新: 更新知识库存储功能

### 2026-03-16
- 🎉 更新: 更新知识库存储功能
- 🎉 更新: 更新知识库相关接口

### 2026-03-15
- ✨ 新增: 新增历史查询接口
- ✨ 新增: 新增对话历史的查询时间、响应时间
- 🎉 更新: 更新对话历史的时间戳追加方式

### 2026-03-14
- ✨ 新增: 新增对话接口，支持流式/非流式对话
- 🎉 更新: 更新历史查询核心功能

### 2026-03-13
- ✨ 新增: 新增跨域中间件

### 2026-03-12
- ✨ 初始化: 初始化项目：FastAPI + LangChain + Chroma 基础架构

## 开源协议

本项目基于 [MIT License](./LICENSE) 开源。

Copyright (C) 2026 - present by Yd Wen

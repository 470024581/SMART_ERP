# SmartERP AI Assistant 后端设置指南## 🚀 快速开始### 1. 环境要求- Python 3.8+ - pip (Python包管理器)### 2. 安装依赖```bashcd serverpip install -r requirements.txt```### 3. 环境配置 (可选)创建 `.env` 文件来自定义配置:```env# OpenAI API 配置 (启用AI功能)OPENAI_API_KEY=your_openai_api_key_hereOPENAI_MODEL=gpt-3.5-turbo# OpenRouter API 配置 (OpenAI的替代)OPENROUTER_API_KEY=your_openrouter_api_key_hereOPENAI_BASE_URL=https://openrouter.ai/api/v1# 数据库配置DATABASE_URL=sqlite:///./data/smart_erp.db# 服务器配置HOST=0.0.0.0PORT=8000DEBUG=TrueLOG_LEVEL=INFO```> **注意**: 即使没有AI API密钥，系统也能正常运行，会使用模拟模式。### 4. 启动服务器```bash# 🎯 推荐方式: 使用内置启动脚本python start.py# 📖 查看启动选项python start.py --help# 🔧 开发模式 (热重载)python start.py --reload# 🚀 生产模式python start.py --prod# 🌐 自定义地址和端口python start.py --host 127.0.0.1 --port 8080```**其他启动方式:**```bash# 直接使用uvicornuvicorn app.main:app --reload --host 0.0.0.0 --port 8000# Python模块方式python -m uvicorn app.main:app --reload```### 5. 验证服务访问以下地址验证服务是否正常:- 🏠 **API 文档**: http://localhost:8000/docs  - 💚 **健康检查**: http://localhost:8000/ping- 📊 **系统信息**: http://localhost:8000/api/v1/analytics/dashboard

## API 接口说明

### 新增的完整 API 接口

#### 智能问答
- `POST /api/v1/query` - 通用智能问答接口

#### 库存管理
- `GET /api/v1/inventory` - 获取库存列表
- `GET /api/v1/inventory/alerts` - 获取库存预警

#### 销售数据
- `GET /api/v1/sales` - 获取销售数据
- `GET /api/v1/sales/products` - 获取产品销量排行

#### 报表生成
- `POST /api/v1/reports/generate` - 生成报表
- `GET /api/v1/reports` - 获取报表列表

#### 数据分析
- `GET /api/v1/analytics/dashboard` - 获取仪表板数据
- `GET /api/v1/analytics/trends` - 获取趋势分析

#### 用户认证 (可选)
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出

### 原有 API (向后兼容)
- `POST /api/v1/sales_query` - 销售查询
- `POST /api/v1/inventory_check` - 库存检查
- `GET /api/v1/reports/sales_daily` - 销售报表

## 数据库说明

系统使用 SQLite 数据库，包含以下表：

1. **products** - 产品信息
2. **inventory** - 库存信息
3. **sales** - 销售记录

数据会在启动时自动从 CSV 文件导入。

## LangChain 集成

系统集成了 LangChain 用于：

1. **智能问答** - 将自然语言转换为 SQL 查询
2. **数据分析** - AI 驱动的销售和库存分析
3. **报表生成** - 自动生成格式化报表
4. **趋势预测** - 基于历史数据的趋势分析

## 前端集成

后端 API 完全兼容前端 React 应用的需求：

- 支持 CORS 跨域请求
- 返回 Chart.js 兼容的图表数据
- 提供结构化的 JSON 响应
- 支持错误处理和状态码

## 故障排除

### 常见问题

1. **端口占用**: 确保 8000 端口未被占用
2. **数据库文件**: 确保 `data/` 目录存在且有写权限
3. **API Key**: 如果使用 AI 功能，确保配置了正确的 API Key
4. **依赖问题**: 确保所有依赖包都已正确安装

### 日志查看

服务器启动后会显示详细的日志信息，包括：
- 数据库连接状态
- API 路由注册情况
- 请求响应日志

## 开发模式

在开发模式下，API 会自动处理错误并返回详细的错误信息。生产环境建议：

1. 设置 `DEBUG=False`
2. 配置正确的 CORS 来源
3. 使用生产级数据库
4. 配置日志记录
5. 设置 API 速率限制

## 扩展功能

系统设计为可扩展的架构，可以轻松添加：

1. **新的数据源** - 支持 MySQL, PostgreSQL 等
2. **更多 AI 模型** - 支持不同的 LLM 提供商
3. **缓存系统** - Redis 等缓存解决方案
4. **消息队列** - 异步任务处理
5. **微服务架构** - 拆分为独立的服务模块 
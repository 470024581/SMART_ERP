# Smart ERP Agent 测试套件

这个目录包含了Smart ERP Agent项目的所有测试工具和脚本。

## 📁 文件结构

```
test/
├── __init__.py              # 测试包初始化
├── README.md               # 本文档
├── check_fix.py            # 修复状态检查工具
├── start_server.py         # 服务器启动脚本
├── direct_test.py          # 直接数据库测试
├── test_fix_page.html      # Web测试界面
├── test_fix.py             # 修复验证测试
├── test_api.py             # 完整API测试套件
├── simple_test.py          # 简单API测试
├── quick_test.py           # 快速功能测试
├── test_db.py              # 数据库功能测试
└── test_simple.py          # 简单功能测试
```

## 🚀 快速开始

### 1. 基础检查
```bash
# 检查修复状态和系统环境
python test/check_fix.py
```

### 2. 启动服务器
```bash
# 启动FastAPI服务器
python test/start_server.py
```

### 3. 运行测试
```bash
# 简单API测试
python test/simple_test.py

# 完整API测试套件
python test/test_api.py

# 快速功能测试
python test/quick_test.py
```

## 📋 测试文件说明

### 核心测试工具

#### `check_fix.py` - 修复状态检查
- **用途**: 检查数据库、文件、配置和模式匹配
- **运行**: `python test/check_fix.py`
- **输出**: 完整的系统状态报告

#### `start_server.py` - 服务器启动
- **用途**: 启动FastAPI服务器用于测试
- **运行**: `python test/start_server.py`
- **端口**: 8001
- **特点**: 自动切换到项目根目录

#### `test_fix_page.html` - Web测试界面
- **用途**: 浏览器中的交互式测试界面
- **功能**: 
  - 服务器状态检查
  - 历史销售额查询测试（修复验证）
  - 多种销售查询测试
  - 图表数据显示
  - 测试结果统计
- **使用**: 在浏览器中打开，确保服务器已启动

### API测试

#### `test_api.py` - 完整API测试套件
- **用途**: 测试所有API端点
- **功能**: 
  - 健康检查
  - 系统信息
  - 销售查询API
  - 快速查询测试
- **运行**: `python test/test_api.py`

#### `simple_test.py` - 简单API测试
- **用途**: 快速测试历史销售额查询
- **运行**: `python test/simple_test.py`
- **输出**: 单一查询的详细结果

### 数据库测试

#### `direct_test.py` - 直接数据库测试
- **用途**: 绕过API直接测试数据库函数
- **功能**: 
  - 数据库连接测试
  - SQL查询验证
  - 模式匹配测试
- **运行**: `python test/direct_test.py`

#### `test_db.py` - 数据库功能测试
- **用途**: 测试所有数据库相关功能
- **功能**: 
  - 数据库状态检查
  - 产品查询
  - 销售查询
  - 数据库初始化
- **运行**: `python test/test_db.py`

### 功能测试

#### `test_fix.py` - 修复验证测试
- **用途**: 验证历史销售额查询修复
- **功能**: 
  - 数据库函数测试
  - 智能体函数测试
- **运行**: `python test/test_fix.py`

#### `quick_test.py` - 快速功能测试
- **用途**: 快速验证核心功能
- **运行**: `python test/quick_test.py`

#### `test_simple.py` - 简单功能测试
- **用途**: 综合测试服务器、数据库、API
- **运行**: `python test/test_simple.py`

## 🎯 测试场景

### 修复验证场景
```bash
# 1. 检查系统状态
python test/check_fix.py

# 2. 启动服务器
python test/start_server.py &

# 3. 验证修复
python test/test_fix.py

# 4. 使用Web界面测试
# 打开 test/test_fix_page.html
```

### 开发测试场景
```bash
# 快速验证
python test/quick_test.py

# 数据库测试
python test/test_db.py

# API测试
python test/test_api.py
```

### 部署验证场景
```bash
# 完整测试流程
python test/check_fix.py
python test/start_server.py &
python test/simple_test.py
python test/test_api.py
```

## 🔧 使用说明

### 环境要求
- Python 3.7+
- 项目依赖已安装 (`pip install -r requirements.txt`)
- 数据库文件存在 (`data/smart_erp.db`)

### 注意事项
1. **路径处理**: 所有测试脚本都会自动处理相对路径
2. **服务器启动**: 测试前确保服务器在8001端口运行
3. **数据库**: 某些测试需要数据库包含销售数据
4. **并发**: 避免同时运行多个API测试脚本

### 故障排除

#### 服务器连接失败
```bash
# 检查服务器状态
python test/check_fix.py

# 启动服务器
python test/start_server.py
```

#### 数据库问题
```bash
# 测试数据库
python test/direct_test.py

# 重置数据库
python test/test_db.py
```

#### 模块导入错误
```bash
# 确保在项目根目录
cd /path/to/smart_erp_agent

# 运行测试
python test/test_name.py
```

## 📊 测试结果解读

### 成功指标
- ✅ 数据库连接正常
- ✅ 销售记录存在
- ✅ API响应包含实际数据
- ✅ 图表数据生成
- ✅ "历史销售额多少？"查询返回详细信息

### 失败指标
- ❌ 数据库文件不存在
- ❌ 查询返回空结果
- ❌ API返回通用错误信息
- ❌ 服务器连接失败

## 🔄 持续集成

这些测试脚本可以集成到CI/CD流程中：

```yaml
# 示例 GitHub Actions
- name: Run Tests
  run: |
    python test/check_fix.py
    python test/start_server.py &
    sleep 5
    python test/test_api.py
    python test/test_fix.py
```

---

**测试套件版本**: v1.0  
**最后更新**: 2025-01-25  
**兼容版本**: Smart ERP Agent v1.0+ 
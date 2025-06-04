# 血糖监测云端系统 RESTful API

基于 Flask 的血糖监测数据云端 RESTful API 系统，提供科研级、工程级的数据管理解决方案。

## 项目概述

本项目实现了一个完整的血糖监测数据云端管理系统，采用 RESTful 架构设计，支持：

- 血糖数据上传与存储
- 数据查询与历史记录管理
- 用户管理与设备管理
- 数据统计与分析
- 完整的认证与授权机制
- 异常处理与日志记录

## 技术栈

- **后端框架**: Flask 2.3+
- **数据库**: MongoDB 6.0+
- **认证**: JWT Token
- **API文档**: Flask-RESTX (Swagger)
- **数据验证**: Marshmallow
- **测试**: pytest
- **部署**: Docker + Docker Compose

## 项目结构

```
glucose/
├── app/                    # 应用核心代码
│   ├── __init__.py        # Flask应用工厂
│   ├── models/            # 数据模型
│   ├── api/               # API路由和视图
│   ├── services/          # 业务逻辑服务
│   ├── utils/             # 工具函数
│   └── config.py          # 配置文件
├── tests/                 # 测试代码
├── docs/                  # API文档
├── docker/                # Docker配置
├── requirements.txt       # Python依赖
├── docker-compose.yml     # 容器编排
└── run.py                # 应用启动入口
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd glucose

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

```bash
# 启动MongoDB (使用Docker)
docker run -d -p 27017:27017 --name glucose-mongo mongo:6.0

# 或使用docker-compose
docker-compose up -d mongodb
```

### 3. 运行应用

```bash
# 开发模式
python run.py

# 或使用Flask命令
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

### 4. 访问API文档

启动后访问: http://localhost:5000/docs

## API 设计原则

- **RESTful 资源风格**: 接口清晰、语义明确、无状态
- **JSON 格式**: 统一使用JSON进行数据交换
- **参数校验**: 所有输入参数均需严格校验
- **异常处理**: 结构化异常响应
- **HTTP状态码**: 标准HTTP状态码传达处理结果
- **认证机制**: JWT Token认证，支持权限控制

## 核心功能模块

### 1. 血糖数据管理
- 数据上传 (POST /api/glucose)
- 数据查询 (GET /api/glucose)
- 数据更新 (PUT /api/glucose/{id})
- 数据删除 (DELETE /api/glucose/{id})

### 2. 用户管理
- 用户注册 (POST /api/users)
- 用户登录 (POST /api/auth/login)
- 用户信息 (GET /api/users/{id})

### 3. 设备管理
- 设备注册 (POST /api/devices)
- 设备列表 (GET /api/devices)
- 设备状态 (GET /api/devices/{id}/status)

### 4. 数据统计
- 统计报告 (GET /api/statistics)
- 趋势分析 (GET /api/analytics/trends)

## 开发指南

详细的开发文档请参考 `docs/` 目录：

- [API接口文档](docs/api.md)
- [数据库设计](docs/database.md)
- [部署指南](docs/deployment.md)
- [测试指南](docs/testing.md)

## 许可证

MIT License

# 血糖监测云端系统 RESTful API 详细设计文档

## 概述

本文档详细描述了血糖监测云端系统的 RESTful API 接口，完全基于 Flask 实现，满足科研级、工程级开发文档要求。涵盖接口功能、请求与响应格式、参数校验、异常处理、HTTP状态码、认证机制等所有技术细节。

## 设计原则

- **RESTful 资源风格**: 接口清晰、语义明确、无状态
- **JSON 格式为主**: 易于终端和前端对接
- **严格参数校验**: 所有输入参数均需校验，异常必须有结构化提示
- **标准HTTP状态码**: 采用HTTP状态码传达处理结果
- **预留认证机制**: Token/Key鉴权点，兼容未来升级
- **MECE原则**: 避免重复和遗漏，确保完整性

## 基础信息

- **基础URL**: `http://localhost:5000/api`
- **API版本**: v1.0
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: JWT Bearer Token
- **时间格式**: ISO8601 UTC格式 (YYYY-MM-DDTHH:MM:SSZ)

## 通用响应格式

### 成功响应结构

```json
{
  "status": "success",
  "message": "操作成功描述",
  "data": {
    // 具体业务数据
  }
}
```

### 错误响应结构

```json
{
  "status": "error",
  "message": "错误描述信息",
  "details": {
    // 详细错误信息，如验证失败的字段
  }
}
```

### 分页响应结构

```json
{
  "status": "success",
  "message": "查询成功",
  "data": {
    "records": [],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_count": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## 认证接口

### 用户登录

**接口**: `POST /auth/login`

**描述**: 用户登录获取访问令牌

**请求参数**:
```json
{
  "username": "string",
  "password": "string"
}
```

**成功响应**:
```json
{
  "status": "success",
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400,
    "token_type": "Bearer",
    "user": {
      "id": "507f1f77bcf86cd799439011",
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

### 刷新令牌

**接口**: `POST /auth/refresh`

**描述**: 使用刷新令牌获取新的访问令牌

**请求头**: `Authorization: Bearer <refresh_token>`

**成功响应**:
```json
{
  "status": "success",
  "message": "令牌刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400,
    "token_type": "Bearer"
  }
}
```

## 血糖数据接口

### 上传血糖数据

**接口**: `POST /glucose`

**描述**: 上传单条血糖测量数据

**请求头**: `Authorization: Bearer <access_token>`

**请求参数**:
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "timestamp": "2025-06-03T20:18:00Z",
  "glucose_value": 6.5,
  "unit": "mmol/L",
  "device_id": "sensor456",
  "note": "after dinner"
}
```

**字段说明**:
- `user_id`: 用户ID (必填)
- `timestamp`: ISO8601格式时间戳 (必填)
- `glucose_value`: 血糖值，范围0.1-50.0 (必填)
- `unit`: 单位，支持"mmol/L"或"mg/dL" (必填)
- `device_id`: 设备ID (可选)
- `note`: 备注信息 (可选)

**成功响应**:
```json
{
  "status": "success",
  "message": "血糖记录创建成功",
  "data": {
    "id": "507f1f77bcf86cd799439012",
    "user_id": "507f1f77bcf86cd799439011",
    "timestamp": "2025-06-03T20:18:00Z",
    "glucose_value": 6.5,
    "unit": "mmol/L",
    "device_id": "sensor456",
    "note": "after dinner",
    "created_at": "2025-06-03T20:18:30Z"
  }
}
```

### 查询血糖记录

**接口**: `GET /glucose`

**描述**: 获取血糖记录列表，支持分页和筛选

**请求头**: `Authorization: Bearer <access_token>`

**查询参数**:
- `user_id`: 用户ID (必填)
- `start_date`: 开始日期 (可选)
- `end_date`: 结束日期 (可选)
- `device_id`: 设备ID (可选)
- `page`: 页码，默认1 (可选)
- `per_page`: 每页数量，默认20 (可选)
- `sort_by`: 排序字段，默认timestamp (可选)
- `sort_order`: 排序方向，asc/desc，默认desc (可选)

**成功响应**:
```json
{
  "status": "success",
  "message": "查询成功",
  "data": {
    "records": [
      {
        "id": "507f1f77bcf86cd799439012",
        "user_id": "507f1f77bcf86cd799439011",
        "timestamp": "2025-06-03T20:18:00Z",
        "glucose_value": 6.5,
        "unit": "mmol/L",
        "device_id": "sensor456",
        "note": "after dinner",
        "created_at": "2025-06-03T20:18:30Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_count": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

## 用户管理接口

### 用户注册

**接口**: `POST /users`

**描述**: 创建新用户账户

**请求参数**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "full_name": "测试用户",
  "age": 30,
  "gender": "male",
  "phone": "13800138000"
}
```

**字段说明**:
- `username`: 用户名，3-50字符 (必填)
- `email`: 邮箱地址 (必填)
- `password`: 密码，6-128字符 (必填)
- `full_name`: 全名 (可选)
- `age`: 年龄，1-150 (可选)
- `gender`: 性别，male/female/other (可选)
- `phone`: 电话号码 (可选)

## 设备管理接口

### 注册设备

**接口**: `POST /devices`

**描述**: 为用户注册新的监测设备

**请求头**: `Authorization: Bearer <access_token>`

**请求参数**:
```json
{
  "device_id": "sensor456",
  "user_id": "507f1f77bcf86cd799439011",
  "device_name": "血糖仪001",
  "device_type": "glucose_meter",
  "manufacturer": "厂商名称",
  "model": "型号ABC",
  "firmware_version": "1.0.0"
}
```

**字段说明**:
- `device_id`: 设备唯一标识 (必填)
- `user_id`: 用户ID (必填)
- `device_name`: 设备名称 (必填)
- `device_type`: 设备类型，支持glucose_meter/cgm/insulin_pump/mobile_app (必填)
- `manufacturer`: 制造商 (可选)
- `model`: 型号 (可选)
- `firmware_version`: 固件版本 (可选)

## 统计分析接口

### 获取统计摘要

**接口**: `GET /statistics/summary`

**描述**: 获取血糖统计摘要信息

**请求头**: `Authorization: Bearer <access_token>`

**查询参数**:
- `start_date`: 开始日期 (可选)
- `end_date`: 结束日期 (可选)
- `device_id`: 设备ID (可选)

**成功响应**:
```json
{
  "status": "success",
  "message": "统计查询成功",
  "data": {
    "total_records": 100,
    "avg_glucose": 6.8,
    "max_glucose": 12.5,
    "min_glucose": 3.2,
    "std_glucose": 1.5,
    "normal_count": 70,
    "high_count": 20,
    "low_count": 10,
    "normal_percentage": 70.0,
    "high_percentage": 20.0,
    "low_percentage": 10.0,
    "time_range": {
      "start_date": "2025-05-01T00:00:00Z",
      "end_date": "2025-06-01T00:00:00Z"
    }
  }
}
```

## 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 400 | Bad Request | 请求参数错误或格式不正确 |
| 401 | Unauthorized | 未授权访问，需要有效的访问令牌 |
| 403 | Forbidden | 禁止访问，权限不足 |
| 404 | Not Found | 请求的资源不存在 |
| 422 | Unprocessable Entity | 请求格式正确但语义错误 |
| 429 | Too Many Requests | 请求频率超限 |
| 500 | Internal Server Error | 服务器内部错误 |

## 使用示例

### 完整的数据上传流程

1. **用户登录**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

2. **上传血糖数据**
```bash
curl -X POST http://localhost:5000/api/glucose \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "user_id": "507f1f77bcf86cd799439011",
    "timestamp": "2025-06-03T20:18:00Z",
    "glucose_value": 6.5,
    "unit": "mmol/L",
    "device_id": "sensor456",
    "note": "after dinner"
  }'
```

3. **查询血糖记录**
```bash
curl -X GET "http://localhost:5000/api/glucose?user_id=507f1f77bcf86cd799439011&page=1&per_page=10" \
  -H "Authorization: Bearer <access_token>"
```

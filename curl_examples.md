# 血糖监测API测试示例 (Glucose Monitoring API Test Examples)

## 服务器信息
- **API Base URL**: http://8.140.20.18:5000
- **API Prefix**: /api

## 1. 健康检查 (Health Check)

```bash
# 测试服务器是否正常运行
curl -X GET http://8.140.20.18:5000/

# 预期响应:
# {"status": "ok", "message": "Glucose Monitoring API is running"}
```

## 2. 上传血糖数据 (Upload Glucose Data)

### 基本血糖数据上传

```bash
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "timestamp": "2025-06-04T14:30:00Z",
    "glucose_value": 6.5,
    "unit": "mmol/L",
    "device_id": "glucose_meter_001",
    "note": "餐后2小时"
  }'
```

### 多个血糖数据示例

```bash
# 示例1: 空腹血糖
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "timestamp": "2025-06-04T08:00:00Z",
    "glucose_value": 5.2,
    "unit": "mmol/L",
    "device_id": "glucose_meter_001",
    "note": "空腹血糖"
  }'

# 示例2: 餐后血糖
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "timestamp": "2025-06-04T10:30:00Z",
    "glucose_value": 8.1,
    "unit": "mmol/L",
    "device_id": "glucose_meter_001",
    "note": "早餐后2小时"
  }'

# 示例3: 使用mg/dL单位
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_002",
    "timestamp": "2025-06-04T15:45:00Z",
    "glucose_value": 120,
    "unit": "mg/dL",
    "device_id": "cgm_sensor_002",
    "note": "午餐后血糖"
  }'

# 示例4: 最小必需字段
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_003",
    "timestamp": "2025-06-04T20:15:00Z",
    "glucose_value": 7.2,
    "unit": "mmol/L"
  }'
```

### 预期成功响应

```json
{
  "status": "success",
  "message": "血糖记录创建成功",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "user_id": "user_001",
    "timestamp": "2025-06-04T14:30:00Z",
    "glucose_value": 6.5,
    "unit": "mmol/L",
    "device_id": "glucose_meter_001",
    "note": "餐后2小时",
    "created_at": "2025-06-04T14:35:22Z"
  }
}
```

## 3. 查询血糖记录 (Query Glucose Records)

### 查询特定用户的所有记录

```bash
curl -X GET "http://8.140.20.18:5000/api/glucose?user_id=user_001"
```

### 带分页的查询

```bash
curl -X GET "http://8.140.20.18:5000/api/glucose?user_id=user_001&page=1&per_page=10"
```

### 按时间范围查询

```bash
curl -X GET "http://8.140.20.18:5000/api/glucose?user_id=user_001&start_date=2025-06-01T00:00:00Z&end_date=2025-06-05T23:59:59Z"
```

### 按设备查询

```bash
curl -X GET "http://8.140.20.18:5000/api/glucose?user_id=user_001&device_id=glucose_meter_001"
```

### 排序查询

```bash
# 按时间升序
curl -X GET "http://8.140.20.18:5000/api/glucose?user_id=user_001&sort_by=timestamp&sort_order=asc"

# 按血糖值降序
curl -X GET "http://8.140.20.18:5000/api/glucose?user_id=user_001&sort_by=glucose_value&sort_order=desc"
```

## 4. 获取单个记录 (Get Single Record)

```bash
# 需要先从查询结果中获取记录ID
curl -X GET http://8.140.20.18:5000/api/glucose/507f1f77bcf86cd799439011
```

## 5. 更新血糖记录 (Update Glucose Record)

```bash
curl -X PUT http://8.140.20.18:5000/api/glucose/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "timestamp": "2025-06-04T14:30:00Z",
    "glucose_value": 6.8,
    "unit": "mmol/L",
    "device_id": "glucose_meter_001",
    "note": "餐后2小时 (已更正)"
  }'
```

## 6. 删除血糖记录 (Delete Glucose Record)

```bash
curl -X DELETE http://8.140.20.18:5000/api/glucose/507f1f77bcf86cd799439011
```

## 7. 批量测试脚本 (Batch Test Script)

```bash
#!/bin/bash

# 设置API基础URL
API_BASE="http://8.140.20.18:5000"

echo "=== 血糖监测API测试 ==="

# 1. 健康检查
echo "1. 健康检查..."
curl -s -X GET $API_BASE/ | jq .

# 2. 上传多条血糖数据
echo -e "\n2. 上传血糖数据..."

# 空腹血糖
curl -s -X POST $API_BASE/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "timestamp": "2025-06-04T08:00:00Z",
    "glucose_value": 5.1,
    "unit": "mmol/L",
    "note": "空腹血糖"
  }' | jq .

# 餐后血糖
curl -s -X POST $API_BASE/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "timestamp": "2025-06-04T10:30:00Z",
    "glucose_value": 7.8,
    "unit": "mmol/L",
    "note": "早餐后2小时"
  }' | jq .

# 3. 查询数据
echo -e "\n3. 查询血糖记录..."
curl -s -X GET "$API_BASE/api/glucose?user_id=test_user" | jq .

echo -e "\n=== 测试完成 ==="
```

## 8. 错误处理示例

### 缺少必需字段

```bash
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "glucose_value": 6.5
  }'

# 预期错误响应:
# {
#   "status": "error",
#   "message": "输入数据验证失败",
#   "details": {
#     "timestamp": ["Missing data for required field."],
#     "unit": ["Missing data for required field."]
#   }
# }
```

### 无效的血糖值

```bash
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "timestamp": "2025-06-04T14:30:00Z",
    "glucose_value": -1.0,
    "unit": "mmol/L"
  }'
```

### 无效的单位

```bash
curl -X POST http://8.140.20.18:5000/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "timestamp": "2025-06-04T14:30:00Z",
    "glucose_value": 6.5,
    "unit": "invalid_unit"
  }'
```

## 9. 数据验证规则

- **user_id**: 必需，字符串，1-100字符
- **timestamp**: 必需，ISO8601格式 (YYYY-MM-DDTHH:MM:SSZ)
- **glucose_value**: 必需，浮点数，范围 0.1-50.0
- **unit**: 必需，只能是 "mmol/L" 或 "mg/dL"
- **device_id**: 可选，字符串，最大100字符
- **note**: 可选，字符串，最大500字符

## 10. 使用技巧

1. **使用 jq 格式化JSON输出**:
   ```bash
   curl -s ... | jq .
   ```

2. **保存响应到文件**:
   ```bash
   curl ... > response.json
   ```

3. **显示HTTP状态码**:
   ```bash
   curl -w "%{http_code}" ...
   ```

4. **详细输出**:
   ```bash
   curl -v ...
   ```

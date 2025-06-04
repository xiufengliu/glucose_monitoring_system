#!/bin/bash

# 血糖监测API调试脚本
# Glucose Monitoring API Debug Script

API_BASE="http://8.140.20.18:5000"

echo "=== 血糖监测API调试 ==="
echo "API服务器: $API_BASE"
echo ""

# 1. 健康检查
echo "1. 健康检查..."
curl -s $API_BASE/ | python3 -m json.tool
echo ""

# 2. 数据库状态检查
echo "2. 数据库状态检查..."
curl -s $API_BASE/db-status | python3 -m json.tool
echo ""

# 3. 测试端点（不需要数据库）
echo "3. 测试端点（不需要数据库）..."
curl -s -X POST $API_BASE/test-glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "timestamp": "2025-06-04T14:30:00Z",
    "glucose_value": 6.5,
    "unit": "mmol/L",
    "note": "测试数据"
  }' | python3 -m json.tool
echo ""

# 4. 测试真实的glucose API
echo "4. 测试真实的glucose API..."
response=$(curl -s -w "%{http_code}" -X POST $API_BASE/api/glucose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "debug_user",
    "timestamp": "2025-06-04T14:30:00Z",
    "glucose_value": 6.5,
    "unit": "mmol/L",
    "note": "调试数据"
  }')

http_code="${response: -3}"
body="${response%???}"

echo "HTTP状态码: $http_code"
echo "响应内容:"
echo "$body" | python3 -m json.tool
echo ""

# 5. 测试查询API
echo "5. 测试查询API..."
response=$(curl -s -w "%{http_code}" -X GET "$API_BASE/api/glucose?user_id=debug_user")

http_code="${response: -3}"
body="${response%???}"

echo "HTTP状态码: $http_code"
echo "响应内容:"
echo "$body" | python3 -m json.tool
echo ""

# 6. 测试API文档
echo "6. 测试API文档..."
curl -s -I $API_BASE/docs/ | head -5
echo ""

echo "=== 调试完成 ==="

#!/bin/bash

# 血糖监测API测试脚本
# Glucose Monitoring API Test Script

# 设置API基础URL
API_BASE="http://8.140.20.18:5000"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 血糖监测API测试脚本 ===${NC}"
echo -e "${BLUE}API服务器: $API_BASE${NC}"
echo ""

# 1. 健康检查
echo -e "${YELLOW}1. 健康检查...${NC}"
response=$(curl -s -w "%{http_code}" -X GET $API_BASE/)
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ 服务器正常运行${NC}"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ 服务器连接失败 (HTTP $http_code)${NC}"
    echo "$body"
    exit 1
fi

echo ""

# 2. 上传血糖数据
echo -e "${YELLOW}2. 上传血糖数据...${NC}"

# 测试数据数组
declare -a test_data=(
    '{"user_id":"test_user_001","timestamp":"2025-06-04T08:00:00Z","glucose_value":5.2,"unit":"mmol/L","device_id":"meter_001","note":"空腹血糖"}'
    '{"user_id":"test_user_001","timestamp":"2025-06-04T10:30:00Z","glucose_value":7.8,"unit":"mmol/L","device_id":"meter_001","note":"早餐后2小时"}'
    '{"user_id":"test_user_001","timestamp":"2025-06-04T14:15:00Z","glucose_value":6.5,"unit":"mmol/L","device_id":"meter_001","note":"午餐前"}'
    '{"user_id":"test_user_001","timestamp":"2025-06-04T16:30:00Z","glucose_value":8.1,"unit":"mmol/L","device_id":"meter_001","note":"午餐后2小时"}'
    '{"user_id":"test_user_002","timestamp":"2025-06-04T09:00:00Z","glucose_value":110,"unit":"mg/dL","device_id":"cgm_002","note":"连续血糖监测"}'
)

# 存储创建的记录ID
record_ids=()

for i in "${!test_data[@]}"; do
    echo -e "  ${BLUE}上传记录 $((i+1))...${NC}"
    
    response=$(curl -s -w "%{http_code}" -X POST $API_BASE/api/glucose \
        -H "Content-Type: application/json" \
        -d "${test_data[$i]}")
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "201" ]; then
        echo -e "    ${GREEN}✓ 上传成功${NC}"
        # 提取记录ID
        record_id=$(echo "$body" | jq -r '.data.id' 2>/dev/null)
        if [ "$record_id" != "null" ] && [ "$record_id" != "" ]; then
            record_ids+=("$record_id")
            echo "    记录ID: $record_id"
        fi
    else
        echo -e "    ${RED}✗ 上传失败 (HTTP $http_code)${NC}"
        echo "    $body" | jq . 2>/dev/null || echo "    $body"
    fi
done

echo ""

# 3. 查询血糖记录
echo -e "${YELLOW}3. 查询血糖记录...${NC}"

echo -e "  ${BLUE}查询用户 test_user_001 的所有记录...${NC}"
response=$(curl -s -w "%{http_code}" -X GET "$API_BASE/api/glucose?user_id=test_user_001")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" = "200" ]; then
    echo -e "    ${GREEN}✓ 查询成功${NC}"
    record_count=$(echo "$body" | jq '.data.records | length' 2>/dev/null)
    total_count=$(echo "$body" | jq '.data.pagination.total_count' 2>/dev/null)
    echo "    找到 $record_count 条记录，总计 $total_count 条"
    
    # 显示记录摘要
    echo "    记录摘要:"
    echo "$body" | jq -r '.data.records[] | "      \(.timestamp): \(.glucose_value) \(.unit) - \(.note)"' 2>/dev/null
else
    echo -e "    ${RED}✗ 查询失败 (HTTP $http_code)${NC}"
    echo "    $body"
fi

echo ""

# 4. 查询单个记录
if [ ${#record_ids[@]} -gt 0 ]; then
    echo -e "${YELLOW}4. 查询单个记录...${NC}"
    first_record_id="${record_ids[0]}"
    echo -e "  ${BLUE}查询记录ID: $first_record_id${NC}"
    
    response=$(curl -s -w "%{http_code}" -X GET "$API_BASE/api/glucose/$first_record_id")
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        echo -e "    ${GREEN}✓ 查询成功${NC}"
        echo "$body" | jq '.data' 2>/dev/null || echo "$body"
    else
        echo -e "    ${RED}✗ 查询失败 (HTTP $http_code)${NC}"
        echo "    $body"
    fi
    echo ""
fi

# 5. 更新记录
if [ ${#record_ids[@]} -gt 0 ]; then
    echo -e "${YELLOW}5. 更新血糖记录...${NC}"
    first_record_id="${record_ids[0]}"
    echo -e "  ${BLUE}更新记录ID: $first_record_id${NC}"
    
    update_data='{"user_id":"test_user_001","timestamp":"2025-06-04T08:00:00Z","glucose_value":5.5,"unit":"mmol/L","device_id":"meter_001","note":"空腹血糖 (已更正)"}'
    
    response=$(curl -s -w "%{http_code}" -X PUT "$API_BASE/api/glucose/$first_record_id" \
        -H "Content-Type: application/json" \
        -d "$update_data")
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        echo -e "    ${GREEN}✓ 更新成功${NC}"
        echo "$body" | jq '.data' 2>/dev/null || echo "$body"
    else
        echo -e "    ${RED}✗ 更新失败 (HTTP $http_code)${NC}"
        echo "    $body"
    fi
    echo ""
fi

# 6. 分页查询测试
echo -e "${YELLOW}6. 分页查询测试...${NC}"
echo -e "  ${BLUE}查询第1页，每页2条记录...${NC}"

response=$(curl -s -w "%{http_code}" -X GET "$API_BASE/api/glucose?user_id=test_user_001&page=1&per_page=2")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" = "200" ]; then
    echo -e "    ${GREEN}✓ 分页查询成功${NC}"
    page=$(echo "$body" | jq '.data.pagination.page' 2>/dev/null)
    per_page=$(echo "$body" | jq '.data.pagination.per_page' 2>/dev/null)
    total_pages=$(echo "$body" | jq '.data.pagination.total_pages' 2>/dev/null)
    echo "    当前页: $page/$total_pages，每页: $per_page 条"
else
    echo -e "    ${RED}✗ 分页查询失败 (HTTP $http_code)${NC}"
    echo "    $body"
fi

echo ""

# 7. 错误处理测试
echo -e "${YELLOW}7. 错误处理测试...${NC}"
echo -e "  ${BLUE}测试缺少必需字段...${NC}"

invalid_data='{"user_id":"test_user","glucose_value":6.5}'

response=$(curl -s -w "%{http_code}" -X POST $API_BASE/api/glucose \
    -H "Content-Type: application/json" \
    -d "$invalid_data")

http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" = "400" ]; then
    echo -e "    ${GREEN}✓ 正确返回验证错误${NC}"
    echo "$body" | jq '.details' 2>/dev/null || echo "$body"
else
    echo -e "    ${RED}✗ 错误处理异常 (HTTP $http_code)${NC}"
    echo "    $body"
fi

echo ""

# 8. 最终统计
echo -e "${YELLOW}8. 最终数据统计...${NC}"
response=$(curl -s -X GET "$API_BASE/api/glucose?user_id=test_user_001")
if [ $? -eq 0 ]; then
    total_records=$(echo "$response" | jq '.data.pagination.total_count' 2>/dev/null)
    echo -e "  ${GREEN}用户 test_user_001 总共有 $total_records 条血糖记录${NC}"
fi

response=$(curl -s -X GET "$API_BASE/api/glucose?user_id=test_user_002")
if [ $? -eq 0 ]; then
    total_records=$(echo "$response" | jq '.data.pagination.total_count' 2>/dev/null)
    echo -e "  ${GREEN}用户 test_user_002 总共有 $total_records 条血糖记录${NC}"
fi

echo ""
echo -e "${BLUE}=== 测试完成 ===${NC}"
echo -e "${GREEN}✓ API测试成功完成！数据已保存到MongoDB${NC}"
echo ""
echo "您可以使用以下命令查看所有数据:"
echo "curl -s \"$API_BASE/api/glucose?user_id=test_user_001\" | jq ."
echo "curl -s \"$API_BASE/api/glucose?user_id=test_user_002\" | jq ."

#!/bin/bash

# 用户系统测试脚本

echo "=========================================="
echo "DivineDaily 用户系统测试"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8080/api/v1"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_api() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local token=$5
    
    echo -e "${YELLOW}测试: ${name}${NC}"
    
    if [ -n "$token" ]; then
        response=$(curl -s -X $method "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${token}" \
            -d "$data")
    else
        response=$(curl -s -X $method "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    echo "响应: $response"
    echo ""
    
    # 返回响应供后续使用
    echo "$response"
}

echo "1. 测试普通用户注册"
echo "----------------------------------------"
register_response=$(test_api "普通用户注册" "POST" "/auth/register" '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "123456",
    "confirm_password": "123456"
}')

# 提取 token
user_token=$(echo $register_response | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "用户 Token: $user_token"
echo ""

echo "2. 测试管理员登录"
echo "----------------------------------------"
admin_response=$(test_api "管理员登录" "POST" "/auth/login" '{
    "username": "admin",
    "password": "594120"
}')

# 提取 admin token
admin_token=$(echo $admin_response | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "管理员 Token: $admin_token"
echo ""

echo "3. 测试获取当前用户信息（普通用户）"
echo "----------------------------------------"
test_api "获取用户信息" "GET" "/auth/me" "" "$user_token"

echo "4. 测试获取当前用户信息（管理员）"
echo "----------------------------------------"
test_api "获取管理员信息" "GET" "/auth/me" "" "$admin_token"

echo "5. 测试访问管理员接口（普通用户 - 应该失败）"
echo "----------------------------------------"
test_api "普通用户访问配置" "GET" "/configs/llm" "" "$user_token"

echo "6. 测试访问管理员接口（管理员 - 应该成功）"
echo "----------------------------------------"
test_api "管理员访问配置" "GET" "/configs/llm" "" "$admin_token"

echo "7. 测试邮箱登录"
echo "----------------------------------------"
test_api "邮箱登录" "POST" "/auth/login" '{
    "username": "test@example.com",
    "password": "123456"
}'

echo "8. 测试手机号注册"
echo "----------------------------------------"
test_api "手机号注册" "POST" "/auth/register" '{
    "username": "phoneuser",
    "phone": "13800138000",
    "password": "123456",
    "confirm_password": "123456"
}'

echo "=========================================="
echo "测试完成！"
echo "=========================================="

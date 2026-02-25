#!/bin/bash

# 用户管理 API 测试脚本

BASE_URL="http://localhost:48080/api/v1"
TOKEN=""

echo "=========================================="
echo "DivineDaily 用户管理 API 测试"
echo "=========================================="
echo ""

# 1. 登录获取 Token
echo "1. 登录获取 Token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"594120"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  echo $LOGIN_RESPONSE
  exit 1
fi

echo "✅ 登录成功，Token: ${TOKEN:0:20}..."
echo ""

# 2. 获取用户统计
echo "2. 获取用户统计..."
STATS_RESPONSE=$(curl -s -X GET "$BASE_URL/admin/users/stats" \
  -H "Authorization: Bearer $TOKEN")

echo $STATS_RESPONSE | python3 -m json.tool 2>/dev/null || echo $STATS_RESPONSE
echo ""

# 3. 获取用户列表
echo "3. 获取用户列表（前5个）..."
USERS_RESPONSE=$(curl -s -X GET "$BASE_URL/admin/users?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN")

echo $USERS_RESPONSE | python3 -m json.tool 2>/dev/null || echo $USERS_RESPONSE
echo ""

# 4. 搜索用户
echo "4. 搜索用户（关键词: admin）..."
SEARCH_RESPONSE=$(curl -s -X GET "$BASE_URL/admin/users?search=admin" \
  -H "Authorization: Bearer $TOKEN")

echo $SEARCH_RESPONSE | python3 -m json.tool 2>/dev/null || echo $SEARCH_RESPONSE
echo ""

# 5. 获取用户详情
echo "5. 获取用户详情（ID: 1）..."
DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/admin/users/1" \
  -H "Authorization: Bearer $TOKEN")

echo $DETAIL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $DETAIL_RESPONSE
echo ""

# 6. 获取审计日志
echo "6. 获取审计日志（最近5条）..."
LOGS_RESPONSE=$(curl -s -X GET "$BASE_URL/admin/audit-logs?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN")

echo $LOGS_RESPONSE | python3 -m json.tool 2>/dev/null || echo $LOGS_RESPONSE
echo ""

echo "=========================================="
echo "✅ 测试完成！"
echo "=========================================="
echo ""
echo "📝 API 端点列表："
echo "  - GET  /admin/users/stats          获取统计数据"
echo "  - GET  /admin/users                获取用户列表"
echo "  - GET  /admin/users/{id}           获取用户详情"
echo "  - POST /admin/users                创建用户"
echo "  - PUT  /admin/users/{id}           更新用户"
echo "  - DELETE /admin/users/{id}         删除用户"
echo "  - POST /admin/users/{id}/reset-password  重置密码"
echo "  - PUT  /admin/users/{id}/role      修改角色"
echo "  - PUT  /admin/users/{id}/status    修改状态"
echo "  - GET  /admin/audit-logs           获取审计日志"
echo ""
echo "🌐 访问管理后台："
echo "  - 后台地址: http://localhost:40081/admin"
echo "  - API 文档: http://localhost:48080/docs"
echo "  - 用户管理: http://localhost:40081/admin/users"
echo ""


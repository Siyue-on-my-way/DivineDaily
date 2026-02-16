#!/bin/bash

# Divine Daily 配置检查脚本

echo "=========================================="
echo "  Divine Daily 配置检查"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查项计数
TOTAL=0
PASSED=0

check_item() {
    TOTAL=$((TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

echo "1. 检查 Docker 环境"
echo "-------------------"
docker --version > /dev/null 2>&1
check_item $? "Docker 已安装"

docker-compose --version > /dev/null 2>&1 || docker compose version > /dev/null 2>&1
check_item $? "Docker Compose 已安装"

echo ""
echo "2. 检查项目文件"
echo "-------------------"
[ -f "/mnt/DivineDaily/docker/docker-compose.yaml" ]
check_item $? "docker-compose.yaml 存在"

[ -f "/mnt/DivineDaily/web/Dockerfile" ]
check_item $? "web/Dockerfile 存在"

[ -f "/mnt/DivineDaily/web-admin/Dockerfile" ]
check_item $? "web-admin/Dockerfile 存在"

[ -f "/mnt/DivineDaily/backend-python/Dockerfile" ]
check_item $? "backend-python/Dockerfile 存在"

echo ""
echo "3. 检查配置文件"
echo "-------------------"
[ -f "/mnt/DivineDaily/web/package.json" ]
check_item $? "web/package.json 存在"

[ -f "/mnt/DivineDaily/web-admin/package.json" ]
check_item $? "web-admin/package.json 存在"

[ -f "/mnt/DivineDaily/web/vite.config.ts" ]
check_item $? "web/vite.config.ts 存在"

[ -f "/mnt/DivineDaily/web-admin/vite.config.ts" ]
check_item $? "web-admin/vite.config.ts 存在"

echo ""
echo "4. 检查端口占用"
echo "-------------------"
! netstat -tuln 2>/dev/null | grep -q ":40080 " && ! ss -tuln 2>/dev/null | grep -q ":40080 "
check_item $? "端口 40080 (web) 未被占用"

! netstat -tuln 2>/dev/null | grep -q ":40081 " && ! ss -tuln 2>/dev/null | grep -q ":40081 "
check_item $? "端口 40081 (web-admin) 未被占用"

! netstat -tuln 2>/dev/null | grep -q ":48080 " && ! ss -tuln 2>/dev/null | grep -q ":48080 "
check_item $? "端口 48080 (backend) 未被占用"

! netstat -tuln 2>/dev/null | grep -q ":45432 " && ! ss -tuln 2>/dev/null | grep -q ":45432 "
check_item $? "端口 45432 (postgres) 未被占用"

echo ""
echo "5. 验证 Docker Compose 配置"
echo "-------------------"
cd /mnt/DivineDaily/docker
docker-compose config > /dev/null 2>&1
check_item $? "docker-compose.yaml 配置有效"

echo ""
echo "=========================================="
echo "  检查结果: $PASSED/$TOTAL 通过"
echo "=========================================="
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}✓ 所有检查通过！可以启动服务了。${NC}"
    echo ""
    echo "启动命令："
    echo "  cd /mnt/DivineDaily/docker"
    echo "  ./deploy.sh"
    echo ""
    echo "或者："
    echo "  cd /mnt/DivineDaily"
    echo "  ./start.sh"
    exit 0
else
    echo -e "${RED}✗ 有 $((TOTAL - PASSED)) 项检查失败，请修复后再启动。${NC}"
    exit 1
fi

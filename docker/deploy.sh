#!/bin/bash

# Divine Daily Docker 部署脚本

set -e

echo "=========================================="
echo "  Divine Daily Docker 部署"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 和 Docker Compose
echo "检查环境..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 环境检查通过${NC}"
echo ""

# 进入 docker 目录
cd "$(dirname "$0")"

# 显示菜单
echo "请选择操作："
echo "1) 启动所有服务"
echo "2) 停止所有服务"
echo "3) 重启所有服务"
echo "4) 查看服务状态"
echo "5) 查看日志"
echo "6) 构建镜像"
echo "7) 清理所有容器和数据"
echo "0) 退出"
echo ""

read -p "请输入选项 [0-7]: " choice

case $choice in
    1)
        echo -e "${YELLOW}启动所有服务...${NC}"
        docker-compose up -d
echo ""
        echo -e "${GREEN}✓ 服务启动成功！${NC}"
echo ""
        echo "访问地址："
        echo "  - 移动端应用: http://localhost:40080"
        echo "  - 管理后台: http://localhost:40081"
        echo "  - 后端 API: http://localhost:48080"
        echo "  - PostgreSQL: localhost:45432"
echo ""
        echo "默认管理员账号："
        echo "  - 用户名: admin"
        echo "  - 密码: 594120"
        ;;
    2)
        echo -e "${YELLOW}停止所有服务...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ 服务已停止${NC}"
        ;;
    3)
        echo -e "${YELLOW}重启所有服务...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ 服务已重启${NC}"
        ;;
    4)
        echo -e "${YELLOW}服务状态：${NC}"
        docker-compose ps
        ;;
    5)
        echo "请选择要查看的服务日志："
        echo "1) 所有服务"
        echo "2) PostgreSQL"
        echo "3) Python 后端"
        echo "4) 移动端前端"
        echo "5) 管理后台"
        read -p "请输入选项 [1-5]: " log_choice
        
        case $log_choice in
            1) docker-compose logs -f ;;
            2) docker-compose logs -f postgres ;;
            3) docker-compose logs -f backend-python ;;
            4) docker-compose logs -f web ;;
            5) docker-compose logs -f web-admin ;;
            *) echo -e "${RED}无效选项${NC}" ;;
        esac
        ;;
    6)
        echo -e "${YELLOW}构建所有镜像...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}✓ 镜像构建完成${NC}"
        ;;
    7)
        read -p "确认要清理所有容器和数据吗？这将删除数据库数据！(y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo -e "${YELLOW}清理所有容器和数据...${NC}"
            docker-compose down -v
            echo -e "${GREEN}✓ 清理完成${NC}"
        else
            echo "已取消"
        fi
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

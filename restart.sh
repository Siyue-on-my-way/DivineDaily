#!/bin/bash

# Divine Daily 重启脚本
# 用于快速重启所有服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"

# 打印带颜色的消息
print_header() {
    echo ""
    echo -e "${CYAN}=========================================="
    echo -e "  $1"
    echo -e "==========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 检查 Docker 环境
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker 服务未运行"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
}

# 显示服务信息
show_services() {
    print_header "Divine Daily 服务信息"
    
    echo -e "${CYAN}服务列表：${NC}"
    echo "  • PostgreSQL    - 数据库"
    echo "  • Backend       - Python FastAPI 后端"
    echo "  • Web           - 移动端前端"
    echo "  • Web-Admin     - 管理后台"
    echo ""
    
    echo -e "${CYAN}访问地址：${NC}"
    echo "  📱 移动端应用: http://localhost:40080"
    echo "  🔧 管理后台:   http://localhost:40081"
    echo "  🚀 后端 API:   http://localhost:48080"
    echo "  📚 API 文档:   http://localhost:48080/docs"
    echo ""
    
    echo -e "${CYAN}默认账号：${NC}"
    echo "  👤 用户名: admin"
    echo "  🔑 密码:   594120"
    echo ""
}

# 主函数
main() {
    print_header "Divine Daily 重启服务"
    
    # 检查 Docker 环境
    print_info "检查 Docker 环境..."
    check_docker
    print_success "Docker 环境正常"
    
    # 进入 docker 目录
    cd "$DOCKER_DIR"
    
    # 停止现有服务
    print_info "停止现有服务..."
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        docker-compose down
        print_success "服务已停止"
    else
        print_warning "没有运行中的服务"
    fi
    
    # 清理旧容器（可选）
    print_info "清理旧容器..."
    docker rm -f divine-daily-backend 2>/dev/null || true
    print_success "清理完成"
    
    # build 服务
    print_info "开始构建服务..."
    docker-compose build 
    # 启动服务
    print_info "启动所有服务..."
    docker-compose up -d
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 5
    
    # 检查服务状态
    print_header "服务状态"
    docker-compose ps
    
    # 显示服务信息
    show_services
    
    # 显示日志提示
    print_header "常用命令"
    echo "  查看所有日志:     docker-compose -f $DOCKER_DIR/docker-compose.yaml logs -f"
    echo "  查看后端日志:     docker-compose -f $DOCKER_DIR/docker-compose.yaml logs -f backend-python"
    echo "  查看移动端日志:   docker-compose -f $DOCKER_DIR/docker-compose.yaml logs -f web"
    echo "  查看管理后台日志: docker-compose -f $DOCKER_DIR/docker-compose.yaml logs -f web-admin"
    echo "  停止所有服务:     $SCRIPT_DIR/stop.sh"
    echo ""
    
    print_success "所有服务已启动！"
}

# 执行主函数
main

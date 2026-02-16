#!/bin/bash

# Divine Daily 停止脚本
# 用于停止所有服务

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
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
}

# 显示菜单
show_menu() {
    print_header "Divine Daily 停止服务"
    
    echo "请选择操作："
    echo "  1) 停止所有服务（保留数据）"
    echo "  2) 停止所有服务并删除数据卷（清空数据库）"
    echo "  3) 仅停止前端服务（web + web-admin）"
    echo "  4) 仅停止后端服务（backend + postgres）"
    echo "  0) 取消"
    echo ""
}

# 停止所有服务
stop_all() {
    print_info "停止所有服务..."
    cd "$DOCKER_DIR"
    
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        docker-compose down
        print_success "所有服务已停止"
    else
        print_warning "没有运行中的服务"
    fi
}

# 停止所有服务并删除数据
stop_all_with_volumes() {
    print_warning "警告：这将删除所有数据库数据！"
    read -p "确认要继续吗？(y/N): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "已取消操作"
        exit 0
    fi
    
    print_info "停止所有服务并删除数据卷..."
    cd "$DOCKER_DIR"
    
    docker-compose down -v
    print_success "所有服务已停止，数据已清除"
}

# 停止前端服务
stop_frontend() {
    print_info "停止前端服务..."
    cd "$DOCKER_DIR"
    
    docker-compose stop web web-admin
    print_success "前端服务已停止"
}

# 停止后端服务
stop_backend() {
    print_info "停止后端服务..."
    cd "$DOCKER_DIR"
    
    docker-compose stop backend-python postgres
    print_success "后端服务已停止"
}

# 显示服务状态
show_status() {
    print_header "当前服务状态"
    cd "$DOCKER_DIR"
    docker-compose ps
    echo ""
}

# 主函数
main() {
    # 检查 Docker 环境
    check_docker
    
    # 如果有参数，直接执行
    if [ $# -gt 0 ]; then
        case "$1" in
            --all|-a)
                stop_all
                ;;
            --clean|-c)
                stop_all_with_volumes
                ;;
            --frontend|-f)
                stop_frontend
                ;;
            --backend|-b)
                stop_backend
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  -a, --all        停止所有服务"
                echo "  -c, --clean      停止所有服务并删除数据"
                echo "  -f, --frontend   仅停止前端服务"
                echo "  -b, --backend    仅停止后端服务"
                echo "  -h, --help       显示帮助信息"
                echo ""
                echo "不带参数运行将显示交互式菜单"
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                echo "使用 --help 查看帮助"
                exit 1
                ;;
        esac
        
        show_status
        exit 0
    fi
    
    # 显示交互式菜单
    show_menu
    read -p "请输入选项 [0-4]: " choice
    
    case $choice in
        1)
            stop_all
            ;;
        2)
            stop_all_with_volumes
            ;;
        3)
            stop_frontend
            ;;
        4)
            stop_backend
            ;;
        0)
            print_info "已取消操作"
            exit 0
            ;;
        *)
            print_error "无效选项"
            exit 1
            ;;
    esac
    
    show_status
    
    print_header "提示"
    echo "  重新启动服务: $SCRIPT_DIR/restart.sh"
    echo ""
}

# 执行主函数
main "$@"

#!/bin/bash

# Divine Daily 日志查看脚本
# 用于快速查看各服务日志

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

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# 显示菜单
show_menu() {
    print_header "Divine Daily 日志查看"
    
    echo "请选择要查看的服务："
    echo "  1) 所有服务"
    echo "  2) PostgreSQL 数据库"
    echo "  3) Python 后端"
    echo "  4) 移动端前端 (web)"
    echo "  5) 管理后台 (web-admin)"
    echo "  0) 退出"
    echo ""
}

# 主函数
main() {
    cd "$DOCKER_DIR"
    
    # 如果有参数，直接执行
    if [ $# -gt 0 ]; then
        case "$1" in
            all|--all|-a)
                print_info "查看所有服务日志（Ctrl+C 退出）"
                docker-compose logs -f
                ;;
            postgres|db|--postgres|-p)
                print_info "查看 PostgreSQL 日志（Ctrl+C 退出）"
                docker-compose logs -f postgres
                ;;
            backend|api|--backend|-b)
                print_info "查看后端日志（Ctrl+C 退出）"
                docker-compose logs -f backend-python
                ;;
            web|frontend|--web|-w)
                print_info "查看移动端日志（Ctrl+C 退出）"
                docker-compose logs -f web
                ;;
            admin|web-admin|--admin|-m)
                print_info "查看管理后台日志（Ctrl+C 退出）"
                docker-compose logs -f web-admin
                ;;
            --help|-h)
                echo "用法: $0 [服务名]"
                echo ""
                echo "服务名:"
                echo "  all, -a          所有服务"
                echo "  postgres, -p     PostgreSQL 数据库"
                echo "  backend, -b      Python 后端"
                echo "  web, -w          移动端前端"
                echo "  admin, -m        管理后台"
                echo "  -h, --help       显示帮助信息"
                echo ""
                echo "不带参数运行将显示交互式菜单"
                exit 0
                ;;
            *)
                echo "未知服务: $1"
                echo "使用 --help 查看帮助"
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # 显示交互式菜单
    while true; do
        show_menu
        read -p "请输入选项 [0-5]: " choice
        
        case $choice in
            1)
                print_info "查看所有服务日志（Ctrl+C 返回菜单）"
                docker-compose logs -f || true
                ;;
            2)
                print_info "查看 PostgreSQL 日志（Ctrl+C 返回菜单）"
                docker-compose logs -f postgres || true
                ;;
            3)
                print_info "查看后端日志（Ctrl+C 返回菜单）"
                docker-compose logs -f backend-python || true
                ;;
            4)
                print_info "查看移动端日志（Ctrl+C 返回菜单）"
                docker-compose logs -f web || true
                ;;
            5)
                print_info "查看管理后台日志（Ctrl+C 返回菜单）"
                docker-compose logs -f web-admin || true
                ;;
            0)
                echo "退出"
                exit 0
                ;;
            *)
                echo "无效选项"
                ;;
        esac
    done
}

# 执行主函数
main "$@"

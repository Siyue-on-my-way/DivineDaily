#!/bin/bash

# DivineDaily 优化任务快速继续脚本
# 用于快速查看进度和继续未完成的任务

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DivineDaily 优化进度查看${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 显示进度文档
if [ -f "OPTIMIZATION_PROGRESS.md" ]; then
    echo -e "${GREEN}✓${NC} 找到进度文档"
    echo ""
    echo -e "${YELLOW}当前进度概览：${NC}"
    grep -A 4 "## 📊 整体进度" OPTIMIZATION_PROGRESS.md
    echo ""
else
    echo -e "${RED}✗${NC} 未找到进度文档"
    exit 1
fi

# 检查后端日志系统
echo -e "${YELLOW}检查后端日志系统...${NC}"
if docker logs divine-daily-backend-python --tail 10 2>&1 | grep -q "\[.*\] \[.*\] \[.*\]"; then
    echo -e "${GREEN}✓${NC} 日志系统正常工作"
else
    echo -e "${YELLOW}⚠${NC} 日志系统可能未生效"
fi

# 检查弃用警告
echo -e "${YELLOW}检查弃用警告...${NC}"
if docker logs divine-daily-backend-python 2>&1 | grep -q "utcnow.*deprecated"; then
    echo -e "${RED}✗${NC} 仍有弃用警告"
else
    echo -e "${GREEN}✓${NC} 无弃用警告"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  下一步任务建议${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "1. 继续替换 print 语句为 logger（约 15 个文件）"
echo "2. 实现 PWA 支持"
echo "3. 开始国际化实施"
echo ""
echo "详细进度请查看: OPTIMIZATION_PROGRESS.md"
echo ""

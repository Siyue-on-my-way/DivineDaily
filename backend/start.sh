#!/bin/bash

# Divine Daily Backend 启动脚本

echo "🔮 Starting Divine Daily Backend Server..."
echo ""

# 设置环境变量（如果 .env 文件存在则加载）
if [ -f .env ]; then
    echo "📝 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 设置默认值
export JWT_SECRET=${JWT_SECRET:-"your-secret-key-change-in-production"}
export SERVER_PORT=${SERVER_PORT:-"8080"}
export DB_HOST=${DB_HOST:-"localhost"}
export DB_PORT=${DB_PORT:-"5432"}
export DB_USER=${DB_USER:-"divinedaily"}
export DB_NAME=${DB_NAME:-"divinedaily"}

echo "⚙️  Configuration:"
echo "   Server Port: $SERVER_PORT"
echo "   Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "   JWT Secret: ${JWT_SECRET:0:20}..."
echo ""

# 启动服务器
echo "🚀 Starting server..."
./server

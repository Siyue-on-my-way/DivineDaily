#!/bin/bash

# 启动脚本

echo "🚀 启动 DivineDaily Backend (Python FastAPI)"

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在，从模板复制..."
    cp .env.template .env
    echo "✅ 请编辑 .env 文件配置数据库连接"
fi

# 检查依赖
echo "📦 检查依赖..."
pip install -r requirements.txt

# 运行数据库迁移
echo "🗄️  运行数据库迁移..."
alembic upgrade head

# 启动服务
echo "🎯 启动服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

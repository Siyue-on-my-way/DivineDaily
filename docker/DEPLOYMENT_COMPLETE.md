# DivineDaily Docker 部署完成

## 🚀 快速部署

### 方式 1: 使用一键部署脚本（推荐）

```bash
cd /mnt/DivineDaily/docker
./deploy.sh
```

### 方式 2: 使用 docker-compose 命令

```bash
cd /mnt/DivineDaily/docker

# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📦 部署的服务

1. **PostgreSQL 数据库**
   - 端口: 45432
   - 用户: divinedaily
   - 密码: divinedaily123
   - 数据库: divinedaily

2. **Python 后端**
   - 端口: 48080
   - API 文档: http://localhost:48080/docs
   - 健康检查: http://localhost:48080/health

3. **前端**
   - 端口: 40080
   - 访问: http://localhost:40080

## ✅ 已完成的配置

### 1. Dockerfile 优化
- ✅ 多阶段构建
- ✅ 非 root 用户运行
- ✅ 健康检查
- ✅ 依赖缓存优化

### 2. docker-compose.yaml 完善
- ✅ 网络配置
- ✅ 数据卷持久化
- ✅ 健康检查依赖
- ✅ 自动数据库迁移
- ✅ 环境变量配置
- ✅ 重启策略

### 3. 部署脚本
- ✅ deploy.sh - 一键部署
- ✅ 服务状态检查
- ✅ 日志查看提示

### 4. 文档
- ✅ README.md - 详细部署指南
- ✅ 故障排查
- ✅ 生产环境配置

## 🔧 启动流程

```
1. 启动 PostgreSQL
   ↓
2. 等待数据库就绪（健康检查）
   ↓
3. 运行数据库迁移（alembic upgrade head）
   ↓
4. 启动 Python 后端
   ↓
5. 启动前端
```

## 📝 环境变量

在 `/mnt/DivineDaily/docker/.env` 中配置：

```bash
# JWT 密钥（生产环境必须修改）
JWT_SECRET=your-secret-key-change-in-production

# Go 代理（可选）
GOPROXY=https://goproxy.cn,direct
```

## 🎯 验证部署

```bash
# 1. 检查服务状态
docker-compose ps

# 2. 查看日志
docker-compose logs -f backend-python

# 3. 测试健康检查
curl http://localhost:48080/health

# 4. 访问 API 文档
open http://localhost:48080/docs

# 5. 访问前端
open http://localhost:40080
```

## 🔄 更新部署

```bash
cd /mnt/DivineDaily/docker

# 重新构建并启动
docker-compose up -d --build

# 或使用部署脚本
./deploy.sh
```

## 🛠️ 常用命令

```bash
# 查看所有容器
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 进入容器
docker-compose exec backend-python bash
docker-compose exec postgres psql -U divinedaily

# 查看资源使用
docker stats
```

## 🎊 部署完成

所有配置已完善，可以直接使用！

**立即部署：**
```bash
cd /mnt/DivineDaily/docker
./deploy.sh
```

或

```bash
cd /mnt/DivineDaily/docker
docker-compose up -d --build
```

# Divine Daily Docker 部署指南

## 📦 服务架构

本项目使用 Docker Compose 编排以下服务：

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| PostgreSQL | divine-daily-postgres | 45432 | 数据库 |
| Python 后端 | divine-daily-backend-python | 48080 | FastAPI 后端 |
| 移动端前端 | divine-daily-web | 40080 | React 移动端应用 |
| 管理后台 | divine-daily-web-admin | 40081 | React 管理后台 |

---

## 🚀 快速开始

### 1. 使用部署脚本（推荐）

```bash
cd /mnt/DivineDaily/docker
./deploy.sh
```

选择操作：
- `1` - 启动所有服务
- `2` - 停止所有服务
- `3` - 重启所有服务
- `4` - 查看服务状态
- `5` - 查看日志
- `6` - 构建镜像
- `7` - 清理所有容器和数据

### 2. 手动启动

```bash
cd /mnt/DivineDaily/docker

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

- **移动端应用**: http://localhost:40080
- **管理后台**: http://localhost:40081
- **后端 API**: http://localhost:48080
- **API 文档**: http://localhost:48080/docs
- **PostgreSQL**: localhost:45432

---

## 🔐 默认账号

### 管理员账号
- 用户名: `admin`
- 密码: `594120`

### 数据库
- 用户名: `divinedaily`
- 密码: `divinedaily123`
- 数据库: `divinedaily`

---

## 📋 服务详情

### PostgreSQL 数据库
- 镜像: `postgres:14`
- 数据持久化: `postgres_data` volume
- 健康检查: 每 10 秒检查一次

### Python 后端
- 基于 FastAPI
- 自动运行数据库迁移
- 自动创建管理员账号
- 支持热重载

### 移动端前端 (web)
- React 19 + TypeScript
- Vite 开发服务器
- 端口: 40080
- 支持热重载

### 管理后台 (web-admin)
- React 19 + TypeScript
- Vite 开发服务器
- 端口: 40081
- 支持热重载

---

## 🔧 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看特定服务日志
```bash
# 查看后端日志
docker-compose logs -f backend-python

# 查看移动端日志
docker-compose logs -f web

# 查看管理后台日志
docker-compose logs -f web-admin

# 查看数据库日志
docker-compose logs -f postgres
```

### 重启特定服务
```bash
# 重启后端
docker-compose restart backend-python

# 重启移动端
docker-compose restart web

# 重启管理后台
docker-compose restart web-admin
```

### 进入容器
```bash
# 进入后端容器
docker exec -it divine-daily-backend-python sh

# 进入移动端容器
docker exec -it divine-daily-web sh

# 进入管理后台容器
docker exec -it divine-daily-web-admin sh

# 进入数据库容器
docker exec -it divine-daily-postgres psql -U divinedaily
```

### 重新构建镜像
```bash
# 重新构建所有镜像
docker-compose build --no-cache

# 重新构建特定服务
docker-compose build --no-cache web
docker-compose build --no-cache web-admin
docker-compose build --no-cache backend-python
```

### 清理和重置
```bash
# 停止并删除容器（保留数据）
docker-compose down

# 停止并删除容器和数据卷（清空数据库）
docker-compose down -v

# 清理未使用的镜像
docker image prune -a
```

---

## 🐛 故障排查

### 1. 端口被占用

如果端口被占用，可以修改 `docker-compose.yaml` 中的端口映射：

```yaml
ports:
  - "40080:40080"  # 改为 "8080:40080"
```

### 2. 数据库连接失败

检查数据库是否健康：
```bash
docker-compose ps postgres
```

查看数据库日志：
```bash
docker-compose logs postgres
```

### 3. 前端无法连接后端

检查环境变量配置：
```bash
docker-compose config
```

确保 `VITE_API_PROXY_TARGET` 指向正确的后端地址。

### 4. 热重载不工作

在 Docker 中，需要启用 `usePolling`：
```typescript
// vite.config.ts
server: {
  watch: {
    usePolling: true,
    }
}
```

### 5. 容器启动失败

查看详细日志：
```bash
docker-compose logs -f [service-name]
```

重新构建镜像：
```bash
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

---

## 📊 性能优化

### 1. 使用 .dockerignore

在各个项目根目录创建 `.dockerignore`：

```
node_modules
dist
.git
.env
*.log
```

### 2. 多阶段构建（生产环境）

修改 Dockerfile 使用多阶段构建：

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. 使用 Docker 缓存

构建时利用缓存：
```bash
docker-compose build
```

---

## 🔒 安全建议

### 生产环境配置

1. **修改默认密码**
   ```yaml
   environment:
     POSTGRES_PASSWORD: your-strong-password
     JWT_SECRET: your-secret-key
   ```

2. **使用环境变量文件**
```bash
   # 创建 .env 文件
   JWT_SECRET=your-secret-key
   POSTGRES_PASSWORD=your-db-password
   ```

3. **限制端口暴露**
   ```yaml
   # 只在内网暴露
   ports:
     - "127.0.0.1:45432:5432"
   ```

4. **使用 HTTPS**
   - 配置 Nginx 反向代理
   - 使用 Let's Encrypt 证书

---

## 📝 环境变量

### 后端环境变量
- `DB_HOST` - 数据库主机
- `DB_PORT` - 数据库端口
- `DB_USER` - 数据库用户
- `DB_PASSWORD` - 数据库密码
- `DB_NAME` - 数据库名称
- `JWT_SECRET` - JWT 密钥
- `JWT_ALGORITHM` - JWT 算法
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token 过期时间

### 前端环境变量
- `VITE_API_PROXY_TARGET` - API 代理目标
- `VITE_API_BASE_URL` - API 基础路径
- `VITE_APP_NAME` - 应用名称

---

## 🎯 下一步

1. 访问移动端应用测试占卜功能
2. 使用管理员账号登录管理后台
3. 配置 LLM 和 Prompt 模板
4. 查看 API 文档了解接口

---

## 📞 支持

如有问题，请查看：
- 项目文档: `/mnt/DivineDaily/README.md`
- 后端文档: `/mnt/DivineDaily/backend-python/README.md`
- 前端文档: `/mnt/DivineDaily/web/README.md`
- 管理后台文档: `/mnt/DivineDaily/web-admin/README.md`

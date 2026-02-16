# Divine Daily 项目总览

## 📦 项目结构

```
DivineDaily/
├── backend-python/          # Python FastAPI 后端
├── web/                     # 移动端前端（React）
├── web-admin/              # 管理后台前端（React）
├── docker/                 # Docker 配置
├── start.sh               # 快速启动脚本
├── check.sh               # 配置检查脚本
└── README.md              # 本文件
```

---

## 🚀 快速开始

### 1. 检查配置
```bash
./check.sh
```

### 2. 启动所有服务
```bash
./start.sh
```

或者使用交互式脚本：
```bash
cd docker
./deploy.sh
```

### 3. 访问应用

| 服务 | 地址 | 说明 |
|------|------|------|
| 📱 移动端应用 | http://localhost:40080 | 普通用户占卜应用 |
| 🔧 管理后台 | http://localhost:40081 | 管理员配置后台 |
| 🚀 后端 API | http://localhost:48080 | FastAPI 后端 |
| 📚 API 文档 | http://localhost:48080/docs | Swagger 文档 |

---

## 🔐 默认账号

### 管理员
- 用户名: `admin`
- 密码: `594120`

---

## 📋 服务说明

### 移动端应用 (web)
- **端口**: 40080
- **技术栈**: React 19 + TypeScript + Vite
- **功能**: 周易占卜、塔罗牌、每日运势、历史记录

### 管理后台 (web-admin)
- **端口**: 40081
- **技术栈**: React 19 + TypeScript + Vite
- **功能**: LLM 配置、Prompt 管理、系统统计

### Python 后端 (backend-python)
- **端口**: 48080
- **技术栈**: FastAPI + SQLAlchemy + PostgreSQL
- **功能**: 认证、占卜、运势、配置管理

### PostgreSQL 数据库
- **端口**: 45432
- **用户**: divinedaily
- **密码**: divinedaily123

---

## 🔧 开发指南

### 本地开发（不使用 Docker）

#### 后端
```bash
cd backend-python
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8080
```

#### 移动端
```bash
cd web
npm install
npm run dev
# 访问 http://localhost:5173
```

#### 管理后台
```bash
cd web-admin
npm install
npm run dev
# 访问 http://localhost:5174
```

### Docker 开发

```bash
# 启动所有服务
cd docker
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📚 文档

- [前端拆分总结](./FRONTEND_SPLIT_SUMMARY.md)
- [Docker 部署完成](./DOCKER_DEPLOYMENT_COMPLETE.md)
- [Docker 部署指南](./docker/README.md)
- [后端文档](./backend-python/README.md)
- [移动端文档](./web/README.md)
- [管理后台文档](./web-admin/README.md)

---

## 🎯 功能特性

### 占卜功能
- ✅ 周易六爻占卜
- ✅ 塔罗牌占卜（单张、三张、十字牌阵）
- ✅ 每日运势
- ✅ 占卜历史记录
- ✅ AI 智能解读

### 用户系统
- ✅ 用户注册/登录
- ✅ JWT 认证
- ✅ 角色权限（admin/normal）
- ✅ 个人中心
- ✅ 占卜统计

### 管理功能
- ✅ LLM 配置管理
- ✅ Prompt 模板管理
- ✅ 系统统计
- ✅ 用户管理（规划中）

---

## 🛠️ 技术栈

### 后端
- FastAPI - 现代高性能 Web 框架
- SQLAlchemy - 异步 ORM
- PostgreSQL - 数据库
- Alembic - 数据库迁移
- PyJWT - JWT 认证

### 前端
- React 19 - UI 框架
- TypeScript - 类型安全
- Vite - 构建工具
- React Router - 路由管理
- Axios - HTTP 客户端
- Framer Motion - 动画

### 部署
- Docker - 容器化
- Docker Compose - 服务编排
- Nginx - 反向代理（可选）

---

## 📊 项目统计

- **代码行数**: ~10,000+ 行
- **API 端点**: 25+ 个
- **前端页面**: 12+ 个
- **数据模型**: 8 个
- **服务层**: 11 个

---

## 🔒 安全建议

### 生产环境必须修改

1. **JWT 密钥**
   ```bash
   JWT_SECRET=your-strong-secret-key
   ```

2. **数据库密码**
   ```bash
   POSTGRES_PASSWORD=your-strong-password
   ```

3. **管理员密码**
   - 首次登录后立即修改

4. **使用 HTTPS**
   - 配置 SSL 证书
   - 使用 Nginx 反向代理

---

## 🐛 故障排查

### 常见问题

1. **端口被占用**
   - 修改 docker-compose.yaml 中的端口映射

2. **数据库连接失败**
   - 检查 PostgreSQL 容器状态
   - 查看数据库日志

3. **前端无法连接后端**
   - 检查 VITE_API_PROXY_TARGET 配置
   - 确认后端服务已启动

4. **热重载不工作**
   - 确保 vite.config.ts 中启用了 usePolling

---

## 📞 支持

如有问题，请查看：
- 项目文档
- API 文档: http://localhost:48080/docs
- GitHub Issues

---

## 📝 更新日志

### 2026-02-13
- ✅ 完成前端项目拆分（web 和 web-admin）
- ✅ 配置 Docker Compose
- ✅ 创建部署脚本
- ✅ 完善文档

### 2026-02-12
- ✅ 完成用户系统接入
- ✅ 完成前端用户系统集成

### 2026-02-13
- ✅ 完成 Python 后端开发
- ✅ 完成所有核心功能

---

## 🎉 致谢

感谢所有贡献者的努力！

---

## 📄 许可证

MIT License

---

**Divine Daily - 让占卜更智能** 🔮✨

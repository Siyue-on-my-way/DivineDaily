# DivineDaily - 智能占卜应用

一个结合传统玄学（周易、塔罗）与现代 AI 技术的智能占卜应用。

---

## 📚 文档导航

### 核心文档（必读）

1. **[PROJECT.md](./PROJECT.md)** - 项目概览
   - 技术架构
   - 核心业务模块
   - 数据模型
   - 快速开始

2. **[DEVELOPMENT.md](./DEVELOPMENT.md)** - 开发指南
   - 环境搭建
   - 项目结构
   - 核心服务开发
   - 算法开发
   - 测试与调试

3. **[API.md](./API.md)** - API 参考
   - 认证接口
   - 占卜接口
   - 每日运势接口
   - 用户档案接口
   - 管理接口

### 设计文档

- **[a-docs/design/ARCH_AND_DESIGN.md](./a-docs/design/ARCH_AND_DESIGN.md)** - 架构与设计
- **[a-docs/design/daily_fortune_integration.md](./a-docs/design/daily_fortune_integration.md)** - 每日运势集成设计

### 实施报告

- **[a-docs/plan/手机端重设计完成报告.md](./a-docs/plan/手机端重设计完成报告.md)** - 移动端设计
- **[a-docs/plan/塔罗牌占卜结果优化完成报告.md](./a-docs/plan/塔罗牌占卜结果优化完成报告.md)** - 塔罗优化

### 子项目文档

- **[backend-python/README.md](./backend-python/README.md)** - Python 后端
- **[web/README.md](./web/README.md)** - 移动端前端
- **[web-admin/README.md](./web-admin/README.md)** - 管理后台
- **[docker/README.md](./docker/README.md)** - Docker 部署

---

## 🚀 快速开始

### 1. 启动服务

```bash
cd /mnt/DivineDaily
./restart.sh
```

### 2. 访问应用

- 🌐 统一入口（Nginx）：http://localhost:6180
- 📱 移动端（Nginx 路由）：http://localhost:6180
- 🔧 管理后台（直连）：http://localhost:6181
- 🚀 后端 API（Nginx 路由）：http://localhost:6180/api/v1
- 📚 API 文档（直连后端）：http://localhost:48080/docs

### 3. 默认账号

- 用户名：`admin`
- 密码：`594120`

---

## 🏗️ 技术栈

**后端**：Python 3.11 + FastAPI + PostgreSQL 14  
**前端**：React 19 + TypeScript + Vite 5  
**部署**：Docker + Docker Compose

---

## 📦 项目结构

```
DivineDaily/
├── PROJECT.md              # 项目概览（必读）
├── DEVELOPMENT.md          # 开发指南（必读）
├── API.md                  # API 参考（必读）
├── README.md               # 本文件
├── restart.sh              # 重启脚本
├── stop.sh                 # 停止脚本
├── logs.sh                 # 日志查看
├── check.sh                # 配置检查
├── backend-python/         # Python 后端
├── web/                    # 移动端前端
├── web-admin/              # 管理后台
├── docker/                 # Docker 配置
└── a-docs/                 # 设计文档
    ├── design/             # 架构设计
    └── plan/               # 实施报告
```

---

## 🎯 核心功能

- 🔮 **周易六爻占卜** - 传统六爻起卦 + AI 解读
- 🎴 **塔罗牌占卜** - 多种牌阵 + 深度解读
- 📅 **每日运势** - 算法计算 + AI 生成
- 🤖 **智能意图识别** - 自动识别问题类型
- 📊 **历史记录** - 占卜历史查询与分析

---

## 🔧 常用命令

```bash
# 重启所有服务
./restart.sh

# 停止所有服务
./stop.sh --all

# 查看后端日志
./logs.sh backend

# 检查配置
./check.sh
```

---

## 📖 开发指南

### 新手入门

1. 阅读 [PROJECT.md](./PROJECT.md) 了解项目架构
2. 阅读 [DEVELOPMENT.md](./DEVELOPMENT.md) 搭建开发环境
3. 阅读 [API.md](./API.md) 了解接口规范

### 开发新功能

1. 查阅 [a-docs/design/ARCH_AND_DESIGN.md](./a-docs/design/ARCH_AND_DESIGN.md) 确保符合架构
2. 参考 [DEVELOPMENT.md](./DEVELOPMENT.md) 中的开发示例
3. 查看 [API.md](./API.md) 了解接口设计规范

---

## 🔐 安全提示

**生产环境必须修改**：

1. JWT 密钥：`JWT_SECRET`
2. 数据库密码：`POSTGRES_PASSWORD`
3. 管理员密码
4. 使用 HTTPS

---

## 📝 更新日志

### 2026-02-22
- ✅ 整理项目文档，删除冗余内容
- ✅ 创建核心文档：PROJECT.md, DEVELOPMENT.md, API.md

### 2026-02-21
- ✅ 完成每日运势 Assistant 配置
- ✅ 集成传统算法

### 2026-02-20
- ✅ 实现传统算法服务
- ✅ 完成数据库迁移

---

## 📞 支持

- 项目文档：查看 `PROJECT.md`
- API 文档：http://localhost:48080/docs
- 开发指南：查看 `DEVELOPMENT.md`

---

## 📄 许可证

MIT License

---

**Divine Daily - 让占卜更智能** 🔮✨

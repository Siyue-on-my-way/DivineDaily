# DivineDaily Backend - Python FastAPI 版本

## 🎉 项目概述

DivineDaily 后端 Python 版本，使用 FastAPI + SQLAlchemy 构建的现代化占卜应用后端服务。

## ✨ 核心功能

- 🔐 **用户认证** - JWT 令牌、角色权限
- 📅 **时间转换** - 公历转农历、节气节日
- 🎴 **易经占卜** - 六爻生成、卦象解析
- 🃏 **塔罗占卜** - 随机抽牌、正逆位
- 🔮 **每日运势** - 综合评分、多维建议

## 🚀 快速开始

### 环境要求
- Python 3.11+
- PostgreSQL 14+
- Docker (可选)

### 安装运行

```bash
# 克隆项目
cd /mnt/DivineDaily/backend-python

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.template .env
# 编辑 .env 文件，配置数据库等信息

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Docker 部署

```bash
docker-compose up -d
```

### 访问 API 文档

启动后访问: http://localhost:8080/docs

## 📊 项目进度

**总体进度: 62.5%** (5/8 阶段完成)

- ✅ Phase 1: 基础架构 (100%)
- ✅ Phase 2: 认证系统 (100%)
- ✅ Phase 3: 时间转换服务 (100%)
- ✅ Phase 4: 占卜核心服务 (100%)
- ✅ Phase 5: 每日运势服务 (100%)
- ⏳ Phase 6: 用户档案服务 (0%)
- ⏳ Phase 7: 智能预处理 (0%)
- ⏳ Phase 8: 管理配置 (0%)

## 📁 项目结构

```
backend-python/
├── app/
│   ├── api/v1/              # API 路由 (9个端点)
│   │   ├── auth.py          # 认证接口
│   │   ├── time_convert.py  # 时间转换
│   │   ├── divination.py    # 占卜接口
│   │   └── daily_fortune.py # 运势接口
│   ├── core/                # 核心功能
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── security.py      # 安全工具
│   │   └── exceptions.py    # 异常处理
│   ├── models/              # 数据模型
│   │   ├── user.py          # 用户模型
│   │   ├── divination.py    # 占卜模型
│   │   └── daily_fortune.py # 运势模型
│   ├── schemas/             # Pydantic 模式
│   ├── services/            # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── time_convert_service.py
│   │   ├── iching_service.py
│   │   ├── tarot_service.py
│   │   ├── divination_service.py
│   │   └── daily_fortune_service.py
│   ├── repositories/        # 数据访问层
│   ├── utils/               # 工具函数
│   ├── dependencies.py      # 依赖注入
│   └── main.py              # 应用入口
├── alembic/                 # 数据库迁移
├── tests/                   # 测试文件 (5个)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔌 API 端点

### 认证 (Auth)
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/me` - 获取当前用户

### 时间转换 (Time)
- `POST /api/v1/time/convert` - 公历转农历
- `POST /api/v1/time/daily_info` - 获取每日信息

### 占卜 (Divination)
- `POST /api/v1/divinations/iching` - 易经占卜
- `POST /api/v1/divinations/tarot` - 塔罗占卜

### 运势 (Fortune)
- `POST /api/v1/daily_fortune` - 获取每日运势

## 🧪 测试

项目包含 5 个独立测试脚本，无需数据库即可运行：

```bash
# 认证功能测试
python3 test_auth_standalone.py

# 时间转换测试
python3 test_time_convert.py

# 易经占卜测试
python3 test_iching_standalone.py

# 占卜服务测试
python3 test_divination_standalone.py

# 运势生成测试
python3 test_daily_fortune_standalone.py
```

## 🛠️ 技术栈

- **FastAPI** - 现代高性能 Web 框架
- **SQLAlchemy** - 强大的异步 ORM
- **Alembic** - 数据库迁移工具
- **Pydantic** - 数据验证
- **PostgreSQL** - 主数据库
- **PyJWT** - JWT 令牌
- **bcrypt** - 密码加密

## 📚 文档

- `PROJECT_STATUS.md` - 项目状态和进度
- `MIGRATION_SUMMARY.md` - 迁移总结
- `PHASE1_COMPLETE.md` - 基础架构报告
- `PHASE3_REPORT.md` - 时间转换报告
- `PHASE4_REPORT.md` - 占卜核心报告
- `PHASE5_REPORT.md` - 每日运势报告

## 📈 统计数据

- Python 文件: 37 个
- 代码行数: ~2400 行
- API 端点: 9 个
- 数据模型: 3 个
- 服务层: 6 个
- 测试脚本: 6 个
- 数据库迁移: 3 个

## 🎯 特性亮点

### 1. 现代化架构
- 异步 I/O 支持
- 清晰的分层设计
- 依赖注入模式

### 2. 类型安全
- Pydantic 数据验证
- 完整的类型注解
- 自动 API 文档

### 3. 易于测试
- 独立测试脚本
- 无数据库依赖
- 清晰的测试输出

### 4. 访客友好
- 支持未登录访问
- 可选用户认证
- 降低使用门槛

## 🔮 核心算法

### 易经占卜
- 三枚铜钱摇卦法
- 六爻生成算法
- 本卦/变卦/互卦分析
- 五行属性计算

### 塔罗占卜
- 随机抽牌算法
- 正逆位判断
- 多种牌阵支持
- 可重现随机性

### 每日运势
- 综合评分系统 (0-100)
- 四维建议（财运、事业、感情、健康）
- 幸运指南（颜色、数字、方位、时辰）
- 宜忌事项生成

## 🚧 待完成功能

- [ ] 用户档案服务
- [ ] 智能预处理
- [ ] 管理配置功能
- [ ] LLM 集成
- [ ] 完整的 64 卦数据
- [ ] 完整的 78 张塔罗牌数据

## 📝 开发日志

- 2026-02-13: Phase 5 完成 - 每日运势服务
- 2026-02-13: Phase 4 完成 - 占卜核心服务
- 2026-02-13: Phase 3 完成 - 时间转换服务
- 2026-02-13: Phase 2 完成 - 认证系统
- 2026-02-13: Phase 1 完成 - 基础架构

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**当前状态**: ✅ 核心功能已完成，可以开始使用和测试  
**最后更新**: 2026-02-13

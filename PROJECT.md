# DivineDaily - 智能占卜应用

## 项目概述

DivineDaily 是一个结合传统玄学（周易、塔罗）与现代 AI 技术的智能占卜应用，为用户提供个性化的运势分析和决策建议。

**核心特性**：
- 🔮 周易六爻占卜
- 🎴 塔罗牌占卜
- 📅 每日运势（算法 + AI）
- 🤖 智能意图识别
- 📊 历史记录分析

---

## 技术架构

### 技术栈

**后端**：
- Python 3.11 + FastAPI
- PostgreSQL 14
- SQLAlchemy (异步 ORM)
- Alembic (数据库迁移)

**前端**：
- React 19 + TypeScript
- Vite 5
- React Router 6

**部署**：
- Docker + Docker Compose
- Nginx (可选)

---

## 核心架构

### 三层智能漏斗

```
用户提问
    ↓
【第一层：意图识别】
    ├─ binary_choice (决策)
    ├─ daily_luck (运势)
    ├─ deep_analysis (深度分析)
    └─ knowledge (知识问答)
    ↓
【第二层：智能路由】
    ├─ 每日运势 → DailyFortuneService
    ├─ 周易占卜 → IChingService
    └─ 塔罗占卜 → TarotService
    ↓
【第三层：LLM 增强】
    ├─ 算法计算（传统命理）
    ├─ LLM 解读（智能分析）
    └─ 结果融合
```

---

## 核心业务模块

### 1. 每日运势系统

**算法驱动 + LLM 解读**

```python
# 核心流程
用户档案（生肖、八字）
    ↓
时间信息（农历、节气、干支）
    ↓
FortuneAlgorithmService（传统算法）
    ├─ 五行生克评分
    ├─ 生肖相冲相合评分
    ├─ 节气加成
    └─ 宜忌生成
    ↓
LLM 增强解读
    ↓
返回结构化运势
```

**评分算法**：
```
综合评分 = 基础分(50) + 五行分(±40) + 生肖分(±20) + 节气分(±15)
```

**五行关系**：
- 相生：木→火→土→金→水→木
- 相克：木克土、土克水、水克火、火克金、金克木

**生肖关系**：
- 相冲：鼠↔马、牛↔羊、虎↔猴、兔↔鸡、龙↔狗、蛇↔猪
- 相合：鼠-龙-猴、牛-蛇-鸡、虎-马-狗、兔-羊-猪

### 2. 周易占卜系统

**六爻起卦 + 卦象解析**

```python
# 摇卦流程
session_id（随机种子）
    ↓
模拟投掷 3 枚硬币 × 6 次
    ├─ 6 = 老阴（变爻）
    ├─ 7 = 少阳
    ├─ 8 = 少阴
    └─ 9 = 老阳（变爻）
    ↓
生成六爻 → 上下卦 → 64 卦
    ↓
变爻分析（如有）
    ↓
LLM 增强解读
```

### 3. 塔罗占卜系统

**抽牌 + 牌阵解读**

```python
# 抽牌流程
session_id（随机种子）
    ↓
选择牌阵
    ├─ single（单张）
    ├─ three（过去/现在/未来）
    └─ cross（十字牌阵）
    ↓
随机抽牌（不重复）
    ├─ 50% 概率逆位
    └─ 获取牌面含义
    ↓
LLM 深度解读
```

---

## 数据模型

### 核心表结构

```sql
-- 用户表
users (id, username, email, password_hash, role, created_at)

-- 用户档案
user_profiles (
    user_id, birth_date, lunar_birth_date,
    animal, zodiac_sign, ganzhi_year, created_at
)

-- 每日运势
daily_fortunes (
    id, user_id, fortune_date,
    overall_score, wealth_score, career_score, love_score, health_score,
    content, lucky_color, lucky_number, lucky_direction, lucky_time,
    yi, ji, solar_term, festival, created_at
)

-- 占卜会话
divination_sessions (
    id, user_id, version, question, event_type,
    intent, status, result_summary, result_detail, result_data,
    created_at, updated_at
)

-- LLM 配置
llm_configs (
    id, name, provider, endpoint, api_key, model_name,
    is_enabled, is_default, extra_config, created_at
)

-- Prompt 配置
prompt_configs (
    id, name, scene, prompt_type, template,
    llm_config_id, temperature, max_tokens, timeout_seconds,
    is_enabled, created_at
)
```

---

## 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 端口：40080, 40081, 48080, 45432

### 2. 启动服务

```bash
cd /mnt/DivineDaily
./restart.sh
```

### 3. 访问应用

- 📱 移动端：http://localhost:40080
- 🔧 管理后台：http://localhost:40081
- 🚀 后端 API：http://localhost:48080
- 📚 API 文档：http://localhost:48080/docs

### 4. 默认账号

- 用户名：`admin`
- 密码：`594120`

---

## 项目结构

```
DivineDaily/
├── backend-python/          # Python FastAPI 后端
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── repositories/   # 数据访问
│   │   └── utils/          # 工具函数
│   ├── alembic/            # 数据库迁移
│   └── requirements.txt
├── web/                     # 移动端前端
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── components/    # React 组件
│   │   ├── pages/         # 页面
│   │   └── services/      # 前端服务
│   └── package.json
├── web-admin/              # 管理后台
├── docker/                 # Docker 配置
│   ├── docker-compose.yaml
│   └── deploy.sh
├── PROJECT.md             # 本文件
├── DEVELOPMENT.md         # 开发指南
└── API.md                 # API 参考
```

---

## 核心算法

### 五行生克评分

```python
def calculate_wuxing_score(user_wuxing: str, day_wuxing: str) -> int:
    """
    相生: 90分 - 日生我，得到助力
    生: 85分 - 我生日，消耗能量
    比和: 70分 - 同类，平稳
    克: 45分 - 我克日，需要努力
    被克: 40分 - 日克我，有压力
    """
```

### 生肖相冲相合评分

```python
def calculate_animal_score(user_animal: str, day_animal: str) -> int:
    """
    相合: +20分
    相冲: -20分
    同生肖: +10分
    其他: 0分
    """
```

### 节气加成

```python
SOLAR_TERM_BONUS = {
    "立春": 15, "立夏": 15, "立秋": 15, "立冬": 15,
    "春分": 10, "夏至": 10, "秋分": 10, "冬至": 10,
    "清明": -5, "寒食": -5
}
```

---

## 配置管理

### LLM 配置

支持多种 LLM 提供商：
- OpenAI
- DeepSeek
- Doubao (字节跳动)
- 其他 OpenAI 兼容接口

### Prompt 配置

支持场景化 Prompt 管理：
- `daily_fortune` - 每日运势
- `divination` - 周易占卜
- `tarot` - 塔罗占卜

**变量替换**：
```python
template = "用户生肖：{user_animal}，今日评分：{overall_score}"
# 自动替换为实际值
```

---

## 降级策略

### LLM 失败降级

```python
try:
    # 尝试调用 LLM
    result = await llm_service.generate(prompt)
except Exception:
    # 降级到算法结果
    result = generate_default_content(algorithm_data)
```

### 算法 + LLM 双引擎

- **算法**：保证基础准确性和一致性
- **LLM**：提升可读性和个性化
- **降级**：LLM 失败时仍有完整功能

---

## 性能优化

### 缓存策略

- 每日运势：按用户 + 日期缓存
- 占卜结果：按 session_id 缓存
- 用户档案：内存缓存

### 数据库优化

- 索引：user_id, fortune_date, session_id
- 分页查询：limit + offset
- 异步查询：SQLAlchemy async

---

## 安全建议

### 生产环境必须修改

1. **JWT 密钥**
```bash
JWT_SECRET=your-strong-secret-key-change-in-production
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

## 常见问题

### 1. 端口被占用

修改 `docker/docker-compose.yaml` 中的端口映射

### 2. 数据库连接失败

```bash
# 检查容器状态
docker-compose ps

# 查看数据库日志
docker-compose logs postgres
```

### 3. LLM 调用失败

- 检查 API Key 是否有效
- 检查网络连接
- 查看后端日志

### 4. 前端无法连接后端

- 检查 `VITE_API_PROXY_TARGET` 配置
- 确认后端服务已启动

---

## 更新日志

### 2026-02-22
- ✅ 整理项目文档
- ✅ 精简文档结构

### 2026-02-21
- ✅ 完成每日运势 Assistant 配置
- ✅ 集成传统算法

### 2026-02-20
- ✅ 实现传统算法服务
- ✅ 完成数据库迁移

### 2026-02-13
- ✅ 完成前端项目拆分
- ✅ 配置 Docker Compose

---

## 许可证

MIT License

---

**Divine Daily - 让占卜更智能** 🔮✨


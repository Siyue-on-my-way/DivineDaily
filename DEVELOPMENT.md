# DivineDaily - 开发指南

## 开发环境搭建

### 1. 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose（可选）

### 2. 本地开发（不使用 Docker）

#### 后端开发

```bash
cd backend-python

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL="postgresql://user:pass@localhost:5432/divinedaily"
export JWT_SECRET="your-secret-key"

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8080
```

#### 前端开发

```bash
cd web

# 安装依赖
npm install

# 配置环境变量（创建 .env.local）
echo "VITE_API_BASE_URL=http://localhost:8080" > .env.local

# 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

#### 管理后台开发

```bash
cd web-admin

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:5174
```

### 3. Docker 开发

```bash
cd docker

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend-python

# 重启服务
docker-compose restart backend-python

# 停止服务
docker-compose down
```

---

## 项目结构详解

### 后端结构

```
backend-python/
├── app/
│   ├── api/v1/              # API 路由
│   │   ├── auth.py          # 认证接口
│   │   ├── divination.py    # 占卜接口
│   │   ├── daily_fortune.py # 每日运势接口
│   │   └── user_profile.py  # 用户档案接口
│   ├── core/                # 核心配置
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── security.py      # 安全工具
│   │   └── exceptions.py    # 异常定义
│   ├── models/              # 数据模型
│   │   ├── user.py
│   │   ├── divination.py
│   │   └── daily_fortune.py
│   ├── repositories/        # 数据访问层
│   │   ├── user_repository.py
│   │   └── divination_repository.py
│   ├── services/            # 业务逻辑层
│   │   ├── auth_service.py
│   │   ├── divination_service.py
│   │   ├── enhanced_divination_service.py
│   │   ├── daily_fortune_service.py
│   │   ├── fortune_algorithm_service.py
│   │   ├── iching_service.py
│   │   ├── tarot_service.py
│   │   ├── llm_service.py
│   │   └── time_convert_service.py
│   ├── schemas/             # Pydantic 模型
│   ├── utils/               # 工具函数
│   │   ├── calendar.py      # 农历转换
│   │   ├── hexagram_data.py # 卦象数据
│   │   └── tarot_data.py    # 塔罗数据
│   └── main.py              # 应用入口
├── alembic/                 # 数据库迁移
│   └── versions/
├── requirements.txt         # 依赖列表
└── Dockerfile
```

### 前端结构

```
web/src/
├── api/                     # API 调用
│   ├── auth.ts
│   ├── divination.ts
│   └── fortune.ts
├── components/              # React 组件
│   ├── mobile/             # 移动端组件
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Input.tsx
│   ├── divination/         # 占卜组件
│   │   ├── DivinationResultCard.tsx
│   │   ├── DailyFortuneDisplay.tsx
│   │   └── RitualFlow.tsx
│   └── tarot/              # 塔罗组件
├── pages/                   # 页面
│   ├── HomePage.tsx
│   ├── DivinationPage.tsx
│   ├── TarotPage.tsx
│   ├── HistoryPage.tsx
│   └── ProfilePage.tsx
├── hooks/                   # 自定义 Hooks
├── lib/                     # 工具库
│   ├── AuthContext.tsx
│   └── axios.ts
├── styles/                  # 样式
└── types/                   # TypeScript 类型
```

---

## 核心服务开发

### 1. 创建新的占卜服务

```python
# backend-python/app/services/my_divination_service.py

class MyDivinationService:
    """自定义占卜服务"""
    
    def __init__(self):
        pass
    
    async def generate_result(self, session_id: str, question: str) -> Dict[str, Any]:
        """生成占卜结果"""
        # 1. 算法计算
        algorithm_result = self._calculate(session_id)
        
        # 2. LLM 增强（可选）
        if llm_service:
            enhanced = await self._enhance_with_llm(question, algorithm_result)
        
        # 3. 返回结果
        return {
            'session_id': session_id,
            'summary': '...',
            'detail': '...',
        }
```

### 2. 添加新的 API 端点

```python
# backend-python/app/api/v1/my_api.py

from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(
    request: MyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """自定义端点"""
    service = MyService(db)
    result = await service.process(request)
    return result
```

### 3. 创建数据库迁移

```bash
cd backend-python

# 创建迁移文件
alembic revision -m "add_my_table"

# 编辑迁移文件
# alembic/versions/xxx_add_my_table.py

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 4. 添加前端页面

```typescript
// web/src/pages/MyPage.tsx

import { useState, useEffect } from 'react';
import { MobilePage } from '../components/mobile/MobileLayout';
import { Card } from '../components/mobile/Card';

export default function MyPage() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    // API 调用
  };
  
  return (
    <MobilePage>
      <Card>
        {/* 内容 */}
      </Card>
    </MobilePage>
  );
}
```

---

## 算法开发

### 1. 五行算法示例

```python
# backend-python/app/services/wuxing_service.py

class WuxingService:
    """五行算法服务"""
    
    WUXING_RELATIONSHIPS = {
        "木": {"火": "生", "土": "克", "金": "被克", "水": "被生", "木": "比和"},
        "火": {"土": "生", "金": "克", "水": "被克", "木": "被生", "火": "比和"},
        "土": {"金": "生", "水": "克", "木": "被克", "火": "被生", "土": "比和"},
        "金": {"水": "生", "木": "克", "火": "被克", "土": "被生", "金": "比和"},
        "水": {"木": "生", "火": "克", "土": "被克", "金": "被生", "水": "比和"},
    }
    
    @staticmethod
    def calculate_score(user_wuxing: str, day_wuxing: str) -> int:
        """计算五行评分"""
        relationship = WuxingService.WUXING_RELATIONSHIPS[user_wuxing][day_wuxing]
        
        score_map = {
            "被生": 90,  # 日生我，得到助力
            "生": 85,    # 我生日，消耗能量
            "比和": 70,  # 同类，平稳
            "克": 45,    # 我克日，需要努力
            "被克": 40,  # 日克我，有压力
        }
        
        return score_map.get(relationship, 60)
```

### 2. 生肖算法示例

```python
# backend-python/app/services/animal_service.py

class AnimalService:
    """生肖算法服务"""
    
    ANIMAL_CONFLICT = {
        "鼠": "马", "牛": "羊", "虎": "猴", "兔": "鸡",
        "龙": "狗", "蛇": "猪", "马": "鼠", "羊": "牛",
        "猴": "虎", "鸡": "兔", "狗": "龙", "猪": "蛇"
    }
    
    ANIMAL_HARMONY = {
        "鼠": ["龙", "猴"], "牛": ["蛇", "鸡"],
        "虎": ["马", "狗"], "兔": ["羊", "猪"],
        "龙": ["鼠", "猴"], "蛇": ["牛", "鸡"],
        "马": ["虎", "狗"], "羊": ["兔", "猪"],
        "猴": ["鼠", "龙"], "鸡": ["牛", "蛇"],
        "狗": ["虎", "马"], "猪": ["兔", "羊"]
    }
    
    @staticmethod
    def calculate_score(user_animal: str, day_animal: str) -> int:
        """计算生肖评分"""
        if user_animal == day_animal:
            return 10  # 同生肖
        
        if AnimalService.ANIMAL_CONFLICT.get(user_animal) == day_animal:
            return -20  # 相冲
        
        if day_animal in AnimalService.ANIMAL_HARMONY.get(user_animal, []):
            return 20  # 相合
        
        return 0  # 其他
```

---

## LLM 集成

### 1. 配置 LLM

```python
# 在管理后台或数据库中配置

llm_config = {
    "name": "DeepSeek",
    "provider": "deepseek",
    "endpoint": "https://api.deepseek.com/v1/chat/completions",
    "api_key": "your-api-key",
    "model_name": "deepseek-chat",
    "is_enabled": True,
    "is_default": True,
    "extra_config": {
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 30
    }
}
```

### 2. 创建 Prompt 配置

```python
prompt_config = {
    "name": "每日运势解读",
    "scene": "daily_fortune",
    "prompt_type": "answer",
    "template": """
你是一位精通命理的大师。请根据以下信息生成运势解读：

【用户信息】
- 生肖：{user_animal}
- 五行：{user_wuxing}

【算法结果】
- 综合评分：{overall_score}分
- 财运评分：{wealth_score}分

请生成温暖、积极的运势解读。
""",
    "llm_config_id": 1,
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout_seconds": 30
}
```

### 3. 调用 LLM

```python
from app.services.llm_service import create_llm_service

# 创建 LLM 服务
llm_service = create_llm_service(llm_config)

# 构建 Prompt
prompt = template.format(
    user_animal="龙",
    user_wuxing="金",
    overall_score=85,
    wealth_score=75
)

# 调用 LLM
try:
    response = await llm_service.generate(prompt)
    print(response)
finally:
    await llm_service.close()
```

---

## 测试

### 1. 单元测试

```python
# backend-python/tests/test_fortune_algorithm.py

import pytest
from app.services.fortune_algorithm_service import FortuneAlgorithmService

def test_wuxing_score():
    """测试五行评分"""
    score = FortuneAlgorithmService.calculate_wuxing_score("木", "火")
    assert 80 <= score <= 100  # 相生，高分

def test_animal_score():
    """测试生肖评分"""
    score = FortuneAlgorithmService.calculate_animal_score("鼠", "马")
    assert score == -20  # 相冲
```

### 2. API 测试

```bash
# 登录
curl -X POST 'http://localhost:8080/api/v1/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"594120"}'

# 获取每日运势
curl -X POST 'http://localhost:8080/api/v1/daily_fortune' \
  -H 'Authorization: Bearer <token>'

# 开始占卜
curl -X POST 'http://localhost:8080/api/v1/divinations/start' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"question":"今天运势如何？","version":"CN"}'
```

### 3. 前端测试

```bash
cd web

# 运行测试
npm test

# 运行 E2E 测试
npm run test:e2e
```

---

## 调试技巧

### 1. 后端调试

```python
# 添加调试日志
import logging
logger = logging.getLogger(__name__)

logger.debug(f"用户ID: {user_id}")
logger.info(f"生成运势: {fortune_date}")
logger.warning(f"LLM 调用失败，使用降级方案")
logger.error(f"错误: {e}")
```

### 2. 前端调试

```typescript
// 使用 console
console.log('数据:', data);
console.error('错误:', error);

// 使用 React DevTools
// 安装浏览器扩展查看组件状态
```

### 3. 数据库调试

```bash
# 进入数据库容器
docker-compose exec postgres psql -U divinedaily

# 查询数据
SELECT * FROM daily_fortunes WHERE user_id = 1;

# 查看表结构
\d daily_fortunes

# 查看索引
\di
```

---

## 性能优化

### 1. 数据库优化

```python
# 使用索引
CREATE INDEX idx_user_date ON daily_fortunes(user_id, fortune_date);

# 使用异步查询
result = await db.execute(select(User).where(User.id == user_id))

# 批量查询
users = await db.execute(select(User).where(User.id.in_(user_ids)))
```

### 2. 缓存优化

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_hexagram_data(hexagram_number: int):
    """缓存卦象数据"""
    return HEXAGRAMS[hexagram_number]
```

### 3. 前端优化

```typescript
// 使用 React.memo
const MyComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
});

// 使用 useMemo
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// 使用 useCallback
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);
```

---

## 代码规范

### Python 代码规范

```python
# 使用 Black 格式化
black backend-python/

# 使用 isort 排序导入
isort backend-python/

# 使用 flake8 检查
flake8 backend-python/

# 使用 mypy 类型检查
mypy backend-python/
```

### TypeScript 代码规范

```bash
# 使用 ESLint
npm run lint

# 使用 Prettier 格式化
npm run format

# 类型检查
npm run type-check
```

---

## 常见问题

### 1. 数据库迁移失败

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 强制标记为已迁移
alembic stamp head
```

### 2. LLM 调用超时

```python
# 增加超时时间
llm_service = create_llm_service(
    llm_config,
    timeout=60  # 60秒
)
```

### 3. 前端构建失败

```bash
# 清除缓存
rm -rf node_modules package-lock.json
npm install

# 清除 Vite 缓存
rm -rf .vite
```

---

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 联系方式

- 项目地址：[GitHub](https://github.com/your-repo/divinedaily)
- 问题反馈：[Issues](https://github.com/your-repo/divinedaily/issues)


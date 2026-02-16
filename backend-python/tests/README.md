# DivineDaily 测试套件

完整的端到端测试套件，用于验证 DivineDaily 项目的所有功能。

---

## 📋 测试套件说明

### 1. `need_test_case.py` - 基础功能测试
**用途**: 服务重启后的快速验证测试

**测试内容**:
- ✅ 用户登录
- ✅ LLM 配置列表
- ✅ Assistant 配置列表
- ✅ LLM 测试接口
- ✅ Assistant 测试用例
- ✅ Assistant 测试接口
- ✅ 占卜开始接口

**运行时间**: ~30秒

---

### 2. `comprehensive_test.py` - 用户端完整测试
**用途**: 完整的用户端业务流程测试

**测试内容**:
- ✅ 用户注册与登录
- ✅ 用户档案管理（创建、获取）
- ✅ 周易占卜（决策类、运势类）
- ✅ 塔罗占卜（单张、三张、十字牌阵）
- ✅ 每日运势生成
- ✅ 历史记录查询

**运行时间**: ~2-3分钟

---

### 3. `admin_test.py` - 管理端完整测试
**用途**: 管理员配置管理功能测试

**测试内容**:
- ✅ 管理员登录
- ✅ LLM 配置管理（增删改查、测试）
- ✅ Assistant 配置管理（增删改查、测试）
- ✅ 测试用例管理

**运行时间**: ~1-2分钟

---

### 4. `run_all_tests.py` - 完整测试运行器
**用途**: 运行所有测试套件并生成报告

**功能**:
- 依次运行所有测试套件
- 生成详细的测试报告
- 保存报告到文件

**运行时间**: ~4-6分钟

---

## 🚀 快速开始

### 安装依赖
```bash
pip install requests pytest pytest-asyncio httpx
```

### 运行单个测试套件

#### 基础功能测试
```bash
cd /mnt/DivineDaily/backend-python/tests
python need_test_case.py
```

#### 用户端完整测试
```bash
python comprehensive_test.py
```

#### 管理端完整测试
```bash
python admin_test.py
```

### 运行所有测试
```bash
python run_all_tests.py
```

---

## 📊 测试报告

运行 `run_all_tests.py` 后会生成测试报告文件：
```
test_report_20260216_153045.txt
```

报告内容包括：
- 测试时间
- 总测试套件数
- 通过/失败数量
- 通过率
- 每个测试套件的详细输出

---

## 🔧 配置说明

### 测试环境配置

在每个测试文件中修改以下配置：

```python
# 后端API地址
BASE_URL = "http://8.148.26.166:48080"
API_BASE = f"{BASE_URL}/api/v1"

# 管理员账号
ADMIN_USERNAME = "admin@163.com"
ADMIN_PASSWORD = "594120"
```

### 测试用户

`comprehensive_test.py` 会自动创建测试用户，使用时间戳确保唯一性：
```python
TEST_USER_EMAIL = f"test_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "test123456"
```

---

## 📝 测试用例详解

### 用户端测试流程

```
1. 用户注册
   ↓
2. 用户登录
   ↓
3. 创建用户档案（姓名、性别、生日）
   ↓
4. 周易占卜 - 决策类问题
   ↓
5. 周易占卜 - 运势类问题
   ↓
6. 塔罗占卜 - 单张牌
   ↓
7. 塔罗占卜 - 三张牌阵
   ↓
8. 塔罗占卜 - 十字牌阵
   ↓
9. 每日运势生成
   ↓
10. 查看占卜历史
```

### 管理端测试流程

```
1. 管理员登录
   ↓
2. 获取LLM配置列表
   ↓
3. 创建新的LLM配置
   ↓
4. 更新LLM配置
   ↓
5. 测试LLM配置
   ↓
6. 删除LLM配置
   ↓
7. 获取Assistant配置列表
   ↓
8. 创建新的Assistant配置
   ↓
9. 更新Assistant配置
   ↓
10. 测试Assistant配置
   ↓
11. 删除Assistant配置
```

---

## 🎯 测试覆盖范围

### API 端点覆盖

#### 认证相关 (5个)
- ✅ POST /api/v1/auth/register
- ✅ POST /api/v1/auth/login
- ✅ GET /api/v1/auth/me
- ✅ POST /api/v1/auth/refresh
- ✅ POST /api/v1/auth/logout

#### 用户档案 (4个)
- ✅ POST /api/v1/profile
- ✅ GET /api/v1/profile
- ✅ PUT /api/v1/profile
- ✅ DELETE /api/v1/profile

#### 占卜相关 (3个)
- ✅ POST /api/v1/divinations/start
- ✅ GET /api/v1/divinations/{session_id}
- ✅ GET /api/v1/divinations

#### 每日运势 (1个)
- ✅ POST /api/v1/daily_fortune

#### LLM配置 (6个)
- ✅ GET /api/v1/configs/llm
- ✅ POST /api/v1/configs/llm
- ✅ PUT /api/v1/configs/llm/{id}
- ✅ DELETE /api/v1/configs/llm/{id}
- ✅ POST /api/v1/configs/llm/{id}/set-default
- ✅ POST /api/v1/configs/llm/{id}/test

#### Assistant配置 (6个)
- ✅ GET /api/v1/configs/assistant
- ✅ POST /api/v1/configs/assistant
- ✅ PUT /api/v1/configs/assistant/{id}
- ✅ DELETE /api/v1/configs/assistant/{id}
- ✅ GET /api/v1/configs/assistant/test-cases
- ✅ POST /api/v1/configs/assistant/{id}/test

**总计**: 25个API端点

---

## 🔍 测试验证点

### 数据验证
- ✅ 状态码验证
- ✅ 响应字段完整性验证
- ✅ 数据格式验证
- ✅ 业务逻辑验证

### 业务逻辑验证
- ✅ 意图识别准确性
- ✅ 卦象生成正确性
- ✅ 塔罗牌数量正确性
- ✅ 运势数据完整性
- ✅ LLM调用成功性
- ✅ 权限控制正确性

### 错误处理验证
- ✅ 未授权访问拒绝
- ✅ 无效参数拒绝
- ✅ 资源不存在处理
- ✅ 超时处理

---

## 📈 性能指标

### 响应时间要求
- 登录: < 1秒
- 占卜: < 30秒
- LLM调用: < 20秒
- 列表查询: < 2秒

### 成功率要求
- 所有测试通过率: 100%
- 单个测试套件通过率: 100%

---

## 🛠️ 故障排查

### 常见问题

#### 1. 连接失败
```
❌ 请求失败: Connection refused
```
**解决方案**: 检查后端服务是否启动，确认 BASE_URL 配置正确

#### 2. 认证失败
```
❌ 登录测试失败: 401
```
**解决方案**: 检查管理员账号密码是否正确

#### 3. 超时
```
❌ 请求超时: POST /divinations/start
```
**解决方案**: 
- 检查LLM服务是否正常
- 增加timeout参数
- 检查网络连接

#### 4. LLM测试失败
```
❌ LLM测试失败: HTTP 401
```
**解决方案**: 检查LLM配置的API Key是否有效

---

## 📅 使用场景

### 场景1: 代码修改后验证
```bash
# 快速验证核心功能
python need_test_case.py

# 如果通过，运行完整测试
python run_all_tests.py
```

### 场景2: 部署前验证
```bash
# 运行所有测试并生成报告
python run_all_tests.py

# 检查报告，确保100%通过
cat test_report_*.txt
```

### 场景3: 定期回归测试
```bash
# 设置定时任务，每天运行
0 2 * * * cd /mnt/DivineDaily/backend-python/tests && python run_all_tests.py
```

### 场景4: 调试特定功能
```bash
# 只运行用户端测试
python comprehensive_test.py

# 只运行管理端测试
python admin_test.py
```

---

## 🔄 持续集成

### GitHub Actions 示例

```yaml
name: DivineDaily Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend-python/tests
          python run_all_tests.py
```

---

## 📞 支持

如有问题，请查看：
- 测试计划文档: `/mnt/DivineDaily/a-docs/plan/COMPREHENSIVE_TEST_PLAN.md`
- API 文档: http://8.148.26.166:48080/docs
- 项目文档: `/mnt/DivineDaily/a-docs/`

---

**维护者**: DivineDaily Team  
**最后更新**: 2026-02-16


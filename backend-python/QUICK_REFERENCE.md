# 🚀 改造快速参考指南

## 📁 文件清单

### 新增文件
```
app/services/
├── question_analyzer.py          # 智能问题分析器（350行）
├── divination_router.py          # 智能路由器（200行）
└── enhanced_divination_service.py # 增强占卜服务（250行）

tests/
├── test_standalone.py            # 独立测试脚本（200行）
└── test_phase1_phase2.py         # 完整测试（备用）

docs/
├── MIGRATION_PROGRESS.md         # 详细进度报告
└── PHASE1_PHASE2_SUMMARY.md      # 完成总结
```

---

## 🎯 核心API

### QuestionAnalyzer

```python
from app.services.question_analyzer import QuestionAnalyzer

# 创建分析器
analyzer = QuestionAnalyzer(llm_service=None)

# 分析问题
analysis = await analyzer.analyze_question("我应该跳槽还是留下？")

# 访问结果
print(analysis.question_type)  # "career"
print(analysis.sub_type)        # "binary_choice"
print(analysis.elements)        # {"option_a": "跳槽", "option_b": "留下"}
print(analysis.complexity)      # "medium"
```

### DivinationRouter

```python
from app.services.divination_router import DivinationRouter

# 创建路由器
router = DivinationRouter(db)

# 路由问题
result = await router.route_question(
    session_id="xxx",
    question="今天运势如何？",
    user_id="user123",
    analysis=analysis,
    divination_service=divination_svc,
    daily_fortune_service=fortune_svc
)
```

### EnhancedDivinationService

```python
from app.services.enhanced_divination_service import EnhancedDivinationService

# 创建服务
service = EnhancedDivinationService(db, llm_service)
service.set_daily_fortune_service(fortune_service)

# 开始占卜
result = await service.start_divination_with_enhancement(request)
```

---

## 🧪 测试命令

```bash
# 运行独立测试
cd /mnt/DivineDaily/backend-python
python3 tests/test_standalone.py

# 查看进度报告
cat MIGRATION_PROGRESS.md

# 查看完成总结
cat PHASE1_PHASE2_SUMMARY.md
```

---

## 📊 功能速查

### 问题类型识别

| 关键词 | 识别类型 | 示例 |
|--------|---------|------|
| 还是、或者 | binary_choice | "A还是B？" |
| 恋爱、感情 | relationship | "我喜欢他" |
| 工作、跳槽 | career | "要不要跳槽" |
| 运势、今日 | fortune | "今天运势" |
| 是什么、含义 | knowledge | "什么是易经" |

### 复杂度评分

| 因素 | 分值 | 说明 |
|------|------|------|
| 关联词（但是/不过） | +1 | 有冲突 |
| 关联词（又/也） | +1 | 多维度 |
| 长度>50字 | +1 | 信息丰富 |
| 长度>100字 | +1 | 非常详细 |
| 关键词≥3个 | +1 | 多方面 |
| 时间因素 | +0.5 | 有时效性 |

**评级**:
- score ≥ 3: high
- score ≥ 1.5: medium
- score < 1.5: simple

### 路由规则

```
问题类型 → 处理策略
─────────────────────
fortune   → 每日运势服务
knowledge → 知识解读（卦象+解释）
其他      → 决策占卜（周易卦象）
```

---

## 🔧 配置说明

### 依赖注入

```python
# 在main.py中配置
enhanced_service = EnhancedDivinationService(db, llm_service)
enhanced_service.set_daily_fortune_service(daily_fortune_service)
```

### 可选配置

```python
# 使用LLM分析（推荐）
analyzer = QuestionAnalyzer(llm_service=llm_service)

# 仅使用规则引擎（降级）
analyzer = QuestionAnalyzer(llm_service=None)
```

---

## 🐛 故障排查

### 问题1: 要素提取失败

**症状**: elements为空  
**原因**: 问题格式不标准  
**解决**: 检查是否包含"还是"、"但是"等关键词

### 问题2: 路由失败

**症状**: 返回基础占卜结果  
**原因**: 路由器异常  
**解决**: 查看日志，检查服务注入

### 问题3: 复杂度评估不准

**症状**: 复杂问题被评为simple  
**原因**: 评分因素不足  
**解决**: 调整评分阈值或添加更多因素

---

## 📝 代码示例

### 示例1: 完整占卜流程

```python
from app.services.enhanced_divination_service import EnhancedDivinationService
from app.schemas.divination import CreateDivinationRequest

# 创建请求
request = CreateDivinationRequest(
    user_id="user123",
    version="CN",
    question="我应该和研究生学妹谈恋爱还是和大一学妹谈？",
    event_type="relationship"
)

# 执行占卜
service = EnhancedDivinationService(db, llm_service)
result = await service.start_divination_with_enhancement(request)

# 查看结果
print(f"问题类型: {result.question_type}")
print(f"问题意图: {result.question_intent}")
print(f"摘要: {result.summary}")
```

### 示例2: 单独使用分析器

```python
from app.services.question_analyzer import QuestionAnalyzer

analyzer = QuestionAnalyzer()
analysis = analyzer._fallback_analysis("今天运势如何？")

print(f"类型: {analysis.question_type}")  # "fortune"
print(f"复杂度: {analysis.complexity}")    # "simple"
```

### 示例3: 自定义路由

```python
from app.services.divination_router import DivinationRouter

class CustomRouter(DivinationRouter):
    async def _process_custom(self, ...):
        # 自定义处理逻辑
        pass
```

---

## 🎓 最佳实践

### 1. 问题分析
- ✅ 优先使用LLM分析
- ✅ 规则引擎作为降级
- ✅ 记录分析结果用于优化

### 2. 路由决策
- ✅ 明确的类型判断
- ✅ 完善的降级策略
- ✅ 详细的日志记录

### 3. 错误处理
- ✅ 捕获所有异常
- ✅ 提供降级方案
- ✅ 记录错误信息

### 4. 性能优化
- ✅ 缓存分析结果
- ✅ 异步处理
- ✅ 避免重复计算

---

## 📞 获取帮助

### 查看文档
```bash
# 详细进度
cat MIGRATION_PROGRESS.md

# 完成总结
cat PHASE1_PHASE2_SUMMARY.md

# 代码注释
grep -r "TODO\|FIXME" app/services/
```

### 运行测试
```bash
# 快速测试
python3 tests/test_standalone.py

# 查看测试覆盖
# (需要安装pytest-cov)
pytest tests/ --cov=app/services
```

### 调试技巧
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 打印分析结果
print(f"分析结果: {vars(analysis)}")

# 检查路由决策
print(f"路由到: {analysis.question_type}")
```

---

## 🔄 版本历史

### v0.2.0 (当前)
- ✅ Phase 1: 智能问题分析增强
- ✅ Phase 2: 智能决策路由系统

### v0.1.0 (基线)
- 基础占卜功能
- 简单意图识别
- LLM增强解读

---

**最后更新**: 2025年当前  
**维护者**: AI Assistant  
**许可证**: MIT


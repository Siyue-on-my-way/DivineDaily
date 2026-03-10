#!/usr/bin/env python3
"""
测试文本格式化功能
"""
import sys
sys.path.insert(0, '/mnt/DivineDaily/backend-python')

from app.utils.text_formatter import TextFormatter

formatter = TextFormatter()

# 测试数据
test_cases = [
    {
        "name": "简单文本",
        "input": "这是一个简单的测试文本。",
        "method": "add_paragraph_breaks"
    },
    {
        "name": "带标题的文本",
        "input": """## 工作运势

你最近的工作运势不错。

### 建议

- 保持积极态度
- 多与同事沟通""",
        "method": "clean_markdown"
    },
    {
        "name": "带列表的文本",
        "input": """工作运势分析：

1. 事业发展顺利
2. 人际关系和谐
3. 财运稳定上升

**建议**：保持现状，稳步前进。""",
        "method": "clean_markdown"
    },
    {
        "name": "需要格式化的纯文本",
        "input": "第一段内容。第二段内容。第三段内容。",
        "method": "add_paragraph_breaks"
    }
]

print("=" * 60)
print("文本格式化测试")
print("=" * 60)

for i, test in enumerate(test_cases, 1):
    print(f"\n测试 {i}: {test['name']}")
    print("-" * 60)
    
    method = getattr(formatter, test['method'])
    result = method(test['input'])
    
    print(f"输入文本:\n{test['input'][:100]}...")
    print(f"\n格式化后:\n{result[:200]}...")
    print(f"\n使用方法: {test['method']}")
    print(f"是否包含 Markdown 标记: {'是' if any(marker in result for marker in ['##', '**', '-', '1.']) else '否'}")
    print("✅ 通过" if result else "❌ 失败")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

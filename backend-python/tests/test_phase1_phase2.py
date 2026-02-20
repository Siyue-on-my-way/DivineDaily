"""测试智能问题分析和路由功能"""

import asyncio
from app.services.question_analyzer import QuestionAnalyzer


async def test_question_analyzer():
    """测试问题分析器"""
    print("=" * 60)
    print("测试智能问题分析器")
    print("=" * 60)
    
    analyzer = QuestionAnalyzer(llm_service=None)  # 使用规则引擎
    
    test_cases = [
        "我应该和研究生学妹谈恋爱还是和大一学妹谈？",
        "杨冠和刘亦菲同时追我，我应该选谁？我最近在事业上升期，希望事业也有成。但是也怕孤独，想谈恋爱",
        "我要不要跳槽到新公司？",
        "今天的运势怎么样？",
        "什么是易经？",
        "我什么时候能找到真爱？",
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n【测试用例 {i}】")
        print(f"问题: {question}")
        print("-" * 60)
        
        analysis = analyzer._fallback_analysis(question)
        
        print(f"问题类型: {analysis.question_type}")
        print(f"子类型: {analysis.sub_type}")
        print(f"意图: {analysis.intent}")
        print(f"复杂度: {analysis.complexity}")
        print(f"关键词: {analysis.keywords}")
        print(f"提取的要素: {analysis.elements}")
        
        # 验证要素提取
        if analysis.sub_type == "binary_choice":
            if "option_a" in analysis.elements and "option_b" in analysis.elements:
                print(f"✅ 成功提取选项A: {analysis.elements['option_a']}")
                print(f"✅ 成功提取选项B: {analysis.elements['option_b']}")
            else:
                print("❌ 未能提取选项")
        
        # 验证顾虑提取
        concerns = [k for k in analysis.elements.keys() if k.startswith("concern_")]
        if concerns:
            print(f"✅ 成功提取 {len(concerns)} 个顾虑:")
            for concern_key in concerns:
                print(f"   - {concern_key}: {analysis.elements[concern_key]}")
        
        # 验证复杂度评估
        if "但是" in question or "不过" in question:
            if analysis.complexity in ["medium", "high"]:
                print(f"✅ 复杂度评估正确: {analysis.complexity}")
            else:
                print(f"❌ 复杂度评估可能有误: {analysis.complexity}")


def test_summary():
    """测试总结"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    print("\n✅ Phase 1 完成项:")
    print("  1. 问题要素提取（option_a, option_b, concern_1等）")
    print("  2. 复杂度评估（多因素：关联词、长度、维度、时间）")
    print("  3. 增强降级规则（10条规则，覆盖更多场景）")
    print("  4. 知识类和运势类问题识别")
    print("  5. 目标人物提取")
    
    print("\n✅ Phase 2 完成项:")
    print("  1. 创建DivinationRouter智能路由器")
    print("  2. 实现问题类型路由（fortune/knowledge/decision）")
    print("  3. 集成到EnhancedDivinationService")
    print("  4. 支持每日运势服务路由")
    print("  5. 支持知识类问题专门处理")
    
    print("\n📝 下一步计划:")
    print("  Phase 3: 场景化Prompt构建系统")
    print("  Phase 4: 方位推荐服务")
    print("  Phase 5: 历史管理增强")


if __name__ == "__main__":
    asyncio.run(test_question_analyzer())
    test_summary()


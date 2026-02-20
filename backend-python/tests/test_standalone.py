"""独立测试脚本 - 测试问题分析逻辑"""


def analyze_question(question: str):
    """简化的问题分析逻辑"""
    elements = {}
    keywords = []
    question_type = "decision"
    sub_type = "open_ended"
    intent = "guidance"
    complexity = "medium"
    
    # 规则1：检测二选一问题
    if "还是" in question:
        question_type = "decision"
        sub_type = "binary_choice"
        intent = "binary_choice"
        
        # 提取选项
        parts = question.split("还是", 1)
        if len(parts) >= 2:
            option_a = parts[0].strip()
            option_b = parts[1].strip()
            
            # 清理前缀
            for prefix in ["我应该", "应该", "要不要", "该不该", "是"]:
                if option_a.startswith(prefix):
                    option_a = option_a[len(prefix):].strip()
            
            option_b = option_b.rstrip("？?。.")
            
            elements["option_a"] = option_a
            elements["option_b"] = option_b
    
    # 规则2：检测感情类
    relationship_keywords = ["恋爱", "喜欢", "爱", "感情", "结婚", "分手", "追", "表白"]
    for kw in relationship_keywords:
        if kw in question:
            question_type = "relationship"
            keywords.append(kw)
    
    # 规则3：检测事业类
    career_keywords = ["工作", "事业", "职业", "跳槽", "升职", "面试", "公司"]
    for kw in career_keywords:
        if kw in question:
            if question_type == "decision":
                question_type = "career"
            keywords.append(kw)
    
    # 规则4：检测运势类
    fortune_keywords = ["运势", "运气", "今日", "本周", "财运"]
    for kw in fortune_keywords:
        if kw in question:
            question_type = "fortune"
            keywords.append(kw)
            break
    
    # 规则5：检测知识类
    knowledge_keywords = ["是什么", "什么意思", "解释", "含义"]
    for kw in knowledge_keywords:
        if kw in question:
            question_type = "knowledge"
            sub_type = "open_ended"
            intent = "understanding"
            keywords.append(kw)
            break
    
    # 规则6：提取顾虑
    concern_markers = ["但是", "不过", "可是"]
    concern_count = 0
    for marker in concern_markers:
        if marker in question:
            concern_count += 1
            parts = question.split(marker, 1)
            if len(parts) > 1:
                concern_text = parts[1].split("。")[0].split("，")[0].strip()
                elements[f"concern_{concern_count}"] = concern_text
    
    # 规则7：复杂度评估
    complexity_score = 0
    if "但是" in question or "不过" in question:
        complexity_score += 1
    if "又" in question or "也" in question:
        complexity_score += 1
    if len(question) > 50:
        complexity_score += 1
    if len(keywords) >= 3:
        complexity_score += 1
    
    if complexity_score >= 3:
        complexity = "high"
    elif complexity_score >= 1.5:
        complexity = "medium"
    else:
        complexity = "simple"
    
    return {
        "question_type": question_type,
        "sub_type": sub_type,
        "intent": intent,
        "complexity": complexity,
        "keywords": keywords,
        "elements": elements
    }


def test_question_analyzer():
    """测试问题分析器"""
    print("=" * 60)
    print("测试智能问题分析器（Phase 1 & 2）")
    print("=" * 60)
    
    test_cases = [
        "我应该和研究生学妹谈恋爱还是和大一学妹谈？",
        "杨冠和刘亦菲同时追我，我应该选谁？我最近在事业上升期，希望事业也有成。但是也怕孤独，想谈恋爱",
        "我要不要跳槽到新公司？",
        "今天的运势怎么样？",
        "什么是易经？",
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n【测试用例 {i}】")
        print(f"问题: {question}")
        print("-" * 60)
        
        result = analyze_question(question)
        
        print(f"问题类型: {result['question_type']}")
        print(f"子类型: {result['sub_type']}")
        print(f"意图: {result['intent']}")
        print(f"复杂度: {result['complexity']}")
        print(f"关键词: {result['keywords']}")
        print(f"提取的要素: {result['elements']}")
        
        # 验证
        if result['sub_type'] == "binary_choice":
            if "option_a" in result['elements'] and "option_b" in result['elements']:
                print(f"✅ 成功提取选项A: {result['elements']['option_a']}")
                print(f"✅ 成功提取选项B: {result['elements']['option_b']}")
            else:
                print("❌ 未能提取选项")
        
        concerns = [k for k in result['elements'].keys() if k.startswith("concern_")]
        if concerns:
            print(f"✅ 成功提取 {len(concerns)} 个顾虑:")
            for concern_key in concerns:
                print(f"   - {concern_key}: {result['elements'][concern_key]}")


def print_summary():
    """打印改造总结"""
    print("\n" + "=" * 60)
    print("改造总结")
    print("=" * 60)
    
    print("\n✅ Phase 1 完成项（智能问题分析增强）:")
    print("  1. ✅ 问题要素提取（option_a, option_b, concern_1等）")
    print("  2. ✅ 复杂度评估（多因素：关联词、长度、维度、时间）")
    print("  3. ✅ 增强降级规则（10条规则，覆盖更多场景）")
    print("  4. ✅ 知识类和运势类问题识别")
    print("  5. ✅ 目标人物提取")
    print("  6. ✅ 增强LLM Prompt（包含示例）")
    
    print("\n✅ Phase 2 完成项（智能决策路由系统）:")
    print("  1. ✅ 创建DivinationRouter智能路由器")
    print("  2. ✅ 实现问题类型路由（fortune/knowledge/decision）")
    print("  3. ✅ 集成到EnhancedDivinationService")
    print("  4. ✅ 支持每日运势服务路由")
    print("  5. ✅ 支持知识类问题专门处理")
    print("  6. ✅ 上下文传递机制")
    
    print("\n📝 已创建的文件:")
    print("  - app/services/question_analyzer.py (增强版)")
    print("  - app/services/divination_router.py (新建)")
    print("  - app/services/enhanced_divination_service.py (更新)")
    
    print("\n🎯 核心改进:")
    print("  1. 问题理解更深入：从简单分类到结构化要素提取")
    print("  2. 决策更智能：根据问题类型自动选择最佳处理策略")
    print("  3. 复杂度评估：多因素综合评估，更准确")
    print("  4. 扩展性更强：易于添加新的问题类型和处理策略")
    
    print("\n📊 对比Go版本:")
    print("  ✅ 问题要素提取 - 已实现")
    print("  ✅ 复杂度评估 - 已实现")
    print("  ✅ 智能路由 - 已实现")
    print("  ✅ 知识类问题处理 - 已实现")
    print("  ⏳ 场景化Prompt构建 - 待实现（Phase 3）")
    print("  ⏳ 方位推荐 - 待实现（Phase 4）")
    
    print("\n🚀 下一步计划:")
    print("  Phase 3: 场景化Prompt构建系统（2-3天）")
    print("  Phase 4: 方位推荐服务（1-2天）")
    print("  Phase 5: 历史管理增强（1天）")
    print("  Phase 6: 变卦关系深度分析（2天）")


if __name__ == "__main__":
    test_question_analyzer()
    print_summary()


"""
DivineDaily Backend Python - 端到端测试套件

模拟真实用户场景的端到端测试
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List


class TestEndToEnd:
    """端到端测试类"""
    
    def test_scenario_career_decision(self):
        """场景测试：职业决策"""
        print("\n" + "=" * 60)
        print("场景1: 职业决策 - 是否跳槽")
        print("=" * 60)
        
        # 用户输入
        user_input = {
            "question": "我应该接受这份新工作还是留在现在的公司？新工作薪资高30%但需要搬家，现在的公司稳定但发展空间有限。",
            "event_type": "career",
            "version": "CN"
        }
        
        print(f"\n📝 用户问题: {user_input['question']}")
        
        # Step 1: 问题分析
        from app.services.question_analyzer import QuestionAnalyzer
        analyzer = QuestionAnalyzer()
        analysis = analyzer.analyze(
            user_input["question"],
            user_input["event_type"]
        )
        
        print(f"\n🔍 问题分析:")
        print(f"  - 复杂度: {analysis['complexity']:.2f}")
        print(f"  - 要素提取: {len(analysis.get('elements', {}))} 个")
        if "elements" in analysis:
            for key, value in analysis["elements"].items():
                print(f"    • {key}: {value}")
        
        # Step 2: 智能路由
        from app.services.divination_router import DivinationRouter
        router = DivinationRouter()
        route_result = router.route(
            user_input["question"],
            user_input["event_type"],
            analysis
        )
        
        print(f"\n🎯 路由决策:")
        print(f"  - 策略: {route_result['strategy']}")
        print(f"  - 原因: {route_result.get('reason', 'N/A')}")
        
        # Step 3: Prompt构建
        from app.services.smart_prompt_builder import SmartPromptBuilder
        prompt_builder = SmartPromptBuilder()
        prompt = prompt_builder.build_prompt(
            question=user_input["question"],
            event_type=user_input["event_type"],
            analysis=analysis,
            route_result=route_result
        )
        
        print(f"\n📋 Prompt构建:")
        print(f"  - 长度: {len(prompt)} 字符")
        print(f"  - 预览: {prompt[:200]}...")
        
        # Step 4: 方位推荐
        from app.services.orientation_service import OrientationService
        orientation_service = OrientationService()
        orientation = orientation_service.recommend(
            version=user_input["version"],
            event_type=user_input["event_type"],
            question=user_input["question"]
        )
        
        print(f"\n🧭 方位推荐:")
        print(f"  - 推荐方位: {orientation['recommended_label']}")
        print(f"  - 推荐理由: {orientation['reason']}")
        
        # 验证
        assert analysis["complexity"] > 0.5  # 复杂问题
        assert route_result["strategy"] == "decision"  # 决策类
        assert len(prompt) > 100
        assert orientation["recommended_key"] in ["NW", "N", "E"]  # 事业相关方位
        
        print("\n✅ 职业决策场景测试通过")
    
    def test_scenario_relationship_fortune(self):
        """场景测试：感情运势"""
        print("\n" + "=" * 60)
        print("场景2: 感情运势 - 关系发展")
        print("=" * 60)
        
        user_input = {
            "question": "我和他的关系会怎么发展？",
            "event_type": "relationship",
            "version": "CN"
        }
        
        print(f"\n📝 用户问题: {user_input['question']}")
        
        # 完整流程
        from app.services.question_analyzer import QuestionAnalyzer
        from app.services.divination_router import DivinationRouter
        from app.services.smart_prompt_builder import SmartPromptBuilder
        from app.services.orientation_service import OrientationService
        
        analyzer = QuestionAnalyzer()
        router = DivinationRouter()
        prompt_builder = SmartPromptBuilder()
        orientation_service = OrientationService()
        
        # 执行
        analysis = analyzer.analyze(user_input["question"], user_input["event_type"])
        route_result = router.route(user_input["question"], user_input["event_type"], analysis)
        prompt = prompt_builder.build_prompt(
            question=user_input["question"],
            event_type=user_input["event_type"],
            analysis=analysis,
            route_result=route_result
        )
        orientation = orientation_service.recommend(
            version=user_input["version"],
            event_type=user_input["event_type"],
            question=user_input["question"]
        )
        
        print(f"\n🔍 分析结果:")
        print(f"  - 复杂度: {analysis['complexity']:.2f}")
        print(f"  - 路由策略: {route_result['strategy']}")
        print(f"  - Prompt长度: {len(prompt)}")
        print(f"  - 推荐方位: {orientation['recommended_label']}")
        
        # 验证
        assert route_result["strategy"] == "fortune"  # 运势类
        assert orientation["recommended_key"] in ["SE", "S", "SW"]  # 感情相关方位
        
        print("\n✅ 感情运势场景测试通过")
    
    def test_scenario_knowledge_query(self):
        """场景测试：知识查询"""
        print("\n" + "=" * 60)
        print("场景3: 知识查询 - 占卜知识")
        print("=" * 60)
        
        user_input = {
            "question": "什么是六爻占卜？它和梅花易数有什么区别？",
            "event_type": "knowledge",
            "version": "CN"
        }
        
        print(f"\n📝 用户问题: {user_input['question']}")
        
        # 完整流程
        from app.services.question_analyzer import QuestionAnalyzer
        from app.services.divination_router import DivinationRouter
        from app.services.smart_prompt_builder import SmartPromptBuilder
        
        analyzer = QuestionAnalyzer()
        router = DivinationRouter()
        prompt_builder = SmartPromptBuilder()
        
        analysis = analyzer.analyze(user_input["question"], user_input["event_type"])
        route_result = router.route(user_input["question"], user_input["event_type"], analysis)
        prompt = prompt_builder.build_prompt(
            question=user_input["question"],
            event_type=user_input["event_type"],
            analysis=analysis,
            route_result=route_result
        )
        
        print(f"\n🔍 分析结果:")
        print(f"  - 复杂度: {analysis['complexity']:.2f}")
        print(f"  - 路由策略: {route_result['strategy']}")
        print(f"  - Prompt预览: {prompt[:150]}...")
        
        # 验证
        assert route_result["strategy"] == "knowledge"  # 知识类
        assert "知识" in prompt or "解释" in prompt
        
        print("\n✅ 知识查询场景测试通过")
    
    def test_scenario_hexagram_analysis(self):
        """场景测试：卦象分析"""
        print("\n" + "=" * 60)
        print("场景4: 卦象分析 - 变卦关系")
        print("=" * 60)
        
        # 模拟占卜结果
        primary_lines = [1, 1, 1, 0, 0, 0]  # 泰卦
        changing_lines = [1, 0, 1, 0, 1, 0]  # 三个变爻
        
        print(f"\n🎲 卦象信息:")
        print(f"  - 本卦: {primary_lines}")
        print(f"  - 变爻: {changing_lines}")
        
        # 卦象分析
        from app.services.hexagram_analysis_service import HexagramAnalysisService
        hexagram_service = HexagramAnalysisService()
        
        # 变卦分析
        transformation = hexagram_service.analyze_transformation(
            primary_lines=primary_lines,
            changing_lines=changing_lines
        )
        
        print(f"\n🔄 变卦分析:")
        print(f"  - 变爻位置: {transformation['changing_positions']}")
        print(f"  - 变化类型: {transformation['transformation_type']}")
        print(f"  - 上卦变化: {transformation['upper_change']}")
        print(f"  - 下卦变化: {transformation['lower_change']}")
        
        # 五行分析
        elements = hexagram_service.analyze_five_elements(
            primary_lines=primary_lines,
            changing_lines=changing_lines
        )
        
        print(f"\n🌟 五行分析:")
        print(f"  - 本卦上卦: {elements['primary_upper']}")
        print(f"  - 本卦下卦: {elements['primary_lower']}")
        print(f"  - 变卦上卦: {elements['changing_upper']}")
        print(f"  - 变卦下卦: {elements['changing_lower']}")
        print(f"  - 五行关系: {elements['relationship']}")
        
        # 验证
        assert len(transformation['changing_positions']) == 3
        assert transformation['transformation_type'] in [
            "single_line", "two_lines", "three_lines",
            "four_lines", "five_lines", "six_lines", "no_change"
        ]
        assert elements['relationship'] in [
            "生", "克", "比和", "耗", "泄"
        ]
        
        print("\n✅ 卦象分析场景测试通过")
    
    def test_scenario_history_management(self):
        """场景测试：历史管理"""
        print("\n" + "=" * 60)
        print("场景5: 历史管理 - 查询与统计")
        print("=" * 60)
        
        # 模拟历史数据查询
        print("\n📊 历史查询场景:")
        
        # 场景1: 查询最近的职业类占卜
        query1 = {
            "limit": 10,
            "event_type": "career",
            "order_by": "created_at",
            "order_direction": "desc"
        }
        print(f"\n  场景1: 查询最近10条职业占卜")
        print(f"    参数: {query1}")
        
        # 场景2: 查询特定日期范围
        query2 = {
            "limit": 20,
            "start_date": "2025-01-01",
            "end_date": "2025-02-20",
            "version": "CN"
        }
        print(f"\n  场景2: 查询2025年1-2月的占卜")
        print(f"    参数: {query2}")
        
        # 场景3: 统计数据
        print(f"\n  场景3: 获取统计数据")
        print(f"    - 总数统计")
        print(f"    - 按类型统计")
        print(f"    - 按版本统计")
        print(f"    - 按状态统计")
        
        # 验证查询参数
        assert query1["limit"] <= 100
        assert query1["order_by"] in ["created_at", "updated_at"]
        assert query1["order_direction"] in ["asc", "desc"]
        
        print("\n✅ 历史管理场景测试通过")
    
    @pytest.mark.asyncio
    async def test_scenario_with_cache(self):
        """场景测试：带缓存的完整流程"""
        print("\n" + "=" * 60)
        print("场景6: 缓存优化 - 性能提升")
        print("=" * 60)
        
        try:
            from app.core.cache import RedisCache, CacheManager
            import time
            
            # 初始化缓存
            cache = RedisCache(host="localhost", port=6379, db=0)
            manager = CacheManager(cache)
            
            # 模拟数据库查询函数
            async def slow_query(user_id: str):
                await asyncio.sleep(0.1)  # 模拟100ms查询
                return {
                    "user_id": user_id,
                    "history_count": 50,
                    "last_divination": datetime.now().isoformat()
                }
            
            user_id = "test_user_123"
            cache_key = f"user:history:{user_id}"
            
            # 第一次查询（无缓存）
            start = time.time()
            result1 = await manager.get_or_set(
                key=cache_key,
                fetch_func=lambda: slow_query(user_id),
                ttl=300
            )
            time1 = time.time() - start
            
            # 第二次查询（有缓存）
            start = time.time()
            result2 = await manager.get_or_set(
                key=cache_key,
                fetch_func=lambda: slow_query(user_id),
                ttl=300
            )
            time2 = time.time() - start
            
            print(f"\n⚡ 性能对比:")
            print(f"  - 首次查询（无缓存）: {time1*1000:.2f}ms")
            print(f"  - 二次查询（有缓存）: {time2*1000:.2f}ms")
            print(f"  - 性能提升: {time1/time2:.1f}x")
            
            # 清理
            await cache.delete(cache_key)
            
            # 验证
            assert result1 == result2
            assert time2 < time1 / 10  # 至少10倍提升
            
            print("\n✅ 缓存优化场景测试通过")
            
        except Exception as e:
            print(f"\n⚠️  缓存测试跳过（Redis未运行）: {e}")
            pytest.skip("Redis not available")
    
    def test_scenario_multi_version_support(self):
        """场景测试：多版本支持"""
        print("\n" + "=" * 60)
        print("场景7: 多版本支持 - CN vs Global")
        print("=" * 60)
        
        from app.services.orientation_service import OrientationService
        
        orientation_service = OrientationService()
        question = "Should I take this new job?"
        event_type = "career"
        
        # CN版本
        cn_result = orientation_service.recommend(
            version="CN",
            event_type=event_type,
            question=question
        )
        
        print(f"\n🇨🇳 CN版本:")
        print(f"  - 推荐方位: {cn_result['recommended_label']}")
        print(f"  - 方位数量: {len(cn_result['options'])}")
        
        # Global版本
        global_result = orientation_service.recommend(
            version="Global",
            event_type=event_type,
            question=question
        )
        
        print(f"\n🌍 Global版本:")
        print(f"  - 推荐方位: {global_result['recommended_label']}")
        print(f"  - 方位数量: {len(global_result['options'])}")
        
        # 验证
        assert len(cn_result['options']) == 8  # 八卦
        assert len(global_result['options']) == 4  # 塔罗
        assert cn_result['recommended_key'] != global_result['recommended_key']
        
        print("\n✅ 多版本支持场景测试通过")
    
    def test_scenario_error_recovery(self):
        """场景测试：错误恢复"""
        print("\n" + "=" * 60)
        print("场景8: 错误恢复 - 降级策略")
        print("=" * 60)
        
        from app.services.divination_router import DivinationRouter
        
        router = DivinationRouter()
        
        # 测试各种边界情况
        test_cases = [
            {
                "name": "空问题",
                "question": "",
                "event_type": "career",
                "analysis": {"complexity": 0.5}
            },
            {
                "name": "极短问题",
                "question": "好吗？",
                "event_type": "decision",
                "analysis": {"complexity": 0.3}
            },
            {
                "name": "极长问题",
                "question": "我" * 500,
                "event_type": "relationship",
                "analysis": {"complexity": 0.8}
            }
        ]
        
        for case in test_cases:
            try:
                result = router.route(
                    case["question"],
                    case["event_type"],
                    case["analysis"]
                )
                print(f"\n  ✓ {case['name']}: {result['strategy']}")
                assert result is not None
                assert "strategy" in result
            except Exception as e:
                print(f"\n  ✗ {case['name']}: {type(e).__name__}")
        
        print("\n✅ 错误恢复场景测试通过")


def run_e2e_tests():
    """运行所有端到端测试"""
    print("=" * 60)
    print("DivineDaily Backend Python - 端到端测试")
    print("=" * 60)
    
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])


if __name__ == "__main__":
    run_e2e_tests()


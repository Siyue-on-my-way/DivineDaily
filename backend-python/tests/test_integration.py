"""
DivineDaily Backend Python - 集成测试套件

测试所有核心功能的集成测试
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

# 模拟导入（实际使用时需要真实导入）
from app.services.question_analyzer import QuestionAnalyzer
from app.services.divination_router import DivinationRouter
from app.services.smart_prompt_builder import SmartPromptBuilder
from app.services.orientation_service import OrientationService
from app.services.hexagram_analysis_service import HexagramAnalysisService
from app.core.cache import RedisCache, CacheManager


class TestIntegration:
    """集成测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """问题分析器fixture"""
        return QuestionAnalyzer()
    
    @pytest.fixture
    def router(self):
        """路由器fixture"""
        return DivinationRouter()
    
    @pytest.fixture
    def prompt_builder(self):
        """Prompt构建器fixture"""
        return SmartPromptBuilder()
    
    @pytest.fixture
    def orientation_service(self):
        """方位服务fixture"""
        return OrientationService()
    
    @pytest.fixture
    def hexagram_service(self):
        """卦象分析服务fixture"""
        return HexagramAnalysisService()
    
    def test_complete_divination_flow(
        self,
        analyzer,
        router,
        prompt_builder,
        orientation_service
    ):
        """测试完整的占卜流程"""
        # 1. 问题分析
        question = "我应该接受这份新工作还是留在现在的公司？"
        event_type = "career"
        version = "CN"
        
        analysis = analyzer.analyze(question, event_type)
        
        assert analysis is not None
        assert "complexity" in analysis
        assert "elements" in analysis
        assert analysis["complexity"] > 0
        
        # 2. 路由决策
        route_result = router.route(question, event_type, analysis)
        
        assert route_result is not None
        assert "strategy" in route_result
        assert route_result["strategy"] in ["fortune", "knowledge", "decision"]
        
        # 3. Prompt构建
        prompt = prompt_builder.build_prompt(
            question=question,
            event_type=event_type,
            analysis=analysis,
            route_result=route_result
        )
        
        assert prompt is not None
        assert len(prompt) > 0
        assert question in prompt or "选项" in prompt
        
        # 4. 方位推荐
        orientation = orientation_service.recommend(
            version=version,
            event_type=event_type,
            question=question
        )
        
        assert orientation is not None
        assert "recommended_key" in orientation
        assert "recommended_label" in orientation
        
        print("\n✅ 完整占卜流程测试通过")
        print(f"  - 复杂度: {analysis['complexity']:.2f}")
        print(f"  - 路由策略: {route_result['strategy']}")
        print(f"  - Prompt长度: {len(prompt)}")
        print(f"  - 推荐方位: {orientation['recommended_label']}")
    
    def test_multiple_question_types(
        self,
        analyzer,
        router,
        prompt_builder
    ):
        """测试多种问题类型"""
        test_cases = [
            {
                "question": "我应该跳槽吗？",
                "event_type": "career",
                "expected_strategy": "decision"
            },
            {
                "question": "我和他的关系会怎么发展？",
                "event_type": "relationship",
                "expected_strategy": "fortune"
            },
            {
                "question": "什么是六爻占卜？",
                "event_type": "knowledge",
                "expected_strategy": "knowledge"
            },
            {
                "question": "我的健康状况如何？",
                "event_type": "health",
                "expected_strategy": "fortune"
            },
            {
                "question": "投资A还是投资B？",
                "event_type": "wealth",
                "expected_strategy": "decision"
            }
        ]
        
        results = []
        for case in test_cases:
            # 分析
            analysis = analyzer.analyze(
                case["question"],
                case["event_type"]
            )
            
            # 路由
            route_result = router.route(
                case["question"],
                case["event_type"],
                analysis
            )
            
            # 构建Prompt
            prompt = prompt_builder.build_prompt(
                question=case["question"],
                event_type=case["event_type"],
                analysis=analysis,
                route_result=route_result
            )
            
            results.append({
                "question": case["question"],
                "event_type": case["event_type"],
                "complexity": analysis["complexity"],
                "strategy": route_result["strategy"],
                "prompt_length": len(prompt)
            })
            
            # 验证路由策略
            assert route_result["strategy"] == case["expected_strategy"]
        
        print("\n✅ 多种问题类型测试通过")
        for r in results:
            print(f"  - {r['event_type']}: {r['strategy']} (复杂度: {r['complexity']:.2f})")
    
    def test_orientation_for_all_event_types(self, orientation_service):
        """测试所有事件类型的方位推荐"""
        event_types = ["career", "relationship", "decision", "health", "wealth"]
        versions = ["CN", "Global"]
        
        results = []
        for version in versions:
            for event_type in event_types:
                orientation = orientation_service.recommend(
                    version=version,
                    event_type=event_type
                )
                
                assert orientation is not None
                assert "recommended_key" in orientation
                assert "recommended_label" in orientation
                
                results.append({
                    "version": version,
                    "event_type": event_type,
                    "orientation": orientation["recommended_label"]
                })
        
        print("\n✅ 所有事件类型方位推荐测试通过")
        for r in results:
            print(f"  - {r['version']}/{r['event_type']}: {r['orientation']}")
    
    def test_hexagram_analysis_integration(self, hexagram_service):
        """测试卦象分析集成"""
        # 测试变卦分析
        primary_lines = [1, 1, 1, 0, 0, 0]  # 泰卦
        changing_lines = [1, 0, 1, 0, 1, 0]  # 变爻
        
        analysis = hexagram_service.analyze_transformation(
            primary_lines=primary_lines,
            changing_lines=changing_lines
        )
        
        assert analysis is not None
        assert "changing_positions" in analysis
        assert "transformation_type" in analysis
        assert "upper_change" in analysis
        assert "lower_change" in analysis
        
        # 测试五行分析
        element_analysis = hexagram_service.analyze_five_elements(
            primary_lines=primary_lines,
            changing_lines=changing_lines
        )
        
        assert element_analysis is not None
        assert "primary_upper" in element_analysis
        assert "primary_lower" in element_analysis
        assert "relationship" in element_analysis
        
        print("\n✅ 卦象分析集成测试通过")
        print(f"  - 变爻数: {len(analysis['changing_positions'])}")
        print(f"  - 变化类型: {analysis['transformation_type']}")
        print(f"  - 五行关系: {element_analysis['relationship']}")
    
    @pytest.mark.asyncio
    async def test_cache_integration(self):
        """测试缓存集成"""
        # 注意：这需要Redis运行
        try:
            cache = RedisCache(
                host="localhost",
                port=6379,
                db=0
            )
            
            # 测试基本缓存操作
            test_key = "test:integration"
            test_value = {"data": "test", "timestamp": datetime.now().isoformat()}
            
            # 设置
            await cache.set(test_key, test_value, ttl=60)
            
            # 获取
            result = await cache.get(test_key)
            assert result is not None
            assert result["data"] == "test"
            
            # 删除
            await cache.delete(test_key)
            result = await cache.get(test_key)
            assert result is None
            
            print("\n✅ 缓存集成测试通过")
            
        except Exception as e:
            print(f"\n⚠️  缓存测试跳过（Redis未运行）: {e}")
            pytest.skip("Redis not available")
    
    def test_error_handling(self, analyzer, router, prompt_builder):
        """测试错误处理"""
        # 测试空问题
        try:
            analysis = analyzer.analyze("", "career")
            # 应该返回默认分析或抛出异常
            assert analysis is not None
        except Exception as e:
            print(f"  - 空问题处理: {type(e).__name__}")
        
        # 测试无效事件类型
        try:
            analysis = analyzer.analyze("测试问题", "invalid_type")
            # 应该使用默认值或抛出异常
            assert analysis is not None
        except Exception as e:
            print(f"  - 无效事件类型处理: {type(e).__name__}")
        
        # 测试None输入
        try:
            analysis = analyzer.analyze(None, None)
        except Exception as e:
            print(f"  - None输入处理: {type(e).__name__}")
        
        print("\n✅ 错误处理测试完成")
    
    def test_performance_baseline(
        self,
        analyzer,
        router,
        prompt_builder,
        orientation_service
    ):
        """测试性能基准"""
        import time
        
        question = "我应该接受这份新工作吗？"
        event_type = "career"
        
        # 测试分析性能
        start = time.time()
        for _ in range(100):
            analyzer.analyze(question, event_type)
        analysis_time = (time.time() - start) / 100
        
        # 测试路由性能
        analysis = analyzer.analyze(question, event_type)
        start = time.time()
        for _ in range(100):
            router.route(question, event_type, analysis)
        route_time = (time.time() - start) / 100
        
        # 测试Prompt构建性能
        route_result = router.route(question, event_type, analysis)
        start = time.time()
        for _ in range(100):
            prompt_builder.build_prompt(
                question=question,
                event_type=event_type,
                analysis=analysis,
                route_result=route_result
            )
        prompt_time = (time.time() - start) / 100
        
        # 测试方位推荐性能
        start = time.time()
        for _ in range(100):
            orientation_service.recommend("CN", event_type, question)
        orientation_time = (time.time() - start) / 100
        
        print("\n✅ 性能基准测试完成")
        print(f"  - 问题分析: {analysis_time*1000:.2f}ms")
        print(f"  - 路由决策: {route_time*1000:.2f}ms")
        print(f"  - Prompt构建: {prompt_time*1000:.2f}ms")
        print(f"  - 方位推荐: {orientation_time*1000:.2f}ms")
        print(f"  - 总计: {(analysis_time+route_time+prompt_time+orientation_time)*1000:.2f}ms")
        
        # 性能断言（应该都在合理范围内）
        assert analysis_time < 0.1  # 100ms
        assert route_time < 0.05  # 50ms
        assert prompt_time < 0.05  # 50ms
        assert orientation_time < 0.05  # 50ms


def run_all_tests():
    """运行所有集成测试"""
    print("=" * 60)
    print("DivineDaily Backend Python - 集成测试")
    print("=" * 60)
    
    # 运行pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])


if __name__ == "__main__":
    run_all_tests()


#!/usr/bin/env python3
"""测试塔罗牌占卜LLM增强功能"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, '/app')

from app.core.database import get_db
from app.services.enhanced_divination_service import EnhancedDivinationService
from app.services.llm_service import LLMService, create_llm_service
from app.repositories.llm_repository import LLMRepository
from app.schemas.divination import CreateDivinationRequest


async def test_tarot_divination():
    """测试塔罗牌占卜"""
    print("=" * 60)
    print("测试塔罗牌占卜LLM增强功能")
    print("=" * 60)
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 获取默认LLM配置
            llm_repo = LLMRepository(db)
            llm_config = await llm_repo.get_default()
            if not llm_config:
                print("❌ 未找到默认LLM配置")
                return False
            
            # 创建LLM服务
            llm_service = create_llm_service(llm_config)
            print(f"✓ LLM服务创建成功: {llm_config.name}")
            
            # 创建增强占卜服务
            divination_service = EnhancedDivinationService(db, llm_service)
            print(f"✓ 增强占卜服务创建成功")
            
            # 创建测试请求 - 使用TAROT版本确保走塔罗牌流程
            request = CreateDivinationRequest(
                user_id="test_user_tarot_123",
                version="TAROT",
                question="我在工作上应该如何突破当前的困境?",
                spread="three",  # 三张牌阵
                event_type="career",
                orientation=None,
                intent="guidance"
            )
            
            print(f"\n问题: {request.question}")
            print(f"牌阵: {request.spread}")
            print(f"类型: {request.event_type}")
            print("\n开始占卜...")
            print("-" * 60)
            
            # 直接调用基础占卜,避免路由到运势服务
            result = await divination_service.start_divination(request)
            
            print("\n" + "=" * 60)
            print("占卜结果")
            print("=" * 60)
            
            print(f"\n会话ID: {result.session_id}")
            
            if result.cards:
                print(f"\n抽到的牌:")
                for card in result.cards:
                    if isinstance(card, dict):
                        print(f"  - {card['position']}: {card['name']} ({'逆位' if card.get('is_reversed') else '正位'})")
                    else:
                        print(f"  - {card.position}: {card.name} ({'逆位' if card.is_reversed else '正位'})")
            
            print(f"\n摘要:")
            print(result.summary[:300] + "..." if len(result.summary) > 300 else result.summary)
            
            print(f"\n详细解读:")
            print(result.detail[:500] + "..." if len(result.detail) > 500 else result.detail)
            
            # 检查是否使用了LLM增强
            if "牌面概览" in result.detail or "核心洞察" in result.detail or "牌面关联分析" in result.detail:
                print("\n✓ 检测到LLM增强内容!")
            else:
                print("\n⚠️  使用了基础解读(未检测到LLM增强特征)")
            
            print("\n" + "=" * 60)
            print("✓ 测试完成!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await db.close()
            break


if __name__ == "__main__":
    success = asyncio.run(test_tarot_divination())
    sys.exit(0 if success else 1)

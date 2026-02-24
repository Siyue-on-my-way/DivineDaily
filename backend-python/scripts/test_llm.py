"""测试 LLM 调用"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.repositories.llm_repository import LLMRepository
from app.repositories.prompt_config_repository import PromptConfigRepository
from app.services.llm_service import create_llm_service


async def test_llm():
    """测试 LLM 调用"""
    
    # 数据库连接
    DATABASE_URL = "postgresql+asyncpg://divinedaily:divinedaily123@postgres:5432/divinedaily"
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 获取配置
        llm_repo = LLMRepository(session)
        prompt_repo = PromptConfigRepository(session)
        
        # 获取 prompt_config
        prompt_config = await prompt_repo.get_by_scene("daily_fortune", "answer")
        print(f"✓ Prompt Config: {prompt_config.name if prompt_config else 'None'}")
        
        if not prompt_config:
            print("✗ 未找到 prompt_config")
            return
        
        # 获取 llm_config
        llm_config = await llm_repo.get_by_id(prompt_config.llm_config_id)
        print(f"✓ LLM Config: {llm_config.name if llm_config else 'None'}")
        print(f"  - Provider: {llm_config.provider if llm_config else 'None'}")
        print(f"  - Endpoint: {llm_config.endpoint if llm_config else 'None'}")
        print(f"  - Model: {llm_config.model_name if llm_config else 'None'}")
        print(f"  - Enabled: {llm_config.is_enabled if llm_config else 'None'}")
        
        if not llm_config:
            print("✗ 未找到 llm_config")
            return
        
        # 创建 LLM 服务
        llm_service = create_llm_service(
            llm_config=llm_config,
            temperature=prompt_config.temperature,
            max_tokens=prompt_config.max_tokens,
            timeout=prompt_config.timeout_seconds
        )
        
        print(f"✓ LLM Service Type: {type(llm_service).__name__}")
        
        # 测试简单的 prompt
        test_prompt = "请用一句话介绍中国传统命理学。"
        print(f"\n发送测试 Prompt: {test_prompt}")
        
        try:
            response = await llm_service.generate(test_prompt)
            print(f"\n✓ LLM 响应成功:")
            print(f"  响应长度: {len(response)}")
            print(f"  响应内容: {response[:200]}")
        except Exception as e:
            print(f"\n✗ LLM 调用失败: {e}")
            import traceback
            traceback.print_exc()
        
        await llm_service.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  测试 LLM 调用")
    print("=" * 60)
    print()
    
    asyncio.run(test_llm())
    
    print()
    print("=" * 60)
    print("  测试完成")
    print("=" * 60)


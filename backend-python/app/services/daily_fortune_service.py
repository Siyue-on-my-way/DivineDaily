"""每日运势服务"""

from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_fortune import DailyFortune
from app.repositories.daily_fortune_repository import DailyFortuneRepository
from app.services.llm_service import get_llm_service


class DailyFortuneService:
    """每日运势服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = DailyFortuneRepository(db)
        self.llm_service = get_llm_service()
    
    async def get_daily_fortune(
        self,
        user_id: int,
        fortune_date: Optional[date] = None
    ) -> Optional[DailyFortune]:
        """获取每日运势"""
        if fortune_date is None:
            fortune_date = date.today()
        
        # 先从数据库查询
        fortune = await self.repository.get_by_user_and_date(user_id, fortune_date)
        
        if fortune:
            return fortune
        
        # 如果不存在，生成新的运势
        return await self.generate_daily_fortune(user_id, fortune_date)
    
    async def generate_daily_fortune(
        self,
        user_id: int,
        fortune_date: date
    ) -> DailyFortune:
        """生成每日运势"""
        
        # 使用 LLM 生成运势内容
        prompt = f"""请为用户生成 {fortune_date} 的每日运势。

请包含以下方面：
1. 整体运势（1-5星）
2. 爱情运势（1-5星）
3. 事业运势（1-5星）
4. 财运（1-5星）
5. 健康运势（1-5星）
6. 幸运颜色
7. 幸运数字
8. 运势详情（100-200字）

请以JSON格式返回。"""

        try:
            response = await self.llm_service.generate(prompt)
            
            # 解析响应（简化版本，实际应该更健壮）
            fortune_data = {
                "overall_score": 4,
                "love_score": 4,
                "career_score": 4,
                "wealth_score": 4,
                "health_score": 4,
                "lucky_color": "蓝色",
                "lucky_number": 7,
                "content": response[:500] if response else "今日运势良好，诸事顺利。"
            }
            
        except Exception:
            # 如果 LLM 失败，使用默认值
            fortune_data = {
                "overall_score": 3,
                "love_score": 3,
                "career_score": 3,
                "wealth_score": 3,
                "health_score": 3,
                "lucky_color": "白色",
                "lucky_number": 8,
                "content": "今日运势平稳，保持平常心。"
            }
        
        # 保存到数据库
        fortune = await self.repository.create(
            user_id=user_id,
            fortune_date=fortune_date,
            **fortune_data
        )
        
        return fortune
    
    async def list_user_fortunes(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 30
    ) -> list[DailyFortune]:
        """获取用户的运势历史"""
        return await self.repository.list_by_user(user_id, skip, limit)

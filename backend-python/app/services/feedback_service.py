"""反馈服务"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Optional


class FeedbackService:
    """反馈服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def submit_divination_feedback(
        self, session_id: str, user_id: int,
        feedback_type: str, rating: int,
        comment: str = None, tags: List[str] = None,
        is_helpful: bool = None
    ):
        """提交占卜反馈"""
        from app.models.feedback import DivinationFeedback
        
        feedback = DivinationFeedback(
            session_id=session_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            tags=tags or [],
            is_helpful=is_helpful
        )
        
        self.db.add(feedback)
        await self.db.flush()
        
        # 更新占卜会话的反馈状态
        await self._update_session_feedback_status(session_id)
        
        return feedback
    
    async def submit_quality_feedback(
        self, quality_history_id: int, rating: int, comment: str = None
    ):
        """提交问题质量反馈"""
        from app.models.question_quality import QuestionQualityHistory
        
        result = await self.db.execute(
            select(QuestionQualityHistory)
            .where(QuestionQualityHistory.id == quality_history_id)
        )
        record = result.scalar_one_or_none()
        
        if record:
            record.user_feedback = rating
            record.feedback_comment = comment
            await self.db.flush()
        
        return record
    
    async def get_feedback_statistics(self, user_id: Optional[int] = None) -> Dict:
        """获取反馈统计"""
        from app.models.feedback import DivinationFeedback
        
        # 构建基础查询
        query = select(
            func.avg(DivinationFeedback.rating).label('avg_rating'),
            func.count(DivinationFeedback.id).label('total_count'),
            DivinationFeedback.feedback_type
        ).group_by(DivinationFeedback.feedback_type)
        
        if user_id:
            query = query.where(DivinationFeedback.user_id == user_id)
        
        result = await self.db.execute(query)
        
        stats = {}
        for row in result:
            stats[row.feedback_type] = {
                'avg_rating': float(row.avg_rating) if row.avg_rating else 0,
                'total_count': row.total_count
            }
        
        # 计算有帮助的比例
        helpful_query = select(
            func.count(DivinationFeedback.id).label('helpful_count')
        ).where(DivinationFeedback.is_helpful == True)
        
        if user_id:
            helpful_query = helpful_query.where(DivinationFeedback.user_id == user_id)
        
        helpful_result = await self.db.execute(helpful_query)
        helpful_count = helpful_result.scalar() or 0
        
        # 总反馈数
        total_query = select(func.count(DivinationFeedback.id))
        if user_id:
            total_query = total_query.where(DivinationFeedback.user_id == user_id)
        
        total_result = await self.db.execute(total_query)
        total_count = total_result.scalar() or 0
        
        stats['overall'] = {
            'helpful_rate': helpful_count / total_count if total_count > 0 else 0,
            'total_feedback': total_count
        }
        
        return stats
    
    async def _update_session_feedback_status(self, session_id: str):
        """更新会话的反馈状态"""
        # 可以在 divination_sessions 表中添加 has_feedback 字段
        # 这里暂时省略，因为需要修改现有表结构
        pass

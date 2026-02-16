"""占卜主服务"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.divination import DivinationSession as DivinationSessionModel
from app.schemas.divination import CreateDivinationRequest, DivinationResult
from app.services.iching_service import IChingService
from app.services.tarot_service import TarotService
from app.core.exceptions import BadRequestError, NotFoundError


class DivinationService:
    """占卜主服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.iching_service = IChingService()
        self.tarot_service = TarotService()
    
    async def start_divination(self, request: CreateDivinationRequest) -> DivinationResult:
        """开始占卜"""
        # 创建会话
        session_id = str(uuid.uuid4())
        session = DivinationSessionModel(
            id=session_id,
            user_id=request.user_id,
            version=request.version,
            question=request.question,
            event_type=request.event_type or "general",  # 提供默认值
            orientation=request.orientation,
            spread=request.spread,
            intent=request.intent,
            status="processing",
        )
        
        self.db.add(session)
        await self.db.flush()
        
        # 根据版本选择占卜方式
        if request.version == "TAROT":
            result = await self._process_tarot(session_id, request)
        else:  # CN
            result = await self._process_iching(session_id, request)
        
        # 更新会话状态
        session.status = "completed"
        session.result_summary = result['summary']
        session.result_detail = result['detail']
        session.result_data = result
        await self.db.flush()
        
        return DivinationResult(
            session_id=session_id,
            outcome=result.get('outcome'),
            title=result.get('title'),
            spread=result.get('spread'),
            cards=result.get('cards'),
            summary=result['summary'],
            detail=result['detail'],
            hexagram_info=result.get('hexagram_info'),
            recommendations=result.get('recommendations'),
            daily_fortune=result.get('daily_fortune'),
            needs_follow_up=False,
            created_at=datetime.utcnow(),
        )
    
    async def _process_iching(self, session_id: str, request: CreateDivinationRequest) -> Dict[str, Any]:
        """处理周易占卜"""
        result = self.iching_service.generate_result(session_id, request.question)
        return result
    
    async def _process_tarot(self, session_id: str, request: CreateDivinationRequest) -> Dict[str, Any]:
        """处理塔罗占卜"""
        spread = request.spread or "single"
        result = self.tarot_service.generate_result(session_id, request.question, spread)
        return result
    
    async def get_result(self, session_id: str) -> Optional[DivinationResult]:
        """获取占卜结果"""
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(DivinationSessionModel).where(DivinationSessionModel.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise NotFoundError(detail="占卜会话不存在")
        
        if session.status != "completed":
            raise BadRequestError(detail="占卜尚未完成")
        
        result_data = session.result_data or {}
        
        return DivinationResult(
            session_id=session.id,
            outcome=result_data.get('outcome'),
            title=result_data.get('title'),
            spread=result_data.get('spread'),
            cards=result_data.get('cards'),
            summary=session.result_summary or "",
            detail=session.result_detail or "",
            hexagram_info=result_data.get('hexagram_info'),
            recommendations=result_data.get('recommendations'),
            daily_fortune=result_data.get('daily_fortune'),
            needs_follow_up=False,
            created_at=session.created_at,
        )
    
    async def list_history(self, user_id: str, limit: int = 20, offset: int = 0) -> list:
        """获取历史记录"""
        from sqlalchemy import select, desc
        
        result = await self.db.execute(
            select(DivinationSessionModel)
            .where(DivinationSessionModel.user_id == user_id)
            .where(DivinationSessionModel.status == "completed")
            .order_by(desc(DivinationSessionModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        sessions = result.scalars().all()
        
        history = []
        for session in sessions:
            history.append({
                'id': session.id,
                'question': session.question,
                'version': session.version,
                'outcome': session.result_data.get('outcome') if session.result_data else None,
                'summary': session.result_summary,
                'created_at': session.created_at,
            })
        
        return history

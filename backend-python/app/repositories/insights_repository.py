"""洞察数据访问层

提供用户洞察相关的数据查询功能
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.divination import DivinationSession
from app.models.question_quality import QuestionQualityHistory
from datetime import datetime, timedelta


class InsightsRepository:
    """洞察数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overview_stats(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户概览统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 包含总次数、本周次数、平均质量等统计数据
        """
        # 总占卜次数
        total_result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(DivinationSession.user_id == user_id)
        )
        total_count = total_result.scalar() or 0
        
        # 本周占卜次数
        week_ago = datetime.now() - timedelta(days=7)
        week_result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(
                and_(
                    DivinationSession.user_id == user_id,
                    DivinationSession.created_at >= week_ago
                )
            )
        )
        week_count = week_result.scalar() or 0
        
        # 平均问题质量评分
        avg_quality_result = await self.db.execute(
            select(func.avg(QuestionQualityHistory.overall_score))
            .where(QuestionQualityHistory.user_id == int(user_id))
        )
        avg_quality_score = avg_quality_result.scalar() or 0
        
        # 最常见的问题类型
        type_result = await self.db.execute(
            select(
                DivinationSession.event_type,
                func.count(DivinationSession.id).label('count')
            )
            .where(DivinationSession.user_id == user_id)
            .group_by(DivinationSession.event_type)
            .order_by(desc('count'))
            .limit(1)
        )
        most_common_row = type_result.first()
        most_common_type = most_common_row[0] if most_common_row else 'general'
        
        # 成功率（completed / total）
        success_result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(
                and_(
                    DivinationSession.user_id == user_id,
                    DivinationSession.status == 'completed'
                )
            )
        )
        success_count = success_result.scalar() or 0
        success_rate = success_count / total_count if total_count > 0 else 0
        
        # 最后一次占卜时间
        last_result = await self.db.execute(
            select(DivinationSession.created_at)
            .where(DivinationSession.user_id == user_id)
            .order_by(DivinationSession.created_at.desc())
            .limit(1)
        )
        last_divination = last_result.scalar()
        
        return {
            'total_count': total_count,
            'week_count': week_count,
            'avg_quality_score': round(float(avg_quality_score), 1) if avg_quality_score else 0,
            'most_common_type': most_common_type,
            'success_rate': round(success_rate, 2),
            'last_divination': last_divination.isoformat() if last_divination else None
        }
    
    async def get_quality_trend(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取问题质量趋势数据
        
        Args:
            user_id: 用户ID
            days: 天数
            
        Returns:
            Dict: 包含每日质量评分数据
        """
        since = datetime.now() - timedelta(days=days)
        
        # 按日期分组统计
        result = await self.db.execute(
            select(
                func.date(QuestionQualityHistory.created_at).label('date'),
                func.avg(QuestionQualityHistory.overall_score).label('avg_score'),
                func.count(QuestionQualityHistory.id).label('count')
            )
            .where(
                and_(
                    QuestionQualityHistory.user_id == int(user_id),
                    QuestionQualityHistory.created_at >= since
                )
            )
            .group_by('date')
            .order_by('date')
        )
        
        data = [
            {
                'date': row.date.isoformat(),
                'score': round(float(row.avg_score), 1),
                'count': row.count
            }
            for row in result.all()
        ]
        
        # 计算统计指标
        scores = [item['score'] for item in data]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        return {
            'data': data,
            'avg_score': round(avg_score, 1),
            'max_score': max_score,
            'min_score': min_score
        }
    
    async def get_type_distribution(self, user_id: str) -> Dict[str, Any]:
        """
        获取占卜类型分布
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 包含各类型的数量和占比
        """
        # 总数
        total_result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(DivinationSession.user_id == user_id)
        )
        total = total_result.scalar() or 0
        
        if total == 0:
            return {'distribution': []}
        
        # 按类型分组
        result = await self.db.execute(
            select(
                DivinationSession.event_type,
                func.count(DivinationSession.id).label('count')
            )
            .where(DivinationSession.user_id == user_id)
            .group_by(DivinationSession.event_type)
            .order_by(desc('count'))
        )
        
        distribution = [
            {
                'type': row.event_type,
                'count': row.count,
                'percentage': round((row.count / total) * 100, 1)
            }
            for row in result.all()
        ]
        
        return {'distribution': distribution}
    
    async def get_outcome_distribution(
        self, 
        user_id: str, 
        period: str = 'all'
    ) -> Dict[str, Any]:
        """
        获取占卜结果分布
        
        Args:
            user_id: 用户ID
            period: 时间段 (week/month/all)
            
        Returns:
            Dict: 包含吉/凶/平的数量和占比
        """
        query = select(DivinationSession).where(DivinationSession.user_id == user_id)
        
        # 应用时间过滤
        if period == 'week':
            since = datetime.now() - timedelta(days=7)
            query = query.where(DivinationSession.created_at >= since)
        elif period == 'month':
            since = datetime.now() - timedelta(days=30)
            query = query.where(DivinationSession.created_at >= since)
        
        # 获取结果数据（从 result_data JSON 字段中提取 outcome）
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        # 统计结果分布
        outcome_counts = {'吉': 0, '平': 0, '凶': 0}
        for session in sessions:
            if session.result_data and 'hexagram_info' in session.result_data:
                outcome = session.result_data['hexagram_info'].get('outcome', '平')
                if outcome in outcome_counts:
                    outcome_counts[outcome] += 1
        
        total = sum(outcome_counts.values())
        
        distribution = [
            {
                'outcome': outcome,
                'count': count,
                'percentage': round((count / total) * 100, 1) if total > 0 else 0
            }
            for outcome, count in outcome_counts.items()
        ]
        
        return {
            'distribution': distribution,
            'period': period
        }
    
    async def get_activity_timeline(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取活动时间线
        
        Args:
            user_id: 用户ID
            limit: 数量限制
            
        Returns:
            List: 最近的占卜活动列表
        """
        # 获取最近的占卜记录
        sessions_result = await self.db.execute(
            select(DivinationSession)
            .where(DivinationSession.user_id == user_id)
            .order_by(DivinationSession.created_at.desc())
            .limit(limit)
        )
        sessions = sessions_result.scalars().all()
        
        activities = []
        for session in sessions:
            # 获取对应的质量评分
            quality_result = await self.db.execute(
                select(QuestionQualityHistory.overall_score)
                .where(QuestionQualityHistory.session_id == session.id)
                .limit(1)
            )
            quality_score = quality_result.scalar()
            
            # 提取结果
            outcome = '平'
            if session.result_data and 'hexagram_info' in session.result_data:
                outcome = session.result_data['hexagram_info'].get('outcome', '平')
            
            activities.append({
                'id': session.id,
                'question': session.question,
                'type': session.event_type,
                'outcome': outcome,
                'quality_score': quality_score,
                'created_at': session.created_at.isoformat()
            })
        
        return activities

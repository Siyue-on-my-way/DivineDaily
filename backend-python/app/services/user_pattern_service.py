"""用户行为模式分析服务"""

from typing import Dict, List
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class UserPatternService:
    """用户行为模式分析服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_and_update_patterns(self, user_id: int):
        """分析并更新用户行为模式"""
        
        # 1. 分析问题风格
        await self._analyze_question_style(user_id)
        
        # 2. 分析话题偏好
        await self._analyze_topic_preference(user_id)
        
        # 3. 分析时间偏好
        await self._analyze_time_preference(user_id)
        
        # 4. 分析质量趋势
        await self._analyze_quality_trend(user_id)
        
        await self.db.commit()
    
    async def _analyze_question_style(self, user_id: int):
        """分析问题风格模式"""
        from app.models.question_quality import QuestionQualityHistory
        from app.models.user_pattern import UserPattern
        
        # 获取最近 30 条问题记录
        result = await self.db.execute(
            select(QuestionQualityHistory)
            .where(QuestionQualityHistory.user_id == user_id)
            .order_by(QuestionQualityHistory.created_at.desc())
            .limit(30)
        )
        records = result.scalars().all()
        
        if not records:
            return
        
        # 计算统计数据
        avg_length = sum(len(r.original_question) for r in records) / len(records)
        uses_first_person = sum(
            1 for r in records 
            if any(word in r.original_question for word in ['我', '我的'])
        ) / len(records) > 0.5
        
        # 提取常见关键词（简化版）
        all_keywords = []
        for r in records:
            # 这里可以使用 jieba 分词
            words = r.original_question.split()
            all_keywords.extend([w for w in words if len(w) > 1])
        
        from collections import Counter
        common_keywords = [
            word for word, count in Counter(all_keywords).most_common(10)
            if len(word) > 1
        ]
        
        pattern_data = {
            'avg_length': int(avg_length),
            'uses_first_person': uses_first_person,
            'common_keywords': common_keywords,
            'question_complexity': 'high' if avg_length > 30 else 'medium' if avg_length > 15 else 'low'
        }
        
        # 保存或更新模式
        await self._upsert_pattern(
            user_id, 'question_style', pattern_data, 
            len(records), 0.8
        )
    
    async def _analyze_topic_preference(self, user_id: int):
        """分析话题偏好"""
        from app.models.divination import DivinationSession
        from app.models.user_pattern import UserPattern
        
        # 统计各类话题的占比
        result = await self.db.execute(
            select(
                DivinationSession.event_type,
                func.count(DivinationSession.id).label('count')
            )
            .where(DivinationSession.user_id == str(user_id))
            .group_by(DivinationSession.event_type)
        )
        
        topic_counts = {row.event_type: row.count for row in result}
        total = sum(topic_counts.values())
        
        if total == 0:
            return
        
        # 计算百分比
        pattern_data = {
            topic: int((count / total) * 100)
            for topic, count in topic_counts.items()
        }
        
        await self._upsert_pattern(
            user_id, 'topic_preference', pattern_data,
            total, 0.9
        )
    
    async def _analyze_time_preference(self, user_id: int):
        """分析时间偏好"""
        from app.models.divination import DivinationSession
        
        # 获取最近 50 次占卜的时间
        result = await self.db.execute(
            select(DivinationSession.created_at)
            .where(DivinationSession.user_id == str(user_id))
            .order_by(DivinationSession.created_at.desc())
            .limit(50)
        )
        
        timestamps = [row.created_at for row in result]
        
        if not timestamps:
            return
        
        # 统计小时分布
        hour_counts = {}
        weekday_counts = {}
        
        for ts in timestamps:
            hour = ts.hour
            weekday = ts.strftime('%A').lower()
            
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            weekday_counts[weekday] = weekday_counts.get(weekday, 0) + 1
        
        # 找出偏好时段（出现次数 > 平均值）
        avg_hour_count = sum(hour_counts.values()) / len(hour_counts) if hour_counts else 0
        preferred_hours = [
            hour for hour, count in hour_counts.items()
            if count > avg_hour_count
        ]
        
        pattern_data = {
            'preferred_hours': sorted(preferred_hours),
            'weekday_distribution': weekday_counts
        }
        
        await self._upsert_pattern(
            user_id, 'time_preference', pattern_data,
            len(timestamps), 0.7
        )
    
    async def _analyze_quality_trend(self, user_id: int):
        """分析质量趋势"""
        from app.models.question_quality import QuestionQualityHistory
        
        # 获取最近 20 条质量记录
        result = await self.db.execute(
            select(QuestionQualityHistory)
            .where(QuestionQualityHistory.user_id == user_id)
            .order_by(QuestionQualityHistory.created_at.desc())
            .limit(20)
        )
        records = result.scalars().all()
        
        if len(records) < 5:
            return
        
        scores = [r.overall_score for r in reversed(records)]
        avg_score = sum(scores) / len(scores)
        
        # 计算改进率（最近 5 条 vs 之前 5 条）
        if len(scores) >= 10:
            recent_avg = sum(scores[-5:]) / 5
            previous_avg = sum(scores[:5]) / 5
            improvement_rate = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
        else:
            improvement_rate = 0
        
        pattern_data = {
            'avg_quality_score': int(avg_score),
            'improvement_rate': round(improvement_rate, 2),
            'recent_scores': scores[-10:]
        }
        
        await self._upsert_pattern(
            user_id, 'quality_trend', pattern_data,
            len(records), 0.85
        )
    
    async def _upsert_pattern(
        self, user_id: int, pattern_type: str,
        pattern_data: Dict, frequency: int, confidence: float
    ):
        """插入或更新模式"""
        from app.models.user_pattern import UserPattern
        
        result = await self.db.execute(
            select(UserPattern)
            .where(
                UserPattern.user_id == user_id,
                UserPattern.pattern_type == pattern_type
            )
        )
        pattern = result.scalar_one_or_none()
        
        if pattern:
            pattern.pattern_data = pattern_data
            pattern.frequency = frequency
            pattern.confidence = confidence
            pattern.updated_at = datetime.now(timezone.utc)
        else:
            pattern = UserPattern(
                user_id=user_id,
                pattern_type=pattern_type,
                pattern_data=pattern_data,
                frequency=frequency,
                confidence=confidence
            )
            self.db.add(pattern)
        
        await self.db.flush()
    
    async def get_user_patterns(self, user_id: int) -> Dict:
        """获取用户所有模式"""
        from app.models.user_pattern import UserPattern
        
        result = await self.db.execute(
            select(UserPattern)
            .where(UserPattern.user_id == user_id)
        )
        patterns = result.scalars().all()
        
        return {
            p.pattern_type: {
                'data': p.pattern_data,
                'frequency': p.frequency,
                'confidence': p.confidence,
                'updated_at': p.updated_at.isoformat()
            }
            for p in patterns
        }

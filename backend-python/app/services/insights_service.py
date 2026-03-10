"""洞察服务层

提供用户洞察相关的业务逻辑和数据分析
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.insights_repository import InsightsRepository


class InsightsService:
    """洞察服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = InsightsRepository(db)
    
    async def get_overview(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户洞察概览
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 概览数据
        """
        stats = await self.repository.get_overview_stats(user_id)
        
        # 判断质量趋势
        quality_trend = 'stable'
        if stats['avg_quality_score'] >= 80:
            quality_trend = 'excellent'
        elif stats['avg_quality_score'] >= 60:
            quality_trend = 'good'
        elif stats['avg_quality_score'] < 50:
            quality_trend = 'needs_improvement'
        
        return {
            **stats,
            'quality_trend': quality_trend
        }
    
    async def get_quality_trend(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取问题质量趋势
        
        Args:
            user_id: 用户ID
            days: 天数
            
        Returns:
            Dict: 趋势数据
        """
        return await self.repository.get_quality_trend(user_id, days)
    
    async def get_type_distribution(self, user_id: str) -> Dict[str, Any]:
        """
        获取占卜类型分布
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 类型分布数据
        """
        return await self.repository.get_type_distribution(user_id)
    
    async def get_outcome_distribution(
        self, 
        user_id: str, 
        period: str = 'all'
    ) -> Dict[str, Any]:
        """
        获取占卜结果分布
        
        Args:
            user_id: 用户ID
            period: 时间段
            
        Returns:
            Dict: 结果分布数据
        """
        return await self.repository.get_outcome_distribution(user_id, period)
    
    async def get_activity_timeline(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        获取活动时间线
        
        Args:
            user_id: 用户ID
            limit: 数量限制
            
        Returns:
            Dict: 活动列表
        """
        activities = await self.repository.get_activity_timeline(user_id, limit)
        return {'activities': activities}
    
    async def get_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        获取个性化建议
        
        基于用户的占卜数据分析，提供改进建议
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 建议列表
        """
        recommendations = []
        
        # 获取概览数据
        overview = await self.repository.get_overview_stats(user_id)
        
        # 建议1：问题质量改进
        avg_quality = overview['avg_quality_score']
        if avg_quality < 60:
            recommendations.append({
                'type': 'quality',
                'priority': 'high',
                'title': '提高问题质量',
                'message': f'您的平均问题质量为 {avg_quality:.0f} 分，建议参考优秀示例改进问题表述',
                'action': '查看示例'
            })
        elif avg_quality < 80:
            recommendations.append({
                'type': 'quality',
                'priority': 'medium',
                'title': '继续优化问题',
                'message': f'您的问题质量为 {avg_quality:.0f} 分，还有提升空间',
                'action': None
            })
        
        # 建议2：占卜类型平衡
        type_dist = await self.repository.get_type_distribution(user_id)
        if type_dist['distribution']:
            top_type = type_dist['distribution'][0]
            if top_type['percentage'] > 60:
                type_names = {
                    'career': '事业',
                    'relationship': '感情',
                    'decision': '决策',
                    'fortune': '运势',
                    'health': '健康',
                    'wealth': '财运'
                }
                type_name = type_names.get(top_type['type'], '该类')
                recommendations.append({
                    'type': 'balance',
                    'priority': 'medium',
                    'title': '平衡关注点',
                    'message': f'您最近 {top_type["percentage"]:.0f}% 的占卜都是关于{type_name}，建议关注生活其他方面',
                    'action': None
                })
        
        # 建议3：占卜频率
        week_count = overview['week_count']
        if week_count > 20:
            recommendations.append({
                'type': 'frequency',
                'priority': 'medium',
                'title': '适度占卜',
                'message': f'您本周已占卜 {week_count} 次，建议适度占卜，避免过度依赖',
                'action': None
            })
        elif week_count == 0 and overview['total_count'] > 0:
            recommendations.append({
                'type': 'frequency',
                'priority': 'low',
                'title': '保持活跃',
                'message': '您本周还没有占卜，有困惑时可以来寻求指引',
                'action': '开始占卜'
            })
        
        # 建议4：成功率
        success_rate = overview['success_rate']
        if success_rate < 0.8:
            recommendations.append({
                'type': 'success',
                'priority': 'low',
                'title': '检查网络连接',
                'message': f'您的占卜成功率为 {success_rate*100:.0f}%，建议在网络稳定时使用',
                'action': None
            })
        
        # 如果没有建议，添加鼓励信息
        if not recommendations:
            recommendations.append({
                'type': 'encouragement',
                'priority': 'low',
                'title': '使用良好',
                'message': '您的占卜习惯很好，继续保持！',
                'action': None
            })
        
        return {'recommendations': recommendations}

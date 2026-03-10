import { useState, useEffect } from 'react';
import { MobilePage } from '../components/mobile';
import { Card, CardHeader, CardContent } from '../components/mobile/Card';
import { useAuth } from '../lib/AuthContext';
import { useNavigate } from 'react-router-dom';
import { insightsApi } from '../api/insights';
import type {
  OverviewStats,
  TypeDistributionItem,
  RecommendationItem,
  ActivityItem
} from '../types/insights';
import './InsightsPage.css';

/**
 * 用户洞察页面
 * 
 * 展示用户的占卜统计、趋势分析和个性化建议
 */
export default function InsightsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 数据状态
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [typeDistribution, setTypeDistribution] = useState<TypeDistributionItem[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);

  /**
   * 加载洞察数据
   */
  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);

      // 并发加载所有数据
      const [overviewData, typeData, recommendationsData, activitiesData] = await Promise.all([
        insightsApi.getOverview(),
        insightsApi.getTypeDistribution(),
        insightsApi.getRecommendations(),
        insightsApi.getActivityTimeline(5)
      ]);

      setOverview(overviewData);
      setTypeDistribution(typeData.distribution);
      setRecommendations(recommendationsData.recommendations);
      setActivities(activitiesData.activities);
    } catch (err: any) {
      console.error('加载洞察数据失败:', err);
      setError(err.response?.data?.detail || '加载失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, [user]);

  // 格式化类型名称
  const formatTypeName = (type: string): string => {
    const typeMap: Record<string, string> = {
      'career': '事业',
      'relationship': '感情',
      'decision': '决策',
      'fortune': '运势',
      'health': '健康',
      'wealth': '财运',
      'knowledge': '知识',
      'general': '综合'
    };
    return typeMap[type] || type;
  };

  // 格式化时间
  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays === 1) return '昨天';
    if (diffDays < 7) return `${diffDays}天前`;
    
    return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
  };

  // 获取优先级图标
  const getPriorityIcon = (priority: string): string => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '💡';
    }
  };

  // 加载状态
  if (loading) {
    return (
      <MobilePage>
        <div className="insights-container">
          <h2 className="insights-title">📊 我的占卜洞察</h2>
          <div className="insights-loading">
            <div className="loading-spinner"></div>
            <p>加载中...</p>
          </div>
        </div>
      </MobilePage>
    );
  }

  // 错误状态
  if (error) {
    return (
      <MobilePage>
        <div className="insights-container">
          <h2 className="insights-title">📊 我的占卜洞察</h2>
          <div className="insights-error">
            <div className="error-icon">⚠️</div>
            <p>{error}</p>
          </div>
        </div>
      </MobilePage>
    );
  }

  return (
    <MobilePage>
      <div className="insights-container">
        <h2 className="insights-title">📊 我的占卜洞察</h2>

        {/* 统计卡片区 */}
        {overview && (
          <div className="stats-grid">
            <Card className="stat-card">
              <CardContent>
                <div className="stat-value">{overview.total_count}</div>
                <div className="stat-label">总占卜次数</div>
              </CardContent>
            </Card>
            <Card className="stat-card">
              <CardContent>
                <div className="stat-value">{overview.week_count}</div>
                <div className="stat-label">本周次数</div>
              </CardContent>
            </Card>
            <Card className="stat-card">
              <CardContent>
                <div className="stat-value">{overview.avg_quality_score.toFixed(0)}</div>
                <div className="stat-label">平均质量</div>
              </CardContent>
            </Card>
            <Card className="stat-card">
              <CardContent>
                <div className="stat-value">{(overview.success_rate * 100).toFixed(0)}%</div>
                <div className="stat-label">成功率</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 类型分布 */}
        {typeDistribution.length > 0 && (
          <Card>
            <CardHeader title="占卜类型分布" icon="📈" />
            <CardContent>
              <div className="type-distribution">
                {typeDistribution.map((item) => (
                  <div key={item.type} className="type-item">
                    <div className="type-info">
                      <span className="type-name">{formatTypeName(item.type)}</span>
                      <span className="type-count">{item.count}次</span>
                    </div>
                    <div className="type-bar">
                      <div 
                        className="type-bar-fill" 
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                    <span className="type-percentage">{item.percentage.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 最近活动 */}
        {activities.length > 0 && (
          <Card>
            <CardHeader title="最近活动" icon="🕐" />
            <CardContent>
              <div className="activity-list">
                {activities.map((activity) => (
                  <div 
                    key={activity.id} 
                    className="activity-item"
                    onClick={() => navigate(`/history/${activity.id}`)}
                  >
                    <div className="activity-header">
                      <span className="activity-question">{activity.question}</span>
                      <span className="activity-time">{formatTime(activity.created_at)}</span>
                    </div>
                    <div className="activity-meta">
                      <span className="activity-type">{formatTypeName(activity.type)}</span>
                      <span className={`activity-outcome outcome-${activity.outcome}`}>
                        {activity.outcome}
                      </span>
                      {activity.quality_score && (
                        <span className="activity-quality">质量: {activity.quality_score}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 个性化建议 */}
        {recommendations.length > 0 && (
          <Card>
            <CardHeader title="个性化建议" icon="💡" />
            <CardContent>
              <div className="recommendations-list">
                {recommendations.map((rec, index) => (
                  <div key={index} className={`recommendation-item priority-${rec.priority}`}>
                    <div className="recommendation-header">
                      <span className="recommendation-icon">{getPriorityIcon(rec.priority)}</span>
                      <span className="recommendation-title">{rec.title}</span>
                    </div>
                    <p className="recommendation-message">{rec.message}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </MobilePage>
  );
}

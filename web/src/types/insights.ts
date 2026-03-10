/**
 * 洞察相关类型定义
 */

/**
 * 概览统计数据
 */
export interface OverviewStats {
  /** 总占卜次数 */
  total_count: number;
  /** 本周占卜次数 */
  week_count: number;
  /** 平均问题质量评分 */
  avg_quality_score: number;
  /** 最常见的问题类型 */
  most_common_type: string;
  /** 占卜成功率 */
  success_rate: number;
  /** 质量趋势 */
  quality_trend: 'excellent' | 'good' | 'stable' | 'needs_improvement';
  /** 最后一次占卜时间 */
  last_divination?: string;
}

/**
 * 质量趋势数据点
 */
export interface QualityTrendDataPoint {
  /** 日期 (YYYY-MM-DD) */
  date: string;
  /** 平均质量评分 */
  score: number;
  /** 当天占卜次数 */
  count: number;
}

/**
 * 质量趋势响应
 */
export interface QualityTrendResponse {
  /** 趋势数据点列表 */
  data: QualityTrendDataPoint[];
  /** 平均评分 */
  avg_score: number;
  /** 最高评分 */
  max_score: number;
  /** 最低评分 */
  min_score: number;
}

/**
 * 类型分布项
 */
export interface TypeDistributionItem {
  /** 问题类型 */
  type: string;
  /** 数量 */
  count: number;
  /** 占比百分比 */
  percentage: number;
}

/**
 * 类型分布响应
 */
export interface TypeDistributionResponse {
  /** 类型分布列表 */
  distribution: TypeDistributionItem[];
}

/**
 * 结果分布项
 */
export interface OutcomeDistributionItem {
  /** 占卜结果 (吉/凶/平) */
  outcome: string;
  /** 数量 */
  count: number;
  /** 占比百分比 */
  percentage: number;
}

/**
 * 结果分布响应
 */
export interface OutcomeDistributionResponse {
  /** 结果分布列表 */
  distribution: OutcomeDistributionItem[];
  /** 时间段 */
  period: 'week' | 'month' | 'all';
}

/**
 * 活动项
 */
export interface ActivityItem {
  /** 会话ID */
  id: string;
  /** 问题 */
  question: string;
  /** 问题类型 */
  type: string;
  /** 占卜结果 */
  outcome: string;
  /** 问题质量评分 */
  quality_score?: number;
  /** 创建时间 */
  created_at: string;
}

/**
 * 活动时间线响应
 */
export interface ActivityTimelineResponse {
  /** 活动列表 */
  activities: ActivityItem[];
}

/**
 * 建议项
 */
export interface RecommendationItem {
  /** 建议类型 */
  type: 'quality' | 'balance' | 'frequency' | 'success' | 'encouragement';
  /** 优先级 */
  priority: 'high' | 'medium' | 'low';
  /** 标题 */
  title: string;
  /** 建议内容 */
  message: string;
  /** 操作按钮文本 */
  action?: string;
}

/**
 * 建议响应
 */
export interface RecommendationsResponse {
  /** 建议列表 */
  recommendations: RecommendationItem[];
}

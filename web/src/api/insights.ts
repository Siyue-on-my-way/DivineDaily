/**
 * 洞察 API
 * 
 * 提供用户洞察数据的 API 调用方法
 */

import axiosInstance from '../lib/axios';
import type {
  OverviewStats,
  QualityTrendResponse,
  TypeDistributionResponse,
  OutcomeDistributionResponse,
  ActivityTimelineResponse,
  RecommendationsResponse
} from '../types/insights';

/**
 * 洞察 API
 */
export const insightsApi = {
  /**
   * 获取用户洞察概览
   * 
   * @returns 概览统计数据
   */
  getOverview: async (): Promise<OverviewStats> => {
    const response = await axiosInstance.get<OverviewStats>('/insights/overview');
    return response.data;
  },

  /**
   * 获取问题质量趋势
   * 
   * @param days - 天数（默认30天）
   * @returns 质量趋势数据
   */
  getQualityTrend: async (days: number = 30): Promise<QualityTrendResponse> => {
    const response = await axiosInstance.get<QualityTrendResponse>('/insights/quality-trend', {
      params: { days }
    });
    return response.data;
  },

  /**
   * 获取占卜类型分布
   * 
   * @returns 类型分布数据
   */
  getTypeDistribution: async (): Promise<TypeDistributionResponse> => {
    const response = await axiosInstance.get<TypeDistributionResponse>('/insights/type-distribution');
    return response.data;
  },

  /**
   * 获取占卜结果分布
   * 
   * @param period - 时间段（week/month/all）
   * @returns 结果分布数据
   */
  getOutcomeDistribution: async (period: 'week' | 'month' | 'all' = 'all'): Promise<OutcomeDistributionResponse> => {
    const response = await axiosInstance.get<OutcomeDistributionResponse>('/insights/outcome-distribution', {
      params: { period }
    });
    return response.data;
  },

  /**
   * 获取活动时间线
   * 
   * @param limit - 数量限制（默认10条）
   * @returns 活动列表
   */
  getActivityTimeline: async (limit: number = 10): Promise<ActivityTimelineResponse> => {
    const response = await axiosInstance.get<ActivityTimelineResponse>('/insights/activity-timeline', {
      params: { limit }
    });
    return response.data;
  },

  /**
   * 获取个性化建议
   * 
   * @returns 建议列表
   */
  getRecommendations: async (): Promise<RecommendationsResponse> => {
    const response = await axiosInstance.get<RecommendationsResponse>('/insights/recommendations');
    return response.data;
  }
};

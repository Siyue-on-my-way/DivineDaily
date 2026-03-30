import axiosInstance from '../lib/axios';
import type { DivinationResult, DivinationSession } from '../types/divination';

export interface DivinationHistoryParams {
  limit?: number;
  offset?: number;
  event_type?: string;
  version?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  order_by?: string;
  order_direction?: string;
}

export interface DivinationHistoryResponse {
  sessions: DivinationSession[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface DivinationStatsResponse {
  total_count: number;
  by_type: Record<string, number>;
  by_version: Record<string, number>;
  by_status: Record<string, number>;
}

// 占卜 API
export const divinationApi = {
  // 获取占卜历史记录
  getHistory: async (params?: DivinationHistoryParams): Promise<DivinationHistoryResponse> => {
    const response = await axiosInstance.get<DivinationHistoryResponse>('/divinations/history', {
      params,
    });
    return response.data;
  },

  // 获取单个占卜详情
  getDetail: async (sessionId: string): Promise<DivinationResult> => {
    const response = await axiosInstance.get<DivinationResult>(`/divinations/${sessionId}`);
    return response.data;
  },

  // 获取占卜统计
  getStats: async (userId: string): Promise<DivinationStatsResponse> => {
    const response = await axiosInstance.get<DivinationStatsResponse>(`/divinations/stats`, {
      params: { user_id: userId },
    });
    return response.data;
  },

  // 保存占卜结果
  save: async (sessionId: string): Promise<void> => {
    await axiosInstance.post(`/divinations/${sessionId}/save`);
  },

  // 分享占卜结果
  share: async (sessionId: string): Promise<{ share_url: string }> => {
    const response = await axiosInstance.post<{ share_url: string }>(
      `/divinations/${sessionId}/share`
    );
    return response.data;
  },
};

import axiosInstance from '../lib/axios';
import type { DivinationResult, DivinationSession } from '../types/divination';

export interface DivinationHistoryParams {
  page?: number;
  limit?: number;
  user_id?: string;
}

export interface DivinationStatsResponse {
  total_count: number;
  saved_count: number;
  shared_count: number;
}

// 占卜 API
export const divinationApi = {
  // 获取占卜历史记录
  getHistory: async (params?: DivinationHistoryParams): Promise<DivinationResult[]> => {
    const response = await axiosInstance.get<{ data: DivinationResult[] }>('/divinations/history', {
      params,
    });
    return response.data.data;
  },

  // 获取单个占卜详情
  getDetail: async (sessionId: string): Promise<DivinationResult> => {
    const response = await axiosInstance.get<DivinationResult>(`/divinations/${sessionId}/result`);
    return response.data;
  },

  // 获取占卜统计
  getStats: async (userId: string): Promise<DivinationStatsResponse> => {
    const response = await axiosInstance.get<{ data: DivinationStatsResponse }>(`/divinations/stats`, {
      params: { user_id: userId },
    });
    return response.data.data;
  },

  // 保存占卜结果
  save: async (sessionId: string): Promise<void> => {
    await axiosInstance.post(`/divinations/${sessionId}/save`);
  },

  // 分享占卜结果
  share: async (sessionId: string): Promise<{ share_url: string }> => {
    const response = await axiosInstance.post<{ data: { share_url: string } }>(
      `/divinations/${sessionId}/share`
    );
    return response.data.data;
  },
};

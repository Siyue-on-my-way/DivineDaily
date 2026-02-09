import axiosInstance from '../lib/axios';
import type { DailyFortuneInfo } from '../types/divination';

export interface DailyFortuneParams {
  user_id: string;
  date?: string; // YYYY-MM-DD
}

// 运势 API
export const fortuneApi = {
  // 获取每日运势
  getDaily: async (params: DailyFortuneParams): Promise<DailyFortuneInfo> => {
    const response = await axiosInstance.get<{ data: DailyFortuneInfo }>('/fortune/daily', {
      params,
    });
    return response.data.data;
  },

  // 获取运势历史
  getHistory: async (userId: string, limit: number = 7): Promise<DailyFortuneInfo[]> => {
    const response = await axiosInstance.get<{ data: DailyFortuneInfo[] }>('/fortune/history', {
      params: { user_id: userId, limit },
    });
    return response.data.data;
  },
};

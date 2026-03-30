import axiosInstance from '../lib/axios';
import type { DailyFortuneInfo } from '../types/divination';

export interface DailyFortuneParams {
  date?: string; // YYYY-MM-DD
}

// 运势 API
export const fortuneApi = {
  // 获取每日运势
  getDaily: async (params: DailyFortuneParams = {}): Promise<DailyFortuneInfo> => {
    const response = await axiosInstance.post<DailyFortuneInfo>('/daily_fortune', null, {
      params: params.date ? { target_date: params.date } : undefined,
    });
    return response.data;
  },

  // 获取运势历史
  getHistory: async (limit: number = 7, offset: number = 0): Promise<DailyFortuneInfo[]> => {
    const response = await axiosInstance.get<DailyFortuneInfo[]>('/daily_fortune/history', {
      params: { limit, skip: offset },
    });
    return response.data;
  },
};

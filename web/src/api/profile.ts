import axiosInstance from '../lib/axios';

export interface UserProfile {
  user_id: string;
  nickname: string;
  gender: string;
  birth_date: string;
  birth_time?: string;
  lunar_year?: number;
  lunar_month?: number;
  lunar_day?: number;
  is_leap_month?: boolean;
  lunar_month_cn?: string;
  lunar_day_cn?: string;
  ganzhi_year?: string;
  ganzhi_month?: string;
  ganzhi_day?: string;
  animal?: string;
  term?: string;
  is_term?: boolean;
  zodiac_sign?: string;
  is_menstruating?: boolean;
  recent_exercise?: string;
  created_at?: string;
  updated_at?: string;
}

export interface UpdateProfileRequest {
  nickname?: string;
  gender?: string;
  birth_date?: string;
  birth_time?: string;
  zodiac_sign?: string;
  is_menstruating?: boolean;
  recent_exercise?: string;
}

export interface ProfileResponse {
  code: number;
  message: string;
  data?: UserProfile;
}

const api = axiosInstance;

export const profileApi = {
  // 获取用户档案
  getProfile: async (userId: string): Promise<UserProfile> => {
    const response = await api.get<UserProfile | ProfileResponse>(`/profile/${userId}`);
    // 兼容两种响应格式
    if ('code' in response.data && response.data.code === 200 && response.data.data) {
      return response.data.data;
    }
    // 直接返回数据对象的格式（后端当前使用的格式）
    return response.data as UserProfile;
  },

  // 更新用户档案
  updateProfile: async (userId: string, data: UpdateProfileRequest): Promise<UserProfile> => {
    const response = await api.put<UserProfile | ProfileResponse>(`/profile/${userId}`, data);
    // 兼容两种响应格式
    if ('code' in response.data && response.data.code === 200 && response.data.data) {
      return response.data.data;
    }
    // 直接返回数据对象的格式（后端当前使用的格式）
    return response.data as UserProfile;
  },
};

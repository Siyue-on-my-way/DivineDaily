import axiosInstance from '../lib/axios';

export interface UserProfile {
  id: number;
  user_id: number;
  nickname?: string;
  avatar?: string;
  gender?: string;
  birth_date?: string;
  birth_time?: string;
  birth_place?: string;
  preferred_divination?: string;
  notification_enabled?: boolean;
  notification_time?: string;
  bio?: string;
  interests?: string;
  lunar_birth?: string;
  animal?: string;
  zodiac_sign?: string;
  bazi?: string;
  created_at?: string;
  updated_at?: string;
}

export interface UpdateProfileRequest {
  nickname?: string;
  avatar?: string;
  gender?: string;
  birth_date?: string;
  birth_time?: string;
  birth_place?: string;
  preferred_divination?: string;
  notification_enabled?: boolean;
  notification_time?: string;
  bio?: string;
  interests?: string;
}

const api = axiosInstance;

export const profileApi = {
  // 获取用户档案
  getProfile: async (userId: string): Promise<UserProfile> => {
    const response = await api.get<UserProfile>(`/profile/${userId}`);
    return response.data;
  },

  // 更新用户档案
  updateProfile: async (userId: string, data: UpdateProfileRequest): Promise<UserProfile> => {
    const response = await api.put<UserProfile>(`/profile/${userId}`, data);
    return response.data;
  },
};

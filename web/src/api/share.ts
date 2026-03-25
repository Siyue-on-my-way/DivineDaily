import axiosInstance from '../lib/axios';

export interface ShareContent {
  share_token: string;
  question: string;
  result: {
    title: string;
    outcome: string;
    summary: string;
    detail: string;
    hexagram_info?: any;
    cards?: any[];
    daily_fortune?: any;
  };
  metadata: {
    created_at: string;
    view_count: number;
    is_expired: boolean;
  };
}

export interface ShareCreateResponse {
  share_token: string;
  share_url: string;
  created_at: string;
  expires_at?: string;
}

export interface ShareStatsResponse {
  total_shares: number;
  total_views: number;
  shares: Array<{
    share_token: string;
    share_url: string;
    view_count: number;
    created_at: string;
    expires_at?: string;
    is_expired: boolean;
  }>;
}

// 分享 API
export const shareApi = {
  // 创建分享
  createShare: async (
    sessionId: string,
    options?: { expires_days?: number; is_public?: boolean }
  ): Promise<ShareCreateResponse> => {
    const response = await axiosInstance.post<ShareCreateResponse>(
      `/shares/${sessionId}/share`,
      options || {}
    );
    return response.data;
  },

  // 获取分享内容（无需登录）
  getShareContent: async (shareToken: string): Promise<ShareContent> => {
    const response = await axiosInstance.get<ShareContent>(`/shares/${shareToken}`);
    return response.data;
  },

  // 记录浏览
  recordView: async (shareToken: string): Promise<void> => {
    await axiosInstance.post(`/shares/${shareToken}/view`);
  },

  // 删除分享
  deleteShare: async (shareToken: string): Promise<void> => {
    await axiosInstance.delete(`/shares/${shareToken}`);
  },

  // 获取分享统计
  getShareStats: async (sessionId: string): Promise<ShareStatsResponse> => {
    const response = await axiosInstance.get<ShareStatsResponse>(
      `/shares/session/${sessionId}/stats`
    );
    return response.data;
  },
};

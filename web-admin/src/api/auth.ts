import axiosInstance from '../lib/axios';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email?: string;
    role: string;
  };
}

const api = axiosInstance;

// 管理员认证 API
export const authApi = {
  // 管理员登录
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data);
    
    // 验证是否为管理员
    if (response.data.user.role !== 'admin') {
      throw new Error('您没有管理员权限');
    }
    
    return response.data;
  },

  // 管理员登出
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  // 获取当前管理员信息
  me: async (): Promise<LoginResponse['user']> => {
    const response = await api.get<LoginResponse['user']>('/auth/me');
    
    // 验证是否为管理员
    if (response.data.role !== 'admin') {
      throw new Error('您没有管理员权限');
    }
    
    return response.data;
  },
};

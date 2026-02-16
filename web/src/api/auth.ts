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

export interface RegisterRequest {
  username: string;
  email?: string;
  phone?: string;
  password: string;
  confirm_password: string;
}

export interface RefreshTokenResponse {
  token: string;
}

const api = axiosInstance;

// 认证 API
export const authApi = {
  // 用户注册
  register: async (data: RegisterRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/register', data);
    return response.data;
  },

  // 用户登录
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data);
    return response.data;
  },

  // 用户登出
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  // 获取当前用户信息
  me: async (): Promise<LoginResponse['user']> => {
    const response = await api.get<LoginResponse['user']>('/auth/me');
    return response.data;
  },

  // 刷新 Token
  refreshToken: async (): Promise<RefreshTokenResponse> => {
    const response = await api.post<RefreshTokenResponse>('/auth/refresh');
    return response.data;
  },
};

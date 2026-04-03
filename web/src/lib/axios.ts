import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { getAuthToken, getRefreshToken, getTokenType, setAuthToken, setRefreshToken, setTokenType, clearAuthToken } from './AuthContext';
import { authApi } from '../api/auth';

// 创建 axios 实例
const axiosInstance: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 自动注入 Authorization Token
    const token = getAuthToken();
    if (token && config.headers) {
      const tokenType = getTokenType();
      const headerValue = tokenType
        ? `${tokenType.toLowerCase() === 'bearer' ? 'Bearer' : tokenType} ${token}`
        : `Bearer ${token}`;
      config.headers.Authorization = headerValue;
    }

    // 添加请求 ID 用于追踪
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    if (config.headers) {
      config.headers['X-Request-ID'] = requestId;
    }

    // 添加时间戳防止缓存（仅 GET 请求）
    if (config.method === 'get' && config.params) {
      config.params._t = Date.now();
    }

    return config;
  },
  (error: AxiosError) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

let isRefreshing = false;
let refreshQueue: Array<(token: string | null) => void> = [];

const resolveRefreshQueue = (token: string | null) => {
  refreshQueue.forEach((callback) => callback(token));
  refreshQueue = [];
};

const isSilentErrorRequest = (config?: InternalAxiosRequestConfig): boolean => {
  if (!config?.headers) return false;
  const value = config.headers['X-Silent-Error'] as string | undefined;
  return value === '1';
};

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // 401 未授权 - 尝试刷新 token
    if (error.response?.status === 401) {
      if (originalRequest._retry) {
        clearAuthToken();
        if (!window.location.pathname.includes('/login')) {
          window.dispatchEvent(new CustomEvent('auth:unauthorized'));
        }
        return Promise.reject(error);
      }

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearAuthToken();
        if (!window.location.pathname.includes('/login')) {
          window.dispatchEvent(new CustomEvent('auth:unauthorized'));
        }
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push((token) => {
            if (!token) {
              reject(error);
              return;
            }
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(axiosInstance(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        const response = await authApi.refreshToken(refreshToken);
        const tokenType = (response.token_type || 'bearer').toLowerCase();
        const authHeader = `${tokenType === 'bearer' ? 'Bearer' : response.token_type} ${response.token}`.trim();
        setAuthToken(response.token);
        if (response.token_type) {
          setTokenType(response.token_type);
        }
        if (response.refresh_token) {
          setRefreshToken(response.refresh_token);
        }
        resolveRefreshQueue(response.token);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = authHeader;
        }
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        resolveRefreshQueue(null);
        clearAuthToken();
        const expiredMessage = '登录已过期，请重新登录';
        window.dispatchEvent(new CustomEvent('toast:error', {
          detail: { message: expiredMessage }
        }));
        window.dispatchEvent(new CustomEvent('auth:expired', {
          detail: { message: expiredMessage }
        }));
        if (!window.location.pathname.includes('/login')) {
          window.dispatchEvent(new CustomEvent('auth:unauthorized'));
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // 403 无权限
    if (error.response?.status === 403) {
      if (!isSilentErrorRequest(originalRequest)) {
        window.dispatchEvent(new CustomEvent('toast:error', {
          detail: { message: '您没有权限执行此操作' }
        }));
      }
      return Promise.reject(error);
    }

    // 500 服务器错误
    if (error.response?.status === 500) {
      if (!isSilentErrorRequest(originalRequest)) {
        window.dispatchEvent(new CustomEvent('toast:error', {
          detail: { message: '服务器错误，请稍后重试' }
        }));
      }
      return Promise.reject(error);
    }

    // 网络错误 - 自动重试
    if (!error.response && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // 等待 1 秒后重试
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      try {
        return await axiosInstance(originalRequest);
      } catch (retryError) {
        if (!isSilentErrorRequest(originalRequest)) {
          window.dispatchEvent(new CustomEvent('toast:error', {
            detail: { message: '网络连接失败，请检查网络设置' }
          }));
        }
        return Promise.reject(retryError);
      }
    }

    // 其他错误
    const errorMessage = (error.response?.data as any)?.message || error.message || '请求失败';
    console.error('Response error:', errorMessage, error);
    
    return Promise.reject(error);
  }
);

export default axiosInstance;

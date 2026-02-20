import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { getAuthToken, clearAuthToken } from './AuthContext';

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
      config.headers.Authorization = `Bearer ${token}`;
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

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // 401 未授权 - 跳转登录
    if (error.response?.status === 401) {
      clearAuthToken();
      
      // 避免在登录页面重复跳转
      if (!window.location.pathname.includes('/login')) {
        // 触发全局登录弹窗
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }
      
      return Promise.reject(error);
    }

    // 403 无权限
    if (error.response?.status === 403) {
      window.dispatchEvent(new CustomEvent('toast:error', {
        detail: { message: '您没有权限执行此操作' }
      }));
      return Promise.reject(error);
    }

    // 500 服务器错误
    if (error.response?.status === 500) {
      window.dispatchEvent(new CustomEvent('toast:error', {
        detail: { message: '服务器错误，请稍后重试' }
      }));
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
        window.dispatchEvent(new CustomEvent('toast:error', {
          detail: { message: '网络连接失败，请检查网络设置' }
        }));
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

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';

interface User {
  id: string;
  username: string;
  email?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  showLoginModal: boolean;
  setShowLoginModal: (show: boolean) => void;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);

  // 从 localStorage 恢复登录状态
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(TOKEN_KEY);
      const savedUser = localStorage.getItem(USER_KEY);
      
      if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
          
          // 验证 token 是否有效
          try {
            const currentUser = await authApi.me();
            setUser(currentUser);
            localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
          } catch (error) {
            // Token 无效，清除登录状态
            console.error('Token validation failed', error);
            clearAuth();
          }
      } catch (e) {
        console.error('Failed to parse saved user data', e);
          clearAuth();
        }
      }
    };

    initAuth();
  }, []);

  const clearAuth = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  const login = async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error('用户名和密码不能为空');
    }

    try {
      const response = await authApi.login({ username, password });
      
      // 保存 token 和用户信息
      localStorage.setItem(TOKEN_KEY, response.token);
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));
      
      setUser(response.user);
      setIsAuthenticated(true);
      setShowLoginModal(false);
    } catch (error: any) {
      console.error('Login failed', error);
      throw new Error(error.response?.data?.message || '登录失败，请检查用户名和密码');
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout API failed', error);
    } finally {
      clearAuth();
    }
  };

  const refreshAuth = async () => {
    try {
      const response = await authApi.refreshToken();
      localStorage.setItem(TOKEN_KEY, response.token);
    } catch (error) {
      console.error('Token refresh failed', error);
      clearAuth();
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        login,
        logout,
        showLoginModal,
        setShowLoginModal,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// 导出 Token 相关工具函数
export const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const setAuthToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const clearAuthToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

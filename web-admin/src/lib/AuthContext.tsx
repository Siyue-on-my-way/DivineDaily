import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';
import { getAuthToken, clearAuthToken } from '../lib/axios';

interface User {
  id: string;
  username: string;
  email?: string;
  role: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  // 从 localStorage 恢复登录状态
  useEffect(() => {
    const initAuth = async () => {
      const token = getAuthToken();
      const savedUser = localStorage.getItem(USER_KEY);
      
      if (token && savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          
          // 验证是否为管理员
          if (userData.role !== 'admin') {
            clearAuth();
            return;
          }
          
          setUser(userData);
          setIsAuthenticated(true);
          
          // 验证 token 是否有效
          try {
            const currentUser = await authApi.me();
            setUser(currentUser);
            localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
          } catch (error) {
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
    clearAuthToken();
  };

  const login = async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error('用户名和密码不能为空');
    }

    try {
      const response = await authApi.login({ username, password });
      
      // 验证管理员角色
      if (response.user.role !== 'admin') {
        throw new Error('您没有管理员权限');
      }
      
      const userData: User = {
        id: String(response.user.id),
        username: response.user.username,
        email: response.user.email,
        role: response.user.role,
      };
      
      // 保存 token 和用户信息
      localStorage.setItem(TOKEN_KEY, response.token);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
      
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error: any) {
      console.error('Login failed', error);
      throw new Error(error.response?.data?.message || error.message || '登录失败');
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout API failed', error);
    } finally {
      clearAuth();
      window.location.href = '/login';
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        login,
        logout,
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

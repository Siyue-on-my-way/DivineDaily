import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/auth';

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
  showLoginModal: boolean;
  setShowLoginModal: (show: boolean) => void;
  refreshAuth: () => Promise<void>;
  authExpired: boolean;
  setAuthExpired: (expired: boolean) => void;
  authExpiredMessage: string | null;
  setAuthExpiredMessage: (message: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';
const TOKEN_TYPE_KEY = 'auth_token_type';
const USER_KEY = 'auth_user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [authExpired, setAuthExpired] = useState(false);
  const [authExpiredMessage, setAuthExpiredMessage] = useState<string | null>(null);

  useEffect(() => {
    const handleAuthExpired = (event: Event) => {
      const customEvent = event as CustomEvent<{ message?: string }>;
      const message = customEvent.detail?.message || '登录已过期，请重新登录';
      setAuthExpired(true);
      setAuthExpiredMessage(message);
      setShowLoginModal(true);
    };

    window.addEventListener('auth:expired', handleAuthExpired);
    return () => {
      window.removeEventListener('auth:expired', handleAuthExpired);
    };
  }, []);

  // 从 localStorage 恢复登录状态
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(TOKEN_KEY);
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      const savedUser = localStorage.getItem(USER_KEY);
      
      console.log('[AuthContext] Init auth - token:', !!token, 'refreshToken:', !!refreshToken, 'savedUser:', savedUser);

      if (!savedUser) {
        setAuthExpired(false);
        return;
      }

      try {
        const userData = JSON.parse(savedUser);
        console.log('[AuthContext] Parsed user data:', userData);
        
        // 确保数据格式正确，id 转为字符串
        const formattedUser: User = {
          id: String(userData.id),
          username: userData.username,
          email: userData.email,
          role: userData.role || 'normal',
        };
        
        console.log('[AuthContext] Setting user state:', formattedUser);
        setUser(formattedUser);
        setIsAuthenticated(true);

        // 验证 token 是否有效，必要时尝试 refresh
        try {
          const currentUser = await authApi.me();
          const updatedUser: User = {
            id: String(currentUser.id),
            username: currentUser.username,
            email: currentUser.email,
            role: currentUser.role || 'normal',
          };
          console.log('[AuthContext] Updated user from API:', updatedUser);
          setUser(updatedUser);
          localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
        } catch (error) {
          if (refreshToken) {
            try {
              const response = await authApi.refreshToken(refreshToken);
              localStorage.setItem(TOKEN_KEY, response.token);
              if (response.token_type) {
                localStorage.setItem(TOKEN_TYPE_KEY, response.token_type);
              }
              if (response.refresh_token) {
                localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
              }
              const currentUser = await authApi.me();
              const updatedUser: User = {
                id: String(currentUser.id),
                username: currentUser.username,
                email: currentUser.email,
                role: currentUser.role || 'normal',
              };
              console.log('[AuthContext] Updated user after refresh:', updatedUser);
              setUser(updatedUser);
              localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
              return;
            } catch (refreshError) {
              console.error('[AuthContext] Token refresh failed during init', refreshError);
            }
          }

          console.error('[AuthContext] Token validation failed', error);
          setAuthExpired(true);
          setAuthExpiredMessage('登录已过期，请重新登录');
          setShowLoginModal(true);
          clearAuth();
        }
      } catch (e) {
        console.error('[AuthContext] Failed to parse saved user data', e);
        setAuthExpired(true);
        setShowLoginModal(true);
        clearAuth();
      }
    };

    initAuth();
  }, [clearAuth]);

  const clearAuth = useCallback(() => {
    setUser(null);
    setIsAuthenticated(false);
    setAuthExpired(false);
    setAuthExpiredMessage(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_TYPE_KEY);
    localStorage.removeItem(USER_KEY);
  }, []);

  const login = async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error('用户名和密码不能为空');
    }

    try {
      const response = await authApi.login({ username, password });
      
      console.log('[AuthContext] Login response:', response);
      
      // 确保用户信息包含所有字段，id 转为字符串
      const userData: User = {
        id: String(response.user.id),
        username: response.user.username,
        email: response.user.email,
        role: response.user.role || 'normal',
      };
      
      console.log('[AuthContext] Setting user state after login:', userData);
      
      // 保存 token 和用户信息
      localStorage.setItem(TOKEN_KEY, response.token);
      if (response.token_type) {
        localStorage.setItem(TOKEN_TYPE_KEY, response.token_type);
      }
      if (response.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
      }
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
      
      setUser(userData);
      setIsAuthenticated(true);
      setAuthExpired(false);
      setAuthExpiredMessage(null);
      setShowLoginModal(false);
    } catch (error: any) {
      console.error('[AuthContext] Login failed', error);
      throw new Error(error.response?.data?.message || '登录失败，请检查用户名和密码');
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('[AuthContext] Logout API failed', error);
    } finally {
      clearAuth();
    }
  };

  const refreshAuth = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        throw new Error('Missing refresh token');
      }
      const response = await authApi.refreshToken(refreshToken);
      localStorage.setItem(TOKEN_KEY, response.token);
      if (response.token_type) {
        localStorage.setItem(TOKEN_TYPE_KEY, response.token_type);
      }
      if (response.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
      }
      setAuthExpired(false);
      setAuthExpiredMessage(null);
    } catch (error) {
      console.error('[AuthContext] Token refresh failed', error);
      clearAuth();
      throw error;
    }
  }, []);

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
        authExpired,
        setAuthExpired,
        authExpiredMessage,
        setAuthExpiredMessage,
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

export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const getTokenType = (): string | null => {
  return localStorage.getItem(TOKEN_TYPE_KEY);
};

export const setAuthToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const setRefreshToken = (token: string): void => {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

export const setTokenType = (tokenType: string): void => {
  localStorage.setItem(TOKEN_TYPE_KEY, tokenType);
};

export const clearAuthToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(TOKEN_TYPE_KEY);
  localStorage.removeItem(USER_KEY);
};

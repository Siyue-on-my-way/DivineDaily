import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../lib/AuthContext';
import { Button } from './Button';
import { Input } from './Input';
import './LoginModal.css';

export default function LoginModal() {
  const navigate = useNavigate();
  const { showLoginModal, setShowLoginModal, login, authExpired, setAuthExpired, authExpiredMessage } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [retryCountdown, setRetryCountdown] = useState(0);
  const usernameRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      setAuthExpired(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setShowLoginModal(false);
    setAuthExpired(false);
    setUsername('');
    setPassword('');
    setError('');
  };

  const handleRegister = () => {
    handleClose();
    navigate('/register');
  };

  const handleRetryLogin = () => {
    setAuthExpired(false);
    setError('');
    if (username) {
      passwordRef.current?.focus();
    } else {
      usernameRef.current?.focus();
    }
  };

  useEffect(() => {
    if (!showLoginModal) {
      setRetryCountdown(0);
      return;
    }

    if (!authExpired) {
      setRetryCountdown(0);
      if (username) {
        passwordRef.current?.focus();
      } else {
        usernameRef.current?.focus();
      }
      return;
    }

    setRetryCountdown(5);
  }, [showLoginModal, authExpired, username]);

  useEffect(() => {
    if (!authExpired || retryCountdown <= 0) {
      return;
    }

    const timer = window.setTimeout(() => {
      setRetryCountdown((prev) => Math.max(prev - 1, 0));
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [authExpired, retryCountdown]);

  useEffect(() => {
    if (authExpired && retryCountdown === 0) {
      if (username) {
        passwordRef.current?.focus();
      } else {
        usernameRef.current?.focus();
      }
    }
  }, [authExpired, retryCountdown, username]);

  if (!showLoginModal) return null;

  return (
    <div className="login-modal-overlay" onClick={handleClose}>
      <div className="login-modal" onClick={(e) => e.stopPropagation()}>
        <div className="login-modal-header">
          <h2>登录</h2>
          <button className="login-modal-close" onClick={handleClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleLogin} className="login-modal-form">
          {authExpired && (
            <div className="login-modal-error">
              <div>{authExpiredMessage || '登录已过期，请重新登录'}</div>
              <button
                type="button"
                className="login-modal-retry"
                onClick={handleRetryLogin}
                disabled={retryCountdown > 0}
              >
                {retryCountdown > 0 ? `重新登录 (${retryCountdown}s)` : '重新登录'}
              </button>
            </div>
          )}
          <Input
            ref={usernameRef}
            label="用户名"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="请输入用户名/邮箱/手机号"
            autoComplete="username"
            required
          />

          <Input
            ref={passwordRef}
            label="密码"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="请输入密码"
            autoComplete="current-password"
            required
          />

          {error && <div className="login-modal-error">{error}</div>}

          <Button
            type="submit"
            variant="primary"
            fullWidth
            disabled={loading || !username || !password}
          >
            {loading ? '登录中...' : '登录'}
          </Button>

          <div className="login-modal-footer">
            <span className="login-modal-register-text">还没有账号？</span>
            <button 
              type="button"
              className="login-modal-register-link" 
              onClick={handleRegister}
            >
              立即注册
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

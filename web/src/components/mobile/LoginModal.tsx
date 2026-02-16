import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../lib/AuthContext';
import { Button } from './Button';
import { Input } from './Input';
import './LoginModal.css';

export default function LoginModal() {
  const navigate = useNavigate();
  const { showLoginModal, setShowLoginModal, login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!showLoginModal) return null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setShowLoginModal(false);
    setUsername('');
    setPassword('');
    setError('');
  };

  const handleRegister = () => {
    handleClose();
    navigate('/register');
  };

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
          <Input
            label="用户名"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="请输入用户名/邮箱/手机号"
            required
          />

          <Input
            label="密码"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="请输入密码"
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

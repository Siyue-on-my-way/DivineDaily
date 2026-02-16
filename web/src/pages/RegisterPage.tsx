import { useState } from 'react';
import { authApi } from '../api/auth';
import { toast } from '../hooks/useToast';
import { useNavigate } from 'react-router-dom';
import './RegisterPage.css';

type RegisterType = 'email' | 'phone';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [registerType, setRegisterType] = useState<RegisterType>('email');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleTypeChange = (type: RegisterType) => {
    setRegisterType(type);
    // 切换注册方式时清空另一个字段
    if (type === 'email') {
      setFormData({ ...formData, phone: '' });
    } else {
      setFormData({ ...formData, email: '' });
    }
  };

  const validateForm = () => {
    if (!formData.username || formData.username.length < 3) {
      toast.error('用户名至少3个字符');
      return false;
    }

    if (registerType === 'email') {
      if (!formData.email) {
        toast.error('请输入邮箱');
      return false;
    }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      toast.error('邮箱格式不正确');
      return false;
    }
    } else {
      if (!formData.phone) {
        toast.error('请输入手机号');
        return false;
      }
      if (!/^1[3-9]\d{9}$/.test(formData.phone)) {
      toast.error('手机号格式不正确');
      return false;
      }
    }

    if (!formData.password || formData.password.length < 6) {
      toast.error('密码至少6位');
      return false;
    }

    if (formData.password !== formData.confirm_password) {
      toast.error('两次密码不一致');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // 根据注册方式构建请求数据，只发送需要的字段
      const requestData: any = {
        username: formData.username,
        password: formData.password,
        confirm_password: formData.confirm_password,
      };

      if (registerType === 'email') {
        requestData.email = formData.email;
      } else {
        requestData.phone = formData.phone;
      }

      await authApi.register(requestData);
      toast.success('注册成功！');
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <h1 className="register-title">注册账号</h1>
        
        {/* 注册方式选择 */}
        <div className="register-type-selector">
          <button
            type="button"
            className={`type-button ${registerType === 'email' ? 'active' : ''}`}
            onClick={() => handleTypeChange('email')}
          >
            📧 邮箱注册
          </button>
          <button
            type="button"
            className={`type-button ${registerType === 'phone' ? 'active' : ''}`}
            onClick={() => handleTypeChange('phone')}
          >
            📱 手机注册
          </button>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label>用户名 *</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="3-50个字符"
              required
            />
          </div>

          {registerType === 'email' ? (
          <div className="form-group">
              <label>邮箱 *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="example@email.com"
                required
            />
          </div>
          ) : (
          <div className="form-group">
              <label>手机号 *</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="13800138000"
                required
            />
          </div>
          )}

          <div className="form-group">
            <label>密码 *</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="至少6位"
              required
            />
          </div>

          <div className="form-group">
            <label>确认密码 *</label>
            <input
              type="password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              placeholder="再次输入密码"
              required
            />
          </div>

          <button type="submit" className="register-button" disabled={loading}>
            {loading ? '注册中...' : '注册'}
          </button>

          <div className="login-link">
            已有账号？<a href="/" onClick={(e) => { e.preventDefault(); navigate('/'); }}>去登录</a>
          </div>
        </form>
      </div>
    </div>
  );
}

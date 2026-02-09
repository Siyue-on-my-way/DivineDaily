import { useState, useEffect } from 'react';
import { MobilePage } from '../components/mobile';
import { Button } from '../components/mobile/Button';
import { Card, CardContent } from '../components/mobile/Card';
import { useAuth } from '../lib/AuthContext';
import { divinationApi } from '../api/divination';
import { toast } from '../hooks/useToast';
import './ProfilePage.css';

export default function ProfilePage() {
  const { isAuthenticated, user, logout, setShowLoginModal } = useAuth();
  const [stats, setStats] = useState({
    total_count: 0,
    saved_count: 0,
    shared_count: 0,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user?.id) {
      loadStats();
    }
  }, [isAuthenticated, user?.id]);

  const loadStats = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    try {
      const data = await divinationApi.getStats(user.id);
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats', error);
      toast.error('加载统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <MobilePage>
        <div className="profile-login-prompt">
          <div className="profile-login-icon">👤</div>
          <h2>未登录</h2>
          <p>登录后可以查看个人资料和占卜历史</p>
          <Button
            variant="primary"
            size="lg"
            onClick={() => setShowLoginModal(true)}
          >
            立即登录
          </Button>
        </div>
      </MobilePage>
    );
  }

  return (
    <MobilePage loading={loading}>
      <div className="profile-container">
        <Card variant="primary">
          <CardContent>
            <div className="profile-header">
              <div className="profile-avatar">
                {user?.username?.charAt(0).toUpperCase() || '?'}
              </div>
              <div className="profile-info">
                <h2 className="profile-username">{user?.username}</h2>
                <p className="profile-id">ID: {user?.id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="profile-section">
          <h3 className="profile-section-title">个人信息</h3>
          <Card>
            <CardContent>
              <div className="profile-item">
                <span className="profile-item-label">用户名</span>
                <span className="profile-item-value">{user?.username}</span>
              </div>
              <div className="profile-item">
                <span className="profile-item-label">用户ID</span>
                <span className="profile-item-value">{user?.id}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="profile-section">
          <h3 className="profile-section-title">占卜统计</h3>
          <Card>
            <CardContent>
              <div className="profile-stats">
                <div className="profile-stat-item">
                  <div className="profile-stat-value">{stats.total_count}</div>
                  <div className="profile-stat-label">占卜次数</div>
                </div>
                <div className="profile-stat-item">
                  <div className="profile-stat-value">{stats.saved_count}</div>
                  <div className="profile-stat-label">收藏</div>
                </div>
                <div className="profile-stat-item">
                  <div className="profile-stat-value">{stats.shared_count}</div>
                  <div className="profile-stat-label">分享</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="profile-actions">
          <Button variant="secondary" fullWidth onClick={logout}>
            退出登录
          </Button>
        </div>
      </div>
    </MobilePage>
  );
}

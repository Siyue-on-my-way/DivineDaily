import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MobilePage } from '../components/mobile/MobileLayout';
import { Card, CardContent, CardFooter, CardHeader, CardBadge } from '../components/mobile/Card';
import { Button } from '../components/mobile/Button';
import { useAuth } from '../lib/AuthContext';
import { fortuneApi } from '../api/fortune';
import { divinationApi } from '../api/divination';
import { toast } from '../hooks/useToast';
import type { DailyFortuneInfo, DivinationResult } from '../types/divination';
import './HomePage.css';

export default function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [fortune, setFortune] = useState<DailyFortuneInfo | null>(null);
  const [recentDivinations, setRecentDivinations] = useState<DivinationResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user?.id) {
      loadData();
    }
  }, [isAuthenticated, user?.id]);

  const loadData = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    try {
      // 并行加载每日运势和最近占卜
      const [fortuneData, historyData] = await Promise.all([
        fortuneApi.getDaily({ user_id: user.id }).catch(() => null),
        divinationApi.getHistory({ user_id: user.id, limit: 2 }).catch(() => []),
      ]);
      
      setFortune(fortuneData);
      setRecentDivinations(historyData);
    } catch (error) {
      console.error('Failed to load home data', error);
    } finally {
      setLoading(false);
    }
  };

  const getStarRating = (score: number) => {
    const fullStars = Math.floor(score / 20);
    const hasHalfStar = score % 20 >= 10;
    return '★'.repeat(fullStars) + (hasHalfStar ? '☆' : '') + '☆'.repeat(5 - fullStars - (hasHalfStar ? 1 : 0));
  };

  return (
    <MobilePage loading={loading}>
      {/* 欢迎卡片 */}
      <Card variant="primary" size="lg" className="home-welcome-card">
        <div className="home-welcome-content">
          <div className="home-welcome-text">
            <h2 className="home-welcome-title">
              你好，{isAuthenticated ? user?.username : '访客'} 🌿
            </h2>
            <p className="home-welcome-subtitle">今日运势</p>
          </div>
          <div className="home-welcome-stars">
            {fortune ? getStarRating(fortune.score) : '⭐⭐⭐⭐☆'}
          </div>
        </div>
      </Card>

      {/* 快速占卜 */}
      <div className="home-section">
        <h3 className="home-section-title">快速占卜</h3>
        <div className="home-divination-grid">
          <Card clickable onClick={() => navigate('/divination')}>
            <div className="home-divination-item">
              <div className="home-divination-icon">🔮</div>
              <h4 className="home-divination-title">周易卦</h4>
              <p className="home-divination-desc">古老智慧指引</p>
            </div>
          </Card>
          <Card clickable onClick={() => navigate('/tarot')}>
            <div className="home-divination-item">
              <div className="home-divination-icon">🎴</div>
              <h4 className="home-divination-title">塔罗牌</h4>
              <p className="home-divination-desc">探索未知的答案</p>
            </div>
          </Card>
        </div>
      </div>

      {/* 每日运势 */}
      {fortune && (
      <div className="home-section">
        <h3 className="home-section-title">每日运势</h3>
        <Card>
          <CardContent>
            <div className="home-fortune-grid">
              <div className="home-fortune-item">
                <span className="home-fortune-label">财运</span>
                  <span className="home-fortune-stars">{getStarRating(fortune.score)}</span>
              </div>
              <div className="home-fortune-item">
                <span className="home-fortune-label">事业</span>
                  <span className="home-fortune-stars">{getStarRating(fortune.score)}</span>
              </div>
              <div className="home-fortune-item">
                <span className="home-fortune-label">感情</span>
                  <span className="home-fortune-stars">{getStarRating(fortune.score)}</span>
              </div>
              <div className="home-fortune-item">
                <span className="home-fortune-label">健康</span>
                  <span className="home-fortune-stars">{getStarRating(fortune.score)}</span>
                </div>
              </div>
              <p style={{ marginTop: '12px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                {fortune.summary}
              </p>
          </CardContent>
        </Card>
      </div>
      )}

      {/* 最近占卜 */}
      {isAuthenticated && recentDivinations.length > 0 && (
      <div className="home-section">
        <h3 className="home-section-title">最近占卜</h3>
        <div className="home-recent-list">
            {recentDivinations.map((item) => (
              <Card key={item.session_id} clickable onClick={() => navigate(`/history/${item.session_id}`)}>
            <CardHeader 
                  title={item.title || '占卜记录'}
                  subtitle={new Date(item.created_at).toLocaleString('zh-CN')}
              icon="🔮"
            />
            <CardContent>
                  <CardBadge>{item.outcome || '已完成'}</CardBadge>
            </CardContent>
          </Card>
            ))}
          </div>
          <Button variant="text" size="sm" fullWidth onClick={() => navigate('/history')}>
            查看全部历史 →
          </Button>
        </div>
      )}
    </MobilePage>
  );
}

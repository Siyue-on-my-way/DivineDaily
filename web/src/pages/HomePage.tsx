import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MobilePage } from '../components/mobile/MobileLayout';
import { Card, CardContent, CardHeader, CardBadge } from '../components/mobile/Card';
import { Button } from '../components/mobile/Button';
import { useAuth } from '../lib/AuthContext';
import { fortuneApi } from '../api/fortune';
import { divinationApi, type DivinationHistoryResponse } from '../api/divination';
import { profileApi } from '../api/profile';
import type { DailyFortuneInfo, DivinationSession } from '../types/divination';
import './HomePage.css';

export default function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated, user, setShowLoginModal } = useAuth();
  const [fortune, setFortune] = useState<DailyFortuneInfo | null>(null);
  const [hasBirthProfile, setHasBirthProfile] = useState<boolean | null>(null);
  const [recentDivinations, setRecentDivinations] = useState<DivinationSession[]>([]);
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
      // 并行加载档案和最近占卜
      const [profile, historyData] = await Promise.all([
        profileApi.getProfile(user.id).catch(() => null),
        divinationApi.getHistory({ limit: 2, offset: 0 }).catch((): DivinationHistoryResponse => ({
          sessions: [],
          total: 0,
          limit: 2,
          offset: 0,
          has_more: false,
        })),
      ]);
      
      const profileHasBirthDate = Boolean(profile?.birth_date);
      setHasBirthProfile(profileHasBirthDate);
      if (!profileHasBirthDate) {
        setFortune(null);
      } else {
        const fortuneData = await fortuneApi.getDaily().catch(() => null);
        setFortune(fortuneData);
      }
      setRecentDivinations(historyData.sessions);
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
            <p className="home-welcome-subtitle">
              {isAuthenticated ? '今日运势' : '登录查看完整功能'}
            </p>
          </div>
          <div className="home-welcome-stars">
            {fortune ? getStarRating(fortune.overall_score) : '⭐⭐⭐⭐☆'}
          </div>
        </div>
      </Card>

      {/* 未登录提示 */}
      {!isAuthenticated && (
        <Card variant="elevated" className="home-login-prompt">
          <CardContent>
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔮</div>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                登录解锁更多功能
              </h3>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
                查看每日运势、保存占卜历史、个性化推荐
              </p>
              <Button variant="primary" onClick={() => setShowLoginModal(true)}>
                立即登录
              </Button>
              <div style={{ marginTop: '12px' }}>
                <Button variant="text" size="sm" onClick={() => navigate('/register')}>
                  还没有账号？立即注册
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

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
      {isAuthenticated && (
        <div className="home-section">
          <h3 className="home-section-title">每日运势</h3>
          <Card>
            <CardContent>
              {hasBirthProfile === null ? (
                <div className="home-fortune-skeleton" aria-label="正在加载档案">
                  <div className="home-fortune-skeleton__line home-fortune-skeleton__line--lg" />
                  <div className="home-fortune-skeleton__line" />
                  <div className="home-fortune-skeleton__line home-fortune-skeleton__line--sm" />
                  <div className="home-fortune-skeleton__grid">
                    {[0, 1, 2, 3].map((idx) => (
                      <div key={idx} className="home-fortune-skeleton__chip" />
                    ))}
                  </div>
                </div>
              ) : !hasBirthProfile ? (
                <div className="home-fortune-empty">
                  <div className="home-fortune-empty__header">今日运势</div>
                  <div className="home-fortune-empty__score">综合评分: 0分</div>
                  <div className="home-fortune-empty__tip">
                    综合运势: <strong>请至「<button type="button" className="home-fortune-empty__link" onClick={() => navigate('/profile')}>个人中心</button>」补齐生日档案后查看.</strong>
                  </div>
                  <div className="home-fortune-empty__rows">
                    <div>幸运色: 无</div>
                    <div>幸运数字: 无</div>
                    <div>幸运方位: 无</div>
                    <div>幸运时辰: 无</div>
                    <div>宜: 无</div>
                    <div>忌: 无</div>
                  </div>
                </div>
              ) : fortune ? (
                <>
                  <div className="home-fortune-grid">
                    <div className="home-fortune-item">
                      <span className="home-fortune-label">财运</span>
                      <span className="home-fortune-stars">{getStarRating(fortune.wealth_score)}</span>
                    </div>
                    <div className="home-fortune-item">
                      <span className="home-fortune-label">事业</span>
                      <span className="home-fortune-stars">{getStarRating(fortune.career_score)}</span>
                    </div>
                    <div className="home-fortune-item">
                      <span className="home-fortune-label">感情</span>
                      <span className="home-fortune-stars">{getStarRating(fortune.love_score)}</span>
                    </div>
                    <div className="home-fortune-item">
                      <span className="home-fortune-label">健康</span>
                      <span className="home-fortune-stars">{getStarRating(fortune.health_score)}</span>
                    </div>
                  </div>
                  <p style={{ marginTop: '12px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                    {fortune.content}
                  </p>
                </>
              ) : null}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 最近占卜 */}
      {isAuthenticated && Array.isArray(recentDivinations) && recentDivinations.length > 0 && (
        <div className="home-section">
          <h3 className="home-section-title">最近占卜</h3>
          <div className="home-recent-list">
            {recentDivinations.map((item) => (
              <Card key={item.id} clickable onClick={() => navigate(`/history/${item.id}`)}>
                <CardHeader 
                  title={item.question || '占卜记录'}
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

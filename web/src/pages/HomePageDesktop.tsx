import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/AuthContext';
import { fortuneApi } from '../api/fortune';
import { divinationApi } from '../api/divination';
import type { DailyFortuneInfo, DivinationResult } from '../types/divination';
import './HomePageDesktop.css';

export default function HomePageDesktop() {
  const navigate = useNavigate();
  const { isAuthenticated, user, setShowLoginModal } = useAuth();
  const [fortune, setFortune] = useState<DailyFortuneInfo | null>(null);
  const [recentDivinations, setRecentDivinations] = useState<DivinationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, thisWeek: 0, thisMonth: 0 });

  useEffect(() => {
    if (isAuthenticated && user?.id) {
      loadData();
    }
  }, [isAuthenticated, user?.id]);

  const loadData = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    try {
      const [fortuneData, historyData] = await Promise.all([
        fortuneApi.getDaily({ user_id: user.id }).catch(() => null),
        divinationApi.getHistory({ user_id: user.id, limit: 5 }).catch(() => []),
      ]);
      
      setFortune(fortuneData);
      const history = Array.isArray(historyData) ? historyData : [];
      setRecentDivinations(history);
      
      // 计算统计数据
      const now = new Date();
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      
      setStats({
        total: history.length,
        thisWeek: history.filter(d => new Date(d.created_at) > weekAgo).length,
        thisMonth: history.filter(d => new Date(d.created_at) > monthAgo).length,
      });
    } catch (error) {
      console.error('Failed to load home data', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#8bc34a';
    if (score >= 40) return '#ffc107';
    return '#ff9800';
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return '今天';
    if (days === 1) return '昨天';
    if (days < 7) return `${days}天前`;
    return date.toLocaleDateString('zh-CN');
  };

  if (loading) {
    return (
      <div className="desktop-loading">
        <div className="desktop-loading__spinner" />
        <div className="desktop-loading__text">加载中...</div>
      </div>
    );
  }

  return (
    <div className="home-desktop">
      {/* Hero Section */}
      <section className="home-hero">
        <div className="home-hero__content">
          <h1 className="home-hero__title">
            {isAuthenticated ? `你好，${user?.username} 🌿` : '欢迎来到 Divine Daily'}
          </h1>
          <p className="home-hero__subtitle">
            {isAuthenticated 
              ? '让古老的智慧指引你的每一天' 
              : '结合传统占卜与现代AI，为你提供智能化的人生指引'}
          </p>
          {!isAuthenticated && (
            <div className="home-hero__actions">
              <button 
                className="desktop-btn desktop-btn--primary desktop-btn--large"
                onClick={() => setShowLoginModal(true)}
              >
                立即开始
              </button>
              <button 
                className="desktop-btn desktop-btn--outline desktop-btn--large"
                onClick={() => navigate('/register')}
              >
                注册账号
              </button>
            </div>
          )}
        </div>
        <div className="home-hero__decoration">
          <div className="home-hero__circle home-hero__circle--1">🔮</div>
          <div className="home-hero__circle home-hero__circle--2">🎴</div>
          <div className="home-hero__circle home-hero__circle--3">🌿</div>
        </div>
      </section>

      {/* 主要内容区 */}
      <div className="home-content">
        {/* 左侧：快速占卜 + 每日运势 */}
        <div className="home-main">
          {/* 快速占卜 */}
          <section className="desktop-card">
            <div className="desktop-card__header">
              <h2 className="desktop-card__title">快速占卜</h2>
              <p className="desktop-card__subtitle">选择你感兴趣的占卜方式</p>
            </div>
            <div className="home-divination-grid">
              <div 
                className="home-divination-card"
                onClick={() => navigate('/divination')}
              >
                <div className="home-divination-card__icon">🔮</div>
                <h3 className="home-divination-card__title">周易占卜</h3>
                <p className="home-divination-card__desc">古老的六爻智慧，为你指点迷津</p>
                <div className="home-divination-card__badge">传统</div>
              </div>
              <div 
                className="home-divination-card"
                onClick={() => navigate('/tarot')}
              >
                <div className="home-divination-card__icon">🎴</div>
                <h3 className="home-divination-card__title">塔罗占卜</h3>
                <p className="home-divination-card__desc">神秘的塔罗牌阵，探索未知答案</p>
                <div className="home-divination-card__badge">神秘</div>
              </div>
            </div>
          </section>

          {/* 每日运势 */}
          {isAuthenticated && fortune && (
            <section className="desktop-card">
              <div className="desktop-card__header">
                <div>
                  <h2 className="desktop-card__title">今日运势</h2>
                  <p className="desktop-card__subtitle">
                    {new Date().toLocaleDateString('zh-CN', { 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric',
                      weekday: 'long'
                    })}
                  </p>
                </div>
                <div 
                  className="home-fortune-score"
                  style={{ background: getScoreColor(fortune.score) }}
                >
                  {fortune.score}
                </div>
              </div>
              
              <div className="home-fortune-content">
                <p className="home-fortune-summary">{fortune.summary}</p>
                
                <div className="home-fortune-details">
                  <div className="home-fortune-detail">
                    <span className="home-fortune-detail__label">💰 财运</span>
                    <span className="home-fortune-detail__value">{fortune.wealth || '平稳'}</span>
                  </div>
                  <div className="home-fortune-detail">
                    <span className="home-fortune-detail__label">💼 事业</span>
                    <span className="home-fortune-detail__value">{fortune.career || '顺利'}</span>
                  </div>
                  <div className="home-fortune-detail">
                    <span className="home-fortune-detail__label">💕 感情</span>
                    <span className="home-fortune-detail__value">{fortune.love || '和谐'}</span>
                  </div>
                  <div className="home-fortune-detail">
                    <span className="home-fortune-detail__label">🏃 健康</span>
                    <span className="home-fortune-detail__value">{fortune.health || '良好'}</span>
                  </div>
                </div>

                <div className="home-fortune-lucky">
                  <div className="home-fortune-lucky-item">
                    <span className="home-fortune-lucky-item__label">幸运色</span>
                    <span className="home-fortune-lucky-item__value">{fortune.lucky_color}</span>
                  </div>
                  <div className="home-fortune-lucky-item">
                    <span className="home-fortune-lucky-item__label">幸运数字</span>
                    <span className="home-fortune-lucky-item__value">{fortune.lucky_number}</span>
                  </div>
                  <div className="home-fortune-lucky-item">
                    <span className="home-fortune-lucky-item__label">幸运方位</span>
                    <span className="home-fortune-lucky-item__value">{fortune.lucky_direction}</span>
                  </div>
                  <div className="home-fortune-lucky-item">
                    <span className="home-fortune-lucky-item__label">幸运时辰</span>
                    <span className="home-fortune-lucky-item__value">{fortune.lucky_time}</span>
                  </div>
                </div>

                {(fortune.yi?.length > 0 || fortune.ji?.length > 0) && (
                  <div className="home-fortune-advice">
                    {fortune.yi?.length > 0 && (
                      <div className="home-fortune-advice__section home-fortune-advice__section--yi">
                        <h4>宜</h4>
                        <ul>
                          {fortune.yi.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {fortune.ji?.length > 0 && (
                      <div className="home-fortune-advice__section home-fortune-advice__section--ji">
                        <h4>忌</h4>
                        <ul>
                          {fortune.ji.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </section>
          )}
        </div>

        {/* 右侧：统计 + 最近记录 */}
        <aside className="home-sidebar">
          {/* 统计卡片 */}
          {isAuthenticated && (
            <section className="desktop-card desktop-card--compact">
              <h3 className="desktop-card__title">占卜统计</h3>
              <div className="home-stats">
                <div className="home-stat">
                  <div className="home-stat__value">{stats.total}</div>
                  <div className="home-stat__label">总次数</div>
                </div>
                <div className="home-stat">
                  <div className="home-stat__value">{stats.thisWeek}</div>
                  <div className="home-stat__label">本周</div>
                </div>
                <div className="home-stat">
                  <div className="home-stat__value">{stats.thisMonth}</div>
                  <div className="home-stat__label">本月</div>
                </div>
              </div>
            </section>
          )}

          {/* 最近占卜 */}
          {isAuthenticated && recentDivinations.length > 0 && (
            <section className="desktop-card desktop-card--compact">
              <div className="desktop-card__header">
                <h3 className="desktop-card__title">最近占卜</h3>
                <button 
                  className="desktop-btn desktop-btn--small"
                  onClick={() => navigate('/history')}
                >
                  查看全部
                </button>
              </div>
              <div className="home-recent-list">
                {recentDivinations.map((item) => (
                  <div 
                    key={item.session_id}
                    className="home-recent-item"
                    onClick={() => navigate(`/history/${item.session_id}`)}
                  >
                    <div className="home-recent-item__icon">
                      {item.hexagram_info ? '🔮' : '🎴'}
                    </div>
                    <div className="home-recent-item__content">
                      <div className="home-recent-item__title">
                        {item.title || '占卜记录'}
                      </div>
                      <div className="home-recent-item__time">
                        {formatDate(item.created_at)}
                      </div>
                    </div>
                    <div className="home-recent-item__badge">
                      {item.outcome || '已完成'}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 未登录提示 */}
          {!isAuthenticated && (
            <section className="desktop-card desktop-card--compact home-login-card">
              <div className="home-login-card__icon">🔮</div>
              <h3 className="home-login-card__title">登录解锁更多功能</h3>
              <p className="home-login-card__desc">
                查看每日运势、保存占卜历史、获取个性化推荐
              </p>
              <button 
                className="desktop-btn desktop-btn--primary"
                onClick={() => setShowLoginModal(true)}
              >
                立即登录
              </button>
              <button 
                className="desktop-btn desktop-btn--secondary"
                style={{ marginTop: '12px' }}
                onClick={() => navigate('/register')}
              >
                注册账号
              </button>
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}


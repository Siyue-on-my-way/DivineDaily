import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/AuthContext';
import { fortuneApi } from '../api/fortune';
import { divinationApi } from '../api/divination';
import { profileApi } from '../api/profile';
import type { DailyFortuneInfo, DivinationSession } from '../types/divination';
import { Card, CardContent, CardHeader } from '../components/mobile/Card';
import { Button } from '../components/mobile/Button';
import { toast } from '../hooks/useToast';
import { formatApiErrorMessage } from '../utils/apiError';
import './HomePageDesktop.css';

export default function HomePageDesktop() {
  const navigate = useNavigate();
  const { isAuthenticated, user, setShowLoginModal } = useAuth();
  const [fortune, setFortune] = useState<DailyFortuneInfo | null>(null);
  const [hasBirthProfile, setHasBirthProfile] = useState<boolean | null>(null);
  const [recentDivinations, setRecentDivinations] = useState<DivinationSession[]>([]);
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
      const [profile, historyResponse] = await Promise.all([
        profileApi.getProfile(user.id).catch(() => null),
        divinationApi.getHistory({ limit: 5 }).catch((err) => {
          toast.error(formatApiErrorMessage(err, '占卜历史加载失败'));
          return { sessions: [], total: 0, limit: 5, offset: 0, has_more: false };
        }),
      ]);

      const profileHasBirthDate = Boolean(profile?.birth_date);
      setHasBirthProfile(profileHasBirthDate);

      if (!profileHasBirthDate) {
        setFortune(null);
      } else {
        const fortuneData = await fortuneApi.getDaily().catch((err) => {
          toast.error(formatApiErrorMessage(err, '今日运势加载失败'));
          return null;
        });
        setFortune(fortuneData);
      }

      const history = historyResponse.sessions;
      setRecentDivinations(history);
      
      // 计算统计数据
      const now = new Date();
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      
      setStats({
        total: history.length,
        thisWeek: history.filter((d: any) => new Date(d.created_at) > weekAgo).length,
        thisMonth: history.filter((d: any) => new Date(d.created_at) > monthAgo).length,
      });
    } catch (error) {
      console.error('Failed to load home data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartDivination = () => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
      return;
    }
    navigate('/divination');
  };

  // 辅助函数：将逗号分隔的字符串转换为数组
  const parseCommaSeparated = (str: string | undefined): string[] => {
    if (!str) return [];
    return str.split(',').map(item => item.trim()).filter(item => item);
  };

  return (
    <div className="home-desktop">
      {/* Hero Section */}
      <div className="home-hero">
        <div className="home-hero__content">
          <h1 className="home-hero__title">
            Divine Daily
          </h1>
          <p className="home-hero__subtitle">
            让占卜更智能 - 结合传统玄学与现代AI的智能占卜平台
          </p>
          <p className="home-hero__subtitle">
            欢迎感兴趣的巫婆巫师们与思越共建, 微信: StayOOOptimistic
          </p>
            <div className="home-hero__actions">
            <Button variant="primary" size="lg" onClick={handleStartDivination}>
              开始占卜
            </Button>
            <Button variant="outline" size="lg" onClick={() => navigate('/about')}>
              了解更多
            </Button>
            </div>
        </div>
        <div className="home-hero__decoration">
          <div className="home-hero__circle home-hero__circle--1">🔮</div>
          <div className="home-hero__circle home-hero__circle--2">🎴</div>
          <div className="home-hero__circle home-hero__circle--3">✨</div>
        </div>
      </div>

      {/* 主要内容区 */}
      <div className="home-content">
        <div className="home-main">
          {/* 快速占卜 */}
          <Card>
            <CardHeader title="快速占卜" subtitle="选择您喜欢的占卜方式" />
            <CardContent>
            <div className="home-divination-grid">
                <div className="home-divination-card" onClick={handleStartDivination}>
                  <div className="home-divination-card__badge">热门</div>
                <div className="home-divination-card__icon">🔮</div>
                <h3 className="home-divination-card__title">周易占卜</h3>
                  <p className="home-divination-card__desc">
                    古老的东方智慧，通过六爻卦象为您指引方向
                  </p>
                </div>
                <div className="home-divination-card" onClick={() => navigate('/tarot')}>
                  <div className="home-divination-card__badge">推荐</div>
                  <div className="home-divination-card__icon">🎴</div>
                  <h3 className="home-divination-card__title">塔罗占卜</h3>
                  <p className="home-divination-card__desc">
                    神秘的西方塔罗，探索未知的答案和可能性
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
              
          {/* 每日运势 */}
          {isAuthenticated && (
            <Card>
              <CardHeader
                title="今日运势"
                subtitle={`综合评分: ${fortune?.overall_score ?? 0}分`}
              />
              <CardContent>
              <div className="home-fortune-content">
                  {hasBirthProfile === null ? (
                    <div className="home-fortune-summary home-fortune-summary--skeleton" aria-label="正在加载档案">
                      <div className="home-fortune-skeleton__line home-fortune-skeleton__line--lg" />
                      <div className="home-fortune-skeleton__line" />
                      <div className="home-fortune-skeleton__line home-fortune-skeleton__line--sm" />
                    </div>
                  ) : !hasBirthProfile ? (
                    <div className="home-fortune-summary home-fortune-summary--empty">
                      <div className="home-fortune-empty-line">
                        综合运势:{' '}
                        <span className="home-fortune-empty-tip">
                          请至「
                          <button
                            type="button"
                            className="home-fortune-empty-link"
                            onClick={() => navigate('/profile')}
                          >
                            个人中心
                          </button>
                          」补齐生日档案后查看.
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="home-fortune-summary">
                      {fortune?.content}
                    </div>
                  )}

                <div className="home-fortune-lucky">
                  {hasBirthProfile === null ? (
                    <>
                      {[0, 1, 2, 3].map((idx) => (
                        <div key={idx} className="home-fortune-lucky-item home-fortune-lucky-item--skeleton" aria-hidden="true">
                          <div className="home-fortune-lucky-item__label">　</div>
                          <div className="home-fortune-lucky-item__value home-fortune-skeleton__block" />
                        </div>
                      ))}
                    </>
                  ) : (
                    <>
                      <div className="home-fortune-lucky-item">
                          <div className="home-fortune-lucky-item__label">幸运色</div>
                          <div className="home-fortune-lucky-item__value">{hasBirthProfile ? (fortune?.lucky_color || '-') : '无'}</div>
                      </div>
                      <div className="home-fortune-lucky-item">
                          <div className="home-fortune-lucky-item__label">幸运数字</div>
                          <div className="home-fortune-lucky-item__value">{hasBirthProfile ? (fortune?.lucky_number || '-') : '无'}</div>
                      </div>
                      <div className="home-fortune-lucky-item">
                          <div className="home-fortune-lucky-item__label">幸运方位</div>
                          <div className="home-fortune-lucky-item__value">{hasBirthProfile ? (fortune?.lucky_direction || '-') : '无'}</div>
                      </div>
                      <div className="home-fortune-lucky-item">
                          <div className="home-fortune-lucky-item__label">幸运时辰</div>
                          <div className="home-fortune-lucky-item__value">{hasBirthProfile ? (fortune?.lucky_time || '-') : '无'}</div>
                      </div>
                    </>
                  )}
                </div>

                  {hasBirthProfile === null ? (
                    <div className="home-fortune-advice" aria-label="正在加载宜忌">
                      <div className="home-fortune-advice__section home-fortune-advice__section--yi">
                        <h4>✓ 宜</h4>
                        <ul>
                          <li className="home-fortune-skeleton__line" style={{ width: '70%' }} />
                          <li className="home-fortune-skeleton__line" style={{ width: '55%' }} />
                        </ul>
                      </div>
                      <div className="home-fortune-advice__section home-fortune-advice__section--ji">
                        <h4>✗ 忌</h4>
                        <ul>
                          <li className="home-fortune-skeleton__line" style={{ width: '65%' }} />
                          <li className="home-fortune-skeleton__line" style={{ width: '50%' }} />
                        </ul>
                      </div>
                    </div>
                  ) : hasBirthProfile ? (
                    (fortune?.yi || fortune?.ji) && (
                  <div className="home-fortune-advice">
                      {fortune?.yi && parseCommaSeparated(fortune.yi).length > 0 && (
                      <div className="home-fortune-advice__section home-fortune-advice__section--yi">
                          <h4>✓ 宜</h4>
                        <ul>
                            {parseCommaSeparated(fortune.yi).map((item, index) => (
                              <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                      {fortune?.ji && parseCommaSeparated(fortune.ji).length > 0 && (
                      <div className="home-fortune-advice__section home-fortune-advice__section--ji">
                          <h4>✗ 忌</h4>
                        <ul>
                            {parseCommaSeparated(fortune.ji).map((item, index) => (
                              <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                    )
                  ) : (
                    <div className="home-fortune-advice">
                      <div className="home-fortune-advice__section home-fortune-advice__section--yi">
                        <h4>✓ 宜</h4>
                        <ul><li>无</li></ul>
                      </div>
                      <div className="home-fortune-advice__section home-fortune-advice__section--ji">
                        <h4>✗ 忌</h4>
                        <ul><li>无</li></ul>
                      </div>
                    </div>
                  )}
              </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 侧边栏 */}
        <div className="home-sidebar">
          {/* 统计数据 */}
          {isAuthenticated && (
            <Card>
              <CardHeader title="占卜统计" />
              <CardContent>
              <div className="home-stats">
                <div className="home-stat">
                  <div className="home-stat__value">{stats.total}</div>
                    <div className="home-stat__label">总计</div>
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
              </CardContent>
            </Card>
          )}

          {/* 最近占卜 */}
          {recentDivinations.length > 0 && (
            <Card>
              <CardHeader 
                title="最近占卜" 
                action={
                  <Button variant="text" size="sm" onClick={() => navigate('/history')}>
                  查看全部
                  </Button>
                }
              />
              <CardContent>
              <div className="home-recent-list">
                  {recentDivinations.map((item: any) => (
                  <div 
                      key={item.id} 
                    className="home-recent-item"
                      onClick={() => navigate(`/history/${item.id}`)}
                  >
                      <div className="home-recent-item__icon">🔮</div>
                    <div className="home-recent-item__content">
                        <div className="home-recent-item__title">{item.question}</div>
                      <div className="home-recent-item__time">
                          {new Date(item.created_at).toLocaleDateString('zh-CN')}
                      </div>
                    </div>
                    <div className="home-recent-item__badge">
                      {item.outcome || '已完成'}
                    </div>
                  </div>
                ))}
              </div>
              </CardContent>
            </Card>
          )}

          {/* 未登录提示 */}
          {!isAuthenticated && (
            <Card className="home-login-card">
              <CardContent>
              <div className="home-login-card__icon">🔮</div>
              <h3 className="home-login-card__title">登录解锁更多功能</h3>
              <p className="home-login-card__desc">
                查看每日运势、保存占卜历史、获取个性化推荐
              </p>
                <Button variant="primary" fullWidth onClick={() => setShowLoginModal(true)}>
                立即登录
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}
    </div>
  );
}

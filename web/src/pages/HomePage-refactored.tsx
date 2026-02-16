import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { MobilePage } from '../components/mobile/MobileLayout';
import { Button } from '../components/mobile/Button';
import { useAuth } from '../lib/AuthContext';
import { fortuneApi } from '../api/fortune';
import { divinationApi } from '../api/divination';
import { toast } from '../hooks/useToast';
import { OnboardingFlow } from '../components/onboarding';
import type { DailyFortuneInfo, DivinationResult } from '../types/divination';
import './HomePage-new.css';

export default function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [fortune, setFortune] = useState<DailyFortuneInfo | null>(null);
  const [recentDivinations, setRecentDivinations] = useState<DivinationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({
    fortune: false,
    recent: false
  });

  useEffect(() => {
    // 检查是否首次访问
    const hasCompletedOnboarding = localStorage.getItem('onboarding_completed');
    if (!hasCompletedOnboarding) {
      setShowOnboarding(true);
    }

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
        divinationApi.getHistory({ user_id: user.id, limit: 3 }).catch(() => []),
      ]);
      
      setFortune(fortuneData);
      setRecentDivinations(historyData);
    } catch (error) {
      console.error('Failed to load home data', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10B981';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  };

  return (
    <>
      {showOnboarding && (
        <OnboardingFlow onComplete={() => setShowOnboarding(false)} />
      )}

      <MobilePage loading={loading}>
        {/* Hero 区域 */}
        <motion.div
          className="home-hero"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="home-hero__content">
            <div className="home-hero__greeting">
              你好，{isAuthenticated ? user?.username : '访客'} 🌿
            </div>
            <motion.div
              className="home-hero__score"
              style={{ color: fortune ? getScoreColor(fortune.score) : 'white' }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
            >
              {fortune?.score || 85}
            </motion.div>
            <div className="home-hero__score-label">今日运势</div>
            {fortune && (
              <div className="home-hero__action">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => toggleSection('fortune')}
                >
                  查看详情
                </Button>
              </div>
            )}
          </div>
        </motion.div>

        {/* 快速入口 */}
        <motion.div
          className="home-quick-actions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <motion.div
            className="home-quick-action"
            onClick={() => navigate('/divination')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="home-quick-action__icon">🔮</div>
            <h3 className="home-quick-action__title">开始占卜</h3>
            <p className="home-quick-action__desc">周易六爻指引</p>
          </motion.div>

          <motion.div
            className="home-quick-action"
            onClick={() => navigate('/history')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="home-quick-action__icon">📜</div>
            <h3 className="home-quick-action__title">历史记录</h3>
            <p className="home-quick-action__desc">查看过往占卜</p>
          </motion.div>
        </motion.div>

        {/* 每日运势详情（可折叠） */}
        {fortune && (
          <motion.div
            className="home-collapsible"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <div
              className="home-collapsible__header"
              onClick={() => toggleSection('fortune')}
            >
              <h3 className="home-collapsible__title">
                <span>⭐</span>
                每日运势详情
              </h3>
              <div
                className={`home-collapsible__icon ${
                  expandedSections.fortune ? 'home-collapsible__icon--expanded' : ''
                }`}
              >
                ▼
              </div>
            </div>

            <AnimatePresence>
              {expandedSections.fortune && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="home-collapsible__content"
                >
                  <div className="home-fortune-grid-compact">
                    <div className="home-fortune-item-compact">
                      <div className="home-fortune-item-compact__icon">💰</div>
                      <div className="home-fortune-item-compact__label">财运</div>
                      <div className="home-fortune-item-compact__value">
                        {Math.floor(fortune.score * 0.9)}
                      </div>
                    </div>
                    <div className="home-fortune-item-compact">
                      <div className="home-fortune-item-compact__icon">💼</div>
                      <div className="home-fortune-item-compact__label">事业</div>
                      <div className="home-fortune-item-compact__value">
                        {Math.floor(fortune.score * 0.95)}
                      </div>
                    </div>
                    <div className="home-fortune-item-compact">
                      <div className="home-fortune-item-compact__icon">❤️</div>
                      <div className="home-fortune-item-compact__label">感情</div>
                      <div className="home-fortune-item-compact__value">
                        {Math.floor(fortune.score * 0.85)}
                      </div>
                    </div>
                    <div className="home-fortune-item-compact">
                      <div className="home-fortune-item-compact__icon">🧘</div>
                      <div className="home-fortune-item-compact__label">健康</div>
                      <div className="home-fortune-item-compact__value">
                        {Math.floor(fortune.score * 1.05)}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* 最近占卜（可折叠） */}
        {isAuthenticated && recentDivinations.length > 0 && (
          <motion.div
            className="home-collapsible"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <div
              className="home-collapsible__header"
              onClick={() => toggleSection('recent')}
            >
              <h3 className="home-collapsible__title">
                <span>🔮</span>
                最近占卜
              </h3>
              <div
                className={`home-collapsible__icon ${
                  expandedSections.recent ? 'home-collapsible__icon--expanded' : ''
                }`}
              >
                ▼
              </div>
            </div>

            <AnimatePresence>
              {expandedSections.recent && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="home-collapsible__content"
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {recentDivinations.map((item, index) => (
                      <motion.div
                        key={item.session_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        style={{
                          padding: '16px',
                          background: 'white',
                          borderRadius: '12px',
                          border: '1px solid var(--border-light)',
                          cursor: 'pointer'
                        }}
                        onClick={() => navigate(`/history/${item.session_id}`)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                          {item.title || '占卜记录'}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          {new Date(item.created_at).toLocaleString('zh-CN')}
                        </div>
                      </motion.div>
                    ))}
                    <Button
                      variant="text"
                      size="sm"
                      fullWidth
                      onClick={() => navigate('/history')}
                    >
                      查看全部历史 →
                    </Button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </MobilePage>
    </>
  );
}

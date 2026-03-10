import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { shareApi, ShareContent } from '../api/share';
import { ShareSEO } from '../components/share/ShareSEO';
import { MobilePage } from '../components/mobile';
import { Card, CardContent, CardBadge } from '../components/mobile/Card';
import { Button } from '../components/mobile/Button';
import './SharePage.css';

export default function SharePage() {
  const { shareToken } = useParams<{ shareToken: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<ShareContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDetail, setShowDetail] = useState(false);

  useEffect(() => {
    if (!shareToken) {
      setError('分享链接无效');
      setLoading(false);
      return;
    }

    loadShareContent();
  }, [shareToken]);

  const loadShareContent = async () => {
    try {
      setLoading(true);
      const data = await shareApi.getShareContent(shareToken!);
      setContent(data);
      setError(null);
    } catch (err: any) {
      console.error('加载分享内容失败', err);
      
      if (err.response?.status === 404) {
        setError('分享不存在或已被删除');
      } else if (err.response?.status === 410) {
        setError('分享已过期');
      } else if (err.response?.status === 403) {
        setError('分享已设为私密');
      } else {
        setError('加载失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  const getOutcomeColor = (outcome: string) => {
    if (outcome.includes('吉')) return 'share-badge--success';
    if (outcome.includes('凶')) return 'share-badge--warning';
    return 'share-badge--info';
  };

  const handleTryDivination = () => {
    navigate('/divination');
  };

  if (loading) {
    return (
      <div className="share-page">
        <div className="share-loading">
          <div className="share-loading-spinner"></div>
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="share-page">
        <div className="share-error">
          <div className="share-error-icon">😔</div>
          <h2>无法加载分享内容</h2>
          <p>{error || '未知错误'}</p>
          <Button variant="primary" onClick={handleTryDivination}>
            去占卜
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="share-page">
      {/* SEO Meta Tags */}
      {content && (
        <ShareSEO
          title={content.result.title || '占卜结果'}
          description={`问题：${content.question} - ${content.result.summary.substring(0, 150)}...`}
          url={window.location.href}
        />
      )}

      {/* Header */}
      <header className="share-header">
        <div className="share-header-content">
          <h1 className="share-logo">🌿 DivineDaily</h1>
          <p className="share-tagline">每日一卦，洞察人生</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="share-main">
        <MobilePage>
          {/* Question Section */}
          <motion.div
            className="share-question"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="share-question-icon">🔮</div>
            <h2 className="share-question-title">占卜问题</h2>
            <p className="share-question-text">{content.question}</p>
          </motion.div>

          {/* Result Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card variant="elevated" size="lg">
              <div className="share-result-header">
                {content.result.outcome && (
                  <CardBadge className={getOutcomeColor(content.result.outcome)}>
                    {content.result.outcome}
                  </CardBadge>
                )}
                {content.result.title && (
                  <h2 className="share-result-title">{content.result.title}</h2>
                )}
              </div>

              {/* Cards Display */}
              {content.result.cards && content.result.cards.length > 0 && (
                <div className="share-cards">
                  {content.result.cards.map((card: any, idx: number) => (
                    <div key={idx} className="share-card-item">
                      <div className={`share-card-icon ${card.is_reversed ? 'share-card-icon--reversed' : ''}`}>
                        🎴
                      </div>
                      <div className="share-card-position">{card.position}</div>
                      <div className="share-card-name">{card.name}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Summary */}
              <CardContent>
                <div className="share-summary markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {content.result.summary}
                  </ReactMarkdown>
                </div>
              </CardContent>

              {/* Toggle Detail Button */}
              {content.result.detail && (
                <div className="share-toggle">
                  <Button
                    variant="text"
                    size="sm"
                    fullWidth
                    onClick={() => setShowDetail(!showDetail)}
                    icon={
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        {showDetail ? (
                          <polyline points="18 15 12 9 6 15"/>
                        ) : (
                          <polyline points="6 9 12 15 18 9"/>
                        )}
                      </svg>
                    }
                  >
                    {showDetail ? '收起详情' : '查看详情'}
                  </Button>
                </div>
              )}
            </Card>
          </motion.div>

          {/* Detail Section */}
          {showDetail && content.result.detail && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardContent>
                  <div className="share-detail markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {content.result.detail}
                    </ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* CTA Section */}
          <motion.div
            className="share-cta"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card variant="gradient">
              <CardContent>
                <div className="share-cta-content">
                  <h3 className="share-cta-title">想要获得你的占卜结果？</h3>
                  <p className="share-cta-text">
                    DivineDaily 结合传统易经与现代 AI，为你提供专业的占卜解读
                  </p>
                  <Button
                    variant="primary"
                    size="lg"
                    fullWidth
                    onClick={handleTryDivination}
                    icon={<span>🔮</span>}
                  >
                    立即体验
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Footer */}
          <footer className="share-footer">
            <p className="share-footer-text">
              浏览次数：{content.metadata.view_count} 次
            </p>
            <p className="share-footer-copyright">
              © 2026 DivineDaily. All rights reserved.
            </p>
          </footer>
        </MobilePage>
      </main>
    </div>
  );
}

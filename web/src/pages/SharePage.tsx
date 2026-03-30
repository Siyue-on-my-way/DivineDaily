import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { QRCodeCanvas } from 'qrcode.react';
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
  const [shareUrl, setShareUrl] = useState('');
  const [showManualCopy, setShowManualCopy] = useState(false);
  const [posterUrl, setPosterUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!shareToken) {
      setError('分享链接无效');
      setLoading(false);
      return;
    }

    setShareUrl(window.location.href);
    loadShareContent();
  }, [shareToken]);

  const loadShareContent = async () => {
    try {
      setLoading(true);
      const data = await shareApi.getShareContent(shareToken!);
      setContent(data);
      setError(null);
      shareApi.recordView(shareToken!).catch(() => undefined);
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

  const handleRetryLoad = () => {
    if (!shareToken) return;
    setError(null);
    loadShareContent();
  };

  const handleCopyLink = async () => {
    try {
      const urlToCopy = shareUrl || window.location.href;
      await navigator.clipboard.writeText(urlToCopy);
      setShowManualCopy(false);
      window.dispatchEvent(new CustomEvent('toast:success', {
        detail: { message: '链接已复制' }
      }));
    } catch (error) {
      console.error('复制链接失败', error);
      setShowManualCopy(true);
      window.dispatchEvent(new CustomEvent('toast:error', {
        detail: { message: '复制失败，请手动复制链接' }
      }));
    }
  };

  const handleCopyInputFocus = (event: React.FocusEvent<HTMLInputElement>) => {
    event.currentTarget.select();
  };

  const handleGeneratePoster = () => {
    if (!content) return;

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = 1080;
    const height = 1920;
    canvas.width = width;
    canvas.height = height;

    const background = ctx.createLinearGradient(0, 0, width, height);
    background.addColorStop(0, '#667eea');
    background.addColorStop(1, '#764ba2');
    ctx.fillStyle = background;
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 64px "PingFang SC", sans-serif';
    ctx.fillText('DivineDaily', 80, 140);

    ctx.font = '36px "PingFang SC", sans-serif';
    ctx.fillText('每日一卦，洞察人生', 80, 200);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 48px "PingFang SC", sans-serif';
    ctx.fillText('占卜问题', 80, 320);

    ctx.font = '36px "PingFang SC", sans-serif';
    const question = content.question || '';
    wrapText(ctx, question, 80, 390, width - 160, 52);

    ctx.font = 'bold 48px "PingFang SC", sans-serif';
    ctx.fillText('结果摘要', 80, 620);

    ctx.font = '34px "PingFang SC", sans-serif';
    const summary = content.result.summary || content.result.detail || '';
    wrapText(ctx, summary, 80, 690, width - 160, 48);

    ctx.fillStyle = '#ffffff';
    ctx.font = '32px "PingFang SC", sans-serif';
    ctx.fillText('扫码查看完整解读', 80, height - 260);

    const qrCanvas = document.querySelector('.share-actions-qr canvas') as HTMLCanvasElement | null;
    if (qrCanvas) {
      ctx.drawImage(qrCanvas, width - 320, height - 420, 240, 240);
    }

    const dataUrl = canvas.toDataURL('image/png');
    setPosterUrl(dataUrl);
  };

  const handleDownloadPoster = () => {
    if (!posterUrl) return;
    const link = document.createElement('a');
    link.href = posterUrl;
    link.download = `divinedaily-share-${shareToken || 'result'}.png`;
    link.click();
  };

  const wrapText = (
    context: CanvasRenderingContext2D,
    text: string,
    x: number,
    y: number,
    maxWidth: number,
    lineHeight: number
  ) => {
    const words = text.split('');
    let line = '';
    let offsetY = y;

    for (let i = 0; i < words.length; i += 1) {
      const testLine = line + words[i];
      const metrics = context.measureText(testLine);
      if (metrics.width > maxWidth && line !== '') {
        context.fillText(line, x, offsetY);
        line = words[i];
        offsetY += lineHeight;
      } else {
        line = testLine;
      }
    }
    if (line) {
      context.fillText(line, x, offsetY);
    }
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
          <div className="share-error-actions">
            <Button variant="secondary" onClick={handleRetryLoad}>
              重新加载
            </Button>
            <Button variant="primary" onClick={handleTryDivination}>
              去占卜
            </Button>
          </div>
          {shareToken && (
            <p className="share-error-token">分享编号：{shareToken}</p>
          )}
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
          description={`问题：${content.question} - ${(content.result.summary || content.result.detail || '').substring(0, 150)}${(content.result.summary || content.result.detail || '').length > 150 ? '...' : ''}`}
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

          {/* Share Actions */}
          <motion.div
            className="share-actions"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.35 }}
          >
            <Card>
              <CardContent>
                <div className="share-actions-content">
                  <h3 className="share-actions-title">分享这个结果</h3>
                  <p className="share-actions-text">复制链接发送给朋友，或继续体验你的占卜</p>
                  <div className="share-actions-grid">
                    <div className="share-actions-qr">
                      <QRCodeCanvas value={shareUrl || window.location.href} size={140} />
                      <span>扫码查看</span>
                    </div>
                    <div className="share-actions-buttons">
                      <Button variant="secondary" onClick={handleCopyLink}>
                        复制链接
                      </Button>
                      {showManualCopy && (
                        <div className="share-actions-manual">
                          <input
                            className="share-actions-input"
                            value={shareUrl || window.location.href}
                            readOnly
                            onFocus={handleCopyInputFocus}
                            onClick={handleCopyInputFocus}
                          />
                          <span>请手动复制链接</span>
                        </div>
                      )}
                      <Button variant="secondary" onClick={handleGeneratePoster}>
                        生成分享海报
                      </Button>
                      <Button variant="primary" onClick={handleTryDivination}>
                        立即体验
                      </Button>
                    </div>
                  </div>
                  {posterUrl && (
                    <div className="share-actions-poster">
                      <img src={posterUrl} alt="分享海报" />
                      <Button variant="outline" onClick={handleDownloadPoster}>
                        下载海报
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

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

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { DivinationResult, HexagramInfo, YarrowProcessTrace, YarrowLineTrace } from '../../types/divination';
import { Card, CardHeader, CardContent, CardBadge } from '../mobile/Card';
import { Button } from '../mobile/Button';
import { divinationApi } from '../../api/divination';
import { shareApi } from '../../api/share';
import { feedbackApi } from '../../api/feedback';
import { FeedbackModal, FeedbackData } from '../feedback/FeedbackModal';
import { toast } from '../../hooks/useToast';
import DailyFortuneDisplay from './DailyFortuneDisplay';
import './DivinationResultCard.css';

interface Props {
  result: DivinationResult;
}

export default function DivinationResultCard({ result }: Props) {
  const [showDetail, setShowDetail] = useState(false);
  const [saving, setSaving] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const isDailyFortune = !!result.daily_fortune;

  const isIChing = !!result.hexagram_info;

  const getOutcomeColor = (outcome: string) => {
    if (outcome.includes('吉')) return 'result-badge--success';
    if (outcome.includes('凶')) return 'result-badge--warning';
    return 'result-badge--info';
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await divinationApi.save(result.session_id);
      toast.success('保存成功');
    } catch (error) {
      console.error('Save failed', error);
      toast.error('保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  const handleShare = async () => {
    setSharing(true);
    try {
      // 使用新的分享 API
      const shareResponse = await shareApi.createShare(result.session_id, {
        expires_days: 30, // 30天过期
        is_public: true
      });
      
      const shareUrl = shareResponse.share_url;
      
      // 尝试使用 Web Share API
      if (navigator.share) {
        await navigator.share({
          title: result.title || '我的占卜结果',
          text: `问题：${result.summary.substring(0, 100)}...`,
          url: shareUrl,
        });
        toast.success('分享成功');
      } else {
        // 降级方案：复制链接
        await navigator.clipboard.writeText(shareUrl);
        toast.success('分享链接已复制到剪贴板');
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Share failed', error);
        toast.error('分享失败，请重试');
      }
    } finally {
      setSharing(false);
    }
  };

  const renderHexagramLines = (hexagram: HexagramInfo) => {
    if (!hexagram.line_values || hexagram.line_values.length !== 6) return null;

    // 自上而下展示，因此需要反转一下（line_values 是自下而上）
    const lines = [...hexagram.line_values].reverse();

    return (
      <div className="iching-lines">
        {lines.map((value, index) => {
          const isYang = value === 7 || value === 9;
          const isChanging = value === 6 || value === 9;
          return (
            <div
              key={index}
              className={[
                'iching-line',
                isYang ? 'iching-line--yang' : 'iching-line--yin',
                isChanging ? 'iching-line--changing' : '',
              ].join(' ')}
            >
              <div className="iching-line-index">第{6 - index}爻</div>
              <div className="iching-line-bar" />
            </div>
          );
        })}
      </div>
    );
  };

  const renderYarrowProcess = (trace?: YarrowProcessTrace) => {
    if (!trace || !trace.lines?.length) return null;

    const renderLine = (line: YarrowLineTrace) => (
      <details key={line.line_index} className="yarrow-line">
        <summary className="yarrow-line-summary">
          <span>第{line.line_index}爻 · {line.line_type}</span>
          {line.is_changing && <span className="yarrow-line-tag">变爻</span>}
        </summary>
        <div className="yarrow-line-body">
          <div className="yarrow-line-meta">
            <span>初始蓍草：{line.initial_stalks}</span>
            <span>最终蓍草：{line.final_stalks}</span>
            <span>爻值：{line.line_value}</span>
          </div>
          <ol className="yarrow-steps">
            {line.changes.map((step) => (
              <li key={step.step_index} className="yarrow-step">
                <div className="yarrow-step-header">
                  <span className="yarrow-step-index">第 {step.step_index} 变</span>
                  <span className="yarrow-step-stalks">
                    {step.stalks_before} → {step.stalks_after}
                  </span>
                </div>
                <div className="yarrow-step-detail">
                  <div>左手：{step.left_pile}（余 {step.left_remainder}）</div>
                  <div>右手：{step.right_pile_before_hang} 挂一 → {step.right_pile_after_hang}（余 {step.right_remainder}）</div>
                  <div>本次去除：{step.removed}</div>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </details>
    );

    return (
      <Card className="yarrow-card">
        <CardHeader title="起卦过程（大衍筮法）" />
        <CardContent>
          <div className="yarrow-intro">
            <p>下面是本次起卦的完整过程记录，你可以展开查看每一爻的三次演变。</p>
          </div>
          <div className="yarrow-lines">
            {trace.lines
              .slice() // 防御性拷贝
              .sort((a, b) => a.line_index - b.line_index)
              .map(renderLine)}
          </div>
        </CardContent>
      </Card>
    );
  };

  const handleFeedbackSubmit = async (feedbackData: FeedbackData) => {
    await feedbackApi.submitDivinationFeedback({
      session_id: result.session_id,
      feedback_type: 'accuracy',
      ...feedbackData
    });
    setFeedbackSubmitted(true);
    toast.success('感谢你的反馈！');
  };

  return (
    <div className="result-container">
      {/* 结果卡片 */}
      <Card variant="elevated" size="lg">
        <div className="result-header">
          {result.outcome && (
            <CardBadge className={getOutcomeColor(result.outcome)}>
              {result.outcome}
            </CardBadge>
          )}
          {result.title && (
            <h2 className="result-title">{result.title}</h2>
          )}
        </div>

        {/* 牌面展示 */}
        {result.cards && result.cards.length > 0 && (
          <div className="result-cards">
            {result.cards.map((card, idx) => (
              <div key={idx} className="result-card-item">
                <div className={`result-card-icon ${card.is_reversed ? 'result-card-icon--reversed' : ''}`}>
                  🎴
                </div>
                <div className="result-card-position">{card.position}</div>
                <div className="result-card-name">{card.name}</div>
              </div>
            ))}
          </div>
        )}

        {/* 摘要 */}
        <CardContent>
          <div className="result-summary markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.summary}
            </ReactMarkdown>
          </div>
        </CardContent>

        {/* 展开按钮 */}
        {result.detail && (
          <div className="result-toggle">
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

      {/* 详细解读 + 卦象/起卦过程 */}
      {showDetail && (
        <div className="result-detail animate-fadeIn">
          {isDailyFortune && result.daily_fortune ? (
            <DailyFortuneDisplay info={result.daily_fortune} />
          ) : (
            <>
              {isIChing && result.hexagram_info && (
                <Card className="iching-card">
                  <CardHeader title="卦象一览" />
                  <CardContent>
                    <div className="iching-header">
                      <div className="iching-title">
                        <div className="iching-name">{result.hexagram_info.name}</div>
                        <div className="iching-meta">
                          <span>上卦：{result.hexagram_info.upper_trigram}</span>
                          <span>下卦：{result.hexagram_info.lower_trigram}</span>
                          <span>五行：{result.hexagram_info.wuxing}</span>
                        </div>
                      </div>
                    </div>
                    {renderHexagramLines(result.hexagram_info)}
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader title="完整解读" />
                <CardContent>
                  <div className="result-detail-content markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {result.detail}
                    </ReactMarkdown>
                  </div>
                </CardContent>
              </Card>

              {renderYarrowProcess(result.yarrow_trace)}
            </>
          )}
        </div>
      )}

      {/* 反馈按钮 */}
      <div className="result-feedback-section">
        {!feedbackSubmitted ? (
          <button
            className="feedback-button"
            onClick={() => setShowFeedback(true)}
          >
            📝 评价这次占卜
          </button>
        ) : (
          <div className="feedback-thanks">
            ✅ 感谢你的反馈！
          </div>
        )}
      </div>

      {/* 操作按钮 */}
      <div className="result-actions">
        <Button 
          variant="outline" 
          size="md" 
          icon={<span>💾</span>}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? '保存中...' : '保存'}
        </Button>
        <Button 
          variant="outline" 
          size="md" 
          icon={<span>📤</span>}
          onClick={handleShare}
          disabled={sharing}
        >
          {sharing ? '分享中...' : '分享'}
        </Button>
      </div>

      {/* 反馈弹窗 */}
      <FeedbackModal
        isOpen={showFeedback}
        onClose={() => setShowFeedback(false)}
        sessionId={result.session_id}
        feedbackType="accuracy"
        onSubmit={handleFeedbackSubmit}
      />
    </div>
  );
}

import { useState } from 'react';
import type { DivinationResult } from '../../types/divination';
import { Card, CardHeader, CardContent, CardBadge } from '../mobile/Card';
import { Button } from '../mobile/Button';
import { divinationApi } from '../../api/divination';
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
  const isDailyFortune = !!result.daily_fortune;

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
      const { share_url } = await divinationApi.share(result.session_id);
      
      // 尝试使用 Web Share API
      if (navigator.share) {
        await navigator.share({
          title: result.title || '占卜结果',
          text: result.summary,
          url: share_url,
        });
        toast.success('分享成功');
      } else {
        // 降级方案：复制链接
        await navigator.clipboard.writeText(share_url);
        toast.success('链接已复制到剪贴板');
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
          <div className="result-summary">
            {result.summary}
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

      {/* 详细解读 */}
      {showDetail && (
        <div className="result-detail animate-fadeIn">
          {isDailyFortune && result.daily_fortune ? (
            <DailyFortuneDisplay info={result.daily_fortune} />
          ) : (
            <Card>
              <CardHeader title="完整解读" />
              <CardContent>
                <div className="result-detail-content">
                  {result.detail}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

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
    </div>
  );
}

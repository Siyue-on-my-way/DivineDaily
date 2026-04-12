import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MobilePage } from '../components/mobile';
import { Button } from '../components/mobile/Button';
import DivinationResultCard from '../components/divination/DivinationResultCard';
import { divinationApi } from '../api/divination';
import type { DivinationResult } from '../types/divination';

export default function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<DivinationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const [processingElapsed, setProcessingElapsed] = useState(0);

  const loadDetail = useCallback(async () => {
    if (!id) {
      setError('缺少历史记录 ID');
      setLoading(false);
      return null;
    }

    try {
      const detail = await divinationApi.getDetail(id);
      setResult(detail);
      setError(null);
      return detail;
    } catch (err: any) {
      setError(err?.response?.data?.detail || '加载历史详情失败');
      return null;
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    let pollingTimer: ReturnType<typeof setTimeout> | null = null;
    let elapsedTimer: ReturnType<typeof setInterval> | null = null;
    let isUnmounted = false;

    const loadAndMaybePoll = async () => {
      const detail = await loadDetail();
      if (isUnmounted) return;

      if (detail?.status === 'processing') {
        pollingTimer = setTimeout(loadAndMaybePoll, 1500);
      }
    };

    setLoading(true);
    setError(null);
    setProcessingElapsed(0);

    elapsedTimer = setInterval(() => {
      setProcessingElapsed((prev) => prev + 1);
    }, 1000);

    loadAndMaybePoll();

    return () => {
      isUnmounted = true;
      if (pollingTimer) clearTimeout(pollingTimer);
      if (elapsedTimer) clearInterval(elapsedTimer);
    };
  }, [loadDetail]);

  const handleRetry = async () => {
    setIsRetrying(true);
    setError(null);
    await loadDetail();
    setIsRetrying(false);
  };

  const isProcessing = result?.status === 'processing';

  return (
    <MobilePage>
      <div style={{ padding: 'var(--spacing-md)' }}>
        <Button
          variant="text"
          size="sm"
          onClick={() => navigate('/history')}
          icon={
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          }
        >
          返回历史
        </Button>

        {loading && !result && <div style={{ marginTop: 16 }}>加载中...</div>}

        {isProcessing && (
          <div
            style={{
              marginTop: 12,
              marginBottom: 12,
              padding: '12px 14px',
              borderRadius: 10,
              background: 'rgba(59,130,246,0.08)',
              color: '#1d4ed8',
              fontSize: 14,
              lineHeight: 1.5,
            }}
          >
            占卜仍在处理中，正在为你同步最新结果…（已等待 {processingElapsed}s）
          </div>
        )}

        {error && !loading && !result && (
          <div style={{ marginTop: 16 }}>
            <div style={{ marginBottom: 12 }}>{error}</div>
            <div style={{ display: 'flex', gap: 8 }}>
              <Button variant="secondary" onClick={() => navigate('/history')}>
                返回历史
              </Button>
              <Button variant="primary" onClick={handleRetry} loading={isRetrying}>
                再试一次
              </Button>
            </div>
          </div>
        )}

        {error && result && (
          <div
            style={{
              marginTop: 12,
              marginBottom: 12,
              padding: '10px 12px',
              borderRadius: 8,
              background: 'rgba(245,158,11,0.12)',
              color: '#92400e',
              fontSize: 13,
            }}
          >
            最新刷新失败：{error}
          </div>
        )}

        {result && (
          <>
            {isRetrying && (
              <div style={{ marginTop: 12, marginBottom: 8, fontSize: 13, color: '#6b7280' }}>
                正在刷新详情...
              </div>
            )}
            <DivinationResultCard result={result} />
          </>
        )}
      </div>
    </MobilePage>
  );
}

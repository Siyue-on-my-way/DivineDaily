import { useState, useEffect, useCallback } from 'react';
import { MobilePage } from '../components/mobile';
import { Button } from '../components/mobile/Button';
import { Card, CardHeader, CardContent, CardBadge } from '../components/mobile/Card';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/AuthContext';
import { divinationApi } from '../api/divination';
import { useRefresh } from '../hooks/useRefresh';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';
import './HistoryPage.css';

interface HistoryItem {
  id: string;
  question: string;
  type: string;
  time: string;
  outcome: string;
  version: string;
  status: string;
}

// 格式化事件类型为中文显示
const formatEventType = (eventType: string | null, version: string, spread?: string | null): string => {
  if (version === 'TAROT') {
    if (spread === 'single') return '塔罗牌·单张';
    if (spread === 'three') return '塔罗牌·三张牌阵';
    if (spread === 'cross') return '塔罗牌·十字牌阵';
    return '塔罗占卜';
  }
  
  const typeMap: Record<string, string> = {
    'career': '事业决策',
    'relationship': '感情问题',
    'decision': '决策咨询',
    'health': '健康问题',
    'wealth': '财运问题',
    'fortune': '每日运势',
    'knowledge': '知识问答',
  };
  
  return typeMap[eventType || ''] || '周易占卜';
};

// 格式化时间为相对时间
const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays === 1) return '昨天';
  if (diffDays < 7) return `${diffDays}天前`;
  
  // 超过7天显示具体日期
  return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
};

// 格式化结果显示
const formatOutcome = (outcome: string | null | undefined): string => {
  if (!outcome) return '平';
  return outcome;
};

/**
 * 历史记录页面
 * 
 * 功能：
 * - 展示用户的占卜历史记录
 * - 支持下拉刷新
 * - 支持无限滚动加载更多
 * - 支持筛选和搜索（待实现）
 */
export default function HistoryPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  
  const PAGE_SIZE = 20;

  /**
   * 加载历史记录
   */
  const loadHistory = useCallback(async (reset: boolean = false) => {
    try {
      if (reset) {
        setLoading(true);
        setPage(0);
      }
      
      setError(null);

      const currentPage = reset ? 0 : page;
      const offset = currentPage * PAGE_SIZE;

      // 调用真实 API
      const response = await divinationApi.getHistory({
        limit: PAGE_SIZE,
        page: currentPage,
      });
      
      // 转换数据格式
      const formattedHistory: HistoryItem[] = response.sessions.map((session: any) => ({
        id: session.id,
        question: session.question,
        type: formatEventType(session.event_type, session.version, session.spread),
        time: formatTime(session.created_at),
        outcome: formatOutcome(session.outcome),
        version: session.version,
        status: session.status,
      }));
      
      if (reset) {
        setHistory(formattedHistory);
      } else {
        setHistory(prev => [...prev, ...formattedHistory]);
      }
      
      // 检查是否还有更多数据
      setHasMore(response.has_more);
      
      if (!reset) {
        setPage(prev => prev + 1);
      }
    } catch (err: any) {
      console.error('加载历史记录失败:', err);
      setError(err.response?.data?.detail || '加载失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, [page]);

  /**
   * 加载更多数据
   */
  const loadMore = useCallback(async () => {
    if (!hasMore || loading) return;
    await loadHistory(false);
  }, [hasMore, loading, loadHistory]);

  /**
   * 刷新数据
   */
  const handleRefresh = useCallback(async () => {
    await loadHistory(true);
  }, [loadHistory]);

  // 初始加载
  useEffect(() => {
    loadHistory(true);
  }, [user]);

  // 下拉刷新
  const { refreshState, pullDistance, bind } = useRefresh({
    onRefresh: handleRefresh,
  });

  // 无限滚动
  const { loading: loadingMore, observerRef } = useInfiniteScroll({
    onLoadMore: loadMore,
    hasMore,
  });

  // 加载状态
  if (loading && history.length === 0) {
    return (
      <MobilePage>
        <div className="history-container">
          <h2 className="history-title">占卜历史</h2>
          <div className="history-loading">
            <div className="loading-spinner"></div>
            <p>加载中...</p>
          </div>
        </div>
      </MobilePage>
    );
  }

  // 错误状态
  if (error && history.length === 0) {
    return (
      <MobilePage>
        <div className="history-container">
          <h2 className="history-title">占卜历史</h2>
          <div className="history-error">
            <div className="error-icon">⚠️</div>
            <p>{error}</p>
            <Button variant="primary" onClick={() => loadHistory(true)}>
              重试
            </Button>
          </div>
        </div>
      </MobilePage>
    );
  }

  return (
    <MobilePage>
      <div className="history-container" {...bind()}>
        {/* 下拉刷新指示器 */}
        {refreshState !== 'idle' && (
          <div 
            className={`refresh-indicator refresh-indicator--${refreshState}`}
            style={{ transform: `translateY(${Math.min(pullDistance, 80)}px)` }}
          >
            {refreshState === 'pulling' && <span>下拉刷新</span>}
            {refreshState === 'ready' && <span>松开刷新</span>}
            {refreshState === 'refreshing' && (
              <>
                <div className="loading-spinner-small"></div>
                <span>刷新中...</span>
              </>
            )}
          </div>
        )}

        <h2 className="history-title">占卜历史</h2>
        
        {history.length === 0 ? (
          <div className="history-empty">
            <div className="history-empty-icon">📜</div>
            <p>暂无占卜记录</p>
            <Button variant="primary" onClick={() => navigate('/divination')}>
              开始占卜
            </Button>
          </div>
        ) : (
          <>
            <div className="history-list">
              {history.map((item) => (
                <Card key={item.id} clickable onClick={() => navigate(`/history/${item.id}`)}>
                  <CardHeader
                    title={item.question}
                    subtitle={item.time}
                    icon="🔮"
                  />
                  <CardContent>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <CardBadge>{item.type}</CardBadge>
                      <CardBadge className={`result-badge--${item.outcome === '吉' ? 'success' : item.outcome === '凶' ? 'danger' : 'info'}`}>
                        {item.outcome}
                      </CardBadge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 无限滚动加载指示器 */}
            <div ref={observerRef} className="load-more-indicator">
              {loadingMore && (
                <div className="loading-more">
                  <div className="loading-spinner-small"></div>
                  <span>加载中...</span>
                </div>
              )}
              {!hasMore && history.length > 0 && (
                <div className="no-more">
                  <span>没有更多了</span>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </MobilePage>
  );
}

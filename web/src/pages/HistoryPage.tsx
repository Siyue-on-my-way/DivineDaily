import { useState, useEffect } from 'react';
import { MobilePage } from '../components/mobile';
import { Button } from '../components/mobile/Button';
import { Card, CardHeader, CardContent, CardBadge } from '../components/mobile/Card';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/AuthContext';
import { divinationApi } from '../api/divination';
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

export default function HistoryPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, [user]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      // 调用真实 API
      const response = await divinationApi.getHistory({
        limit: 50,
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
      
      setHistory(formattedHistory);
    } catch (err: any) {
      console.error('加载历史记录失败:', err);
      setError(err.response?.data?.detail || '加载失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 加载状态
  if (loading) {
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
  if (error) {
    return (
      <MobilePage>
        <div className="history-container">
          <h2 className="history-title">占卜历史</h2>
          <div className="history-error">
            <div className="error-icon">⚠️</div>
            <p>{error}</p>
            <Button variant="primary" onClick={loadHistory}>
              重试
            </Button>
          </div>
        </div>
      </MobilePage>
    );
  }

  return (
    <MobilePage>
      <div className="history-container">
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
        )}
        </div>
    </MobilePage>
  );
}

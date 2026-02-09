import { MobilePage } from '../components/mobile';
import { Button } from '../components/mobile/Button';
import { Card, CardHeader, CardContent, CardBadge } from '../components/mobile/Card';
import { useNavigate } from 'react-router-dom';
import './HistoryPage.css';

export default function HistoryPage() {
  const navigate = useNavigate();

  // TODO: 从 API 获取真实数据
  const mockHistory = [
    {
      id: '1',
      question: '转介绍会成功吗？',
      type: '塔罗牌·三张牌阵',
      time: '2小时前',
      outcome: '吉',
    },
    {
      id: '2',
      question: '今天运势如何',
      type: '每日运势',
      time: '昨天',
      outcome: '平',
    },
  ];

  return (
    <MobilePage>
      <div className="history-container">
        <h2 className="history-title">占卜历史</h2>
        
        {mockHistory.length === 0 ? (
          <div className="history-empty">
            <div className="history-empty-icon">📜</div>
            <p>暂无占卜记录</p>
            <Button variant="primary" onClick={() => navigate('/divination')}>
              开始占卜
            </Button>
      </div>
        ) : (
      <div className="history-list">
            {mockHistory.map((item) => (
              <Card key={item.id} clickable onClick={() => navigate(`/history/${item.id}`)}>
            <CardHeader
              title={item.question}
                  subtitle={item.time}
                  icon="🔮"
                />
                <CardContent>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <CardBadge>{item.type}</CardBadge>
                    <CardBadge className={`result-badge--${item.outcome === '吉' ? 'success' : 'info'}`}>
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

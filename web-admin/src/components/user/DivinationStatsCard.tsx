import './DivinationStatsCard.css';

interface DivinationStatsCardProps {
  totalCount: number;
  ichingCount: number;
  tarotCount: number;
  fortuneCount: number;
}

export default function DivinationStatsCard({
  totalCount,
  ichingCount,
  tarotCount,
  fortuneCount,
}: DivinationStatsCardProps) {
  return (
    <div className="divination-stats-card">
      <div className="card-header">
        <h2>占卜统计</h2>
      </div>
      <div className="card-body">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-icon total">📊</div>
            <div className="stat-label">总次数</div>
            <div className="stat-value">{totalCount}</div>
          </div>
          <div className="stat-item">
            <div className="stat-icon iching">☯️</div>
            <div className="stat-label">易经卦象</div>
            <div className="stat-value">{ichingCount}</div>
          </div>
          <div className="stat-item">
            <div className="stat-icon tarot">🃏</div>
            <div className="stat-label">塔罗牌</div>
            <div className="stat-value">{tarotCount}</div>
          </div>
          <div className="stat-item">
            <div className="stat-icon fortune">🔮</div>
            <div className="stat-label">运势</div>
            <div className="stat-value">{fortuneCount}</div>
          </div>
        </div>
      </div>
    </div>
  );
}


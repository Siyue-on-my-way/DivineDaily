import { Link } from 'react-router-dom';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const cards = [
    {
      title: 'LLM 配置',
      description: '管理 LLM 模型配置，包括 API 密钥、端点等',
      icon: '🤖',
      link: '/admin/llm-config',
      color: '#4CAF50',
    },
    {
      title: 'Assistant 配置',
      description: '管理 AI Assistant，包括占卜、塔罗等场景的智能助手',
      icon: '📝',
      link: '/admin/prompt-config',
      color: '#2196F3',
    },
    {
      title: '用户管理',
      description: '管理用户账号、权限等（即将推出）',
      icon: '👥',
      link: '#',
      color: '#FF9800',
      disabled: true,
    },
    {
      title: '系统设置',
      description: '系统配置、日志查看等（即将推出）',
      icon: '⚙️',
      link: '#',
      color: '#9C27B0',
      disabled: true,
    },
  ];

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>管理首页</h1>
        <p>欢迎使用 Divine Daily 管理后台</p>
      </div>

      <div className="dashboard-cards">
        {cards.map((card) => (
          <Link
            key={card.title}
            to={card.link}
            className={`dashboard-card ${card.disabled ? 'disabled' : ''}`}
            style={{ borderTopColor: card.color }}
            onClick={(e) => card.disabled && e.preventDefault()}
          >
            <div className="card-icon" style={{ color: card.color }}>
              {card.icon}
            </div>
            <h3 className="card-title">{card.title}</h3>
            <p className="card-description">{card.description}</p>
            {card.disabled && (
              <span className="card-badge">即将推出</span>
            )}
          </Link>
        ))}
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-value">2</div>
          <div className="stat-label">LLM 配置</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">4</div>
          <div className="stat-label">Assistant 配置</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">-</div>
          <div className="stat-label">活跃用户</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">-</div>
          <div className="stat-label">今日占卜</div>
        </div>
      </div>
    </div>
  );
}

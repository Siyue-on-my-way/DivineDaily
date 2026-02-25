import { UserStats } from '../../types/user';
import './UserStatsCard.css';

interface UserStatsCardProps {
  stats: UserStats | null;
  loading?: boolean;
}

export default function UserStatsCard({ stats, loading = false }: UserStatsCardProps) {
  if (loading) {
    return (
      <div className="user-stats-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const statsData = [
    {
      label: '总用户数',
      value: stats.total_users,
      icon: '👥',
      color: '#2196F3',
      trend: `今日新增 ${stats.today_new_users}`,
    },
    {
      label: '管理员',
      value: stats.admin_users,
      icon: '👑',
      color: '#FF9800',
      trend: `普通用户 ${stats.normal_users}`,
    },
    {
      label: '活跃用户',
      value: stats.active_users,
      icon: '✨',
      color: '#4CAF50',
      trend: `7天活跃 ${stats.active_7days}`,
    },
    {
      label: '禁用用户',
      value: stats.disabled_users,
      icon: '🚫',
      color: '#F44336',
      trend: `占比 ${stats.total_users > 0 ? ((stats.disabled_users / stats.total_users) * 100).toFixed(1) : 0}%`,
    },
  ];

  return (
    <div className="user-stats-container">
      {statsData.map((stat, index) => (
        <div key={index} className="stat-card" style={{ borderTopColor: stat.color }}>
          <div className="stat-icon" style={{ color: stat.color }}>
            {stat.icon}
          </div>
          <div className="stat-content">
            <div className="stat-label">{stat.label}</div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-trend">{stat.trend}</div>
          </div>
        </div>
      ))}
    </div>
  );
}


import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import type { DivinationResult } from '../../types/divination';
import './HistoryFilter.css';

interface TimelineGroup {
  date: string;
  items: DivinationResult[];
}

interface Props {
  groups: TimelineGroup[];
}

export default function HistoryTimeline({ groups }: Props) {
  const navigate = useNavigate();

  const getOutcomeBadgeClass = (outcome: string) => {
    if (outcome.includes('吉')) return 'history-timeline-item__badge--success';
    if (outcome.includes('凶')) return 'history-timeline-item__badge--warning';
    return 'history-timeline-item__badge--info';
  };

  const getTypeIcon = (type: string) => {
    if (type.includes('塔罗')) return '🎴';
    if (type.includes('运势')) return '⭐';
    return '☯';
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));

    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  };

  if (groups.length === 0) {
    return (
      <div className="history-empty">
        <div className="history-empty__icon">📜</div>
        <div className="history-empty__text">暂无占卜记录</div>
      </div>
    );
  }

  return (
    <div className="history-timeline">
      {groups.map((group, groupIndex) => (
        <motion.div
          key={group.date}
          className="history-timeline-group"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: groupIndex * 0.1 }}
        >
          <div className="history-timeline-group__date">{group.date}</div>
          <div className="history-timeline-group__items">
            {group.items.map((item, itemIndex) => (
              <motion.div
                key={item.session_id}
                className="history-timeline-item"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: (groupIndex * 0.1) + (itemIndex * 0.05) }}
                onClick={() => navigate(`/history/${item.session_id}`)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="history-timeline-item__header">
                  <h3 className="history-timeline-item__title">
                    {item.title || '占卜记录'}
                  </h3>
                  {item.outcome && (
                    <span
                      className={`history-timeline-item__badge ${getOutcomeBadgeClass(
                        item.outcome
                      )}`}
                    >
                      {item.outcome}
                    </span>
                  )}
                </div>
                <div className="history-timeline-item__meta">
                  <div className="history-timeline-item__type">
                    <span>{getTypeIcon(item.title || '')}</span>
                    <span>{item.title?.split('·')[0] || '占卜'}</span>
                  </div>
                  <div className="history-timeline-item__time">
                    <span>🕐</span>
                    <span>{formatTime(item.created_at)}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  );
}

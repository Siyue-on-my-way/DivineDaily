import { useState } from 'react';
import './UserFilterPanel.css';

interface UserFilterPanelProps {
  onFilter: (filters: {
    role?: string;
    status?: number;
    startDate?: string;
    endDate?: string;
  }) => void;
  onReset: () => void;
}

export default function UserFilterPanel({ onFilter, onReset }: UserFilterPanelProps) {
  const [role, setRole] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleApply = () => {
    onFilter({
      role: role || undefined,
      status: status ? parseInt(status) : undefined,
      startDate: startDate || undefined,
      endDate: endDate || undefined,
    });
  };

  const handleReset = () => {
    setRole('');
    setStatus('');
    setStartDate('');
    setEndDate('');
    onReset();
  };

  const hasFilters = role || status || startDate || endDate;

  return (
    <div className="user-filter-panel">
      <div className="filter-header" onClick={() => setIsExpanded(!isExpanded)}>
        <span className="filter-title">
          🔍 高级筛选 {hasFilters && <span className="filter-badge">已筛选</span>}
        </span>
        <span className="filter-toggle">{isExpanded ? '▲' : '▼'}</span>
      </div>

      {isExpanded && (
        <div className="filter-content">
          <div className="filter-row">
            <div className="filter-item">
              <label>角色</label>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="">全部</option>
                <option value="admin">管理员</option>
                <option value="normal">普通用户</option>
              </select>
            </div>

            <div className="filter-item">
              <label>状态</label>
              <select value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="">全部</option>
                <option value="1">正常</option>
                <option value="0">禁用</option>
              </select>
            </div>

            <div className="filter-item">
              <label>注册开始时间</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="filter-item">
              <label>注册结束时间</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          <div className="filter-actions">
            <button className="filter-btn apply-btn" onClick={handleApply}>
              应用筛选
            </button>
            <button className="filter-btn reset-btn" onClick={handleReset}>
              重置
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


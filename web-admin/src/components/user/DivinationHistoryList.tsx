import { useState } from 'react';
import { UserDivination } from '../../types/user';
import './DivinationHistoryList.css';

interface DivinationHistoryListProps {
  divinations: UserDivination[];
  loading: boolean;
  total: number;
  currentPage: number;
  pageSize: number;
  filterType: string;
  searchKeyword: string;
  onPageChange: (page: number) => void;
  onFilterChange: (type: string) => void;
  onSearch: (keyword: string) => void;
  onViewDetail: (divination: UserDivination) => void;
}

export default function DivinationHistoryList({
  divinations,
  loading,
  total,
  currentPage,
  pageSize,
  filterType,
  searchKeyword,
  onPageChange,
  onFilterChange,
  onSearch,
  onViewDetail,
}: DivinationHistoryListProps) {
  const [searchInput, setSearchInput] = useState(searchKeyword);

  const getTypeIcon = (version: string) => {
    if (version.includes('iching') || version.includes('易经')) return '☯️';
    if (version.includes('tarot') || version.includes('塔罗')) return '🃏';
    if (version.includes('fortune') || version.includes('运势')) return '🔮';
    return '📖';
  };

  const getTypeName = (version: string) => {
    if (version.includes('iching') || version.includes('易经')) return '易经占卜';
    if (version.includes('tarot') || version.includes('塔罗')) return '塔罗占卜';
    if (version.includes('fortune') || version.includes('运势')) return '运势占卜';
    return '占卜';
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { text: string; className: string }> = {
      completed: { text: '已完成', className: 'completed' },
      pending: { text: '进行中', className: 'pending' },
      failed: { text: '失败', className: 'failed' },
    };
    const statusInfo = statusMap[status] || { text: status, className: 'unknown' };
    return <span className={`status-badge ${statusInfo.className}`}>{statusInfo.text}</span>;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchInput);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="divination-history-list">
      <div className="card-header">
        <h2>占卜历史记录</h2>
        <span className="total-count">共 {total} 条记录</span>
      </div>

      <div className="filter-bar">
        <div className="filter-tabs">
          <button
            className={`filter-tab ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => onFilterChange('all')}
          >
            全部
          </button>
          <button
            className={`filter-tab ${filterType === 'iching' ? 'active' : ''}`}
            onClick={() => onFilterChange('iching')}
          >
            易经
          </button>
          <button
            className={`filter-tab ${filterType === 'tarot' ? 'active' : ''}`}
            onClick={() => onFilterChange('tarot')}
          >
            塔罗
          </button>
          <button
            className={`filter-tab ${filterType === 'fortune' ? 'active' : ''}`}
            onClick={() => onFilterChange('fortune')}
          >
            运势
          </button>
        </div>
        <form className="search-form" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            placeholder="搜索问题..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button type="submit">搜索</button>
        </form>
      </div>

      <div className="history-list">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : divinations.length === 0 ? (
          <div className="empty">暂无占卜记录</div>
        ) : (
          divinations.map((divination) => (
            <div key={divination.id} className="history-item">
              <div className="item-header">
                <div className="item-meta">
                  <span className="item-icon">{getTypeIcon(divination.version)}</span>
                  <span className="item-date">📅 {formatDate(divination.created_at)}</span>
                  <span className="item-type">{getTypeName(divination.version)}</span>
                  {getStatusBadge(divination.status)}
                </div>
              </div>
              <div className="item-body">
                <div className="item-question">
                  <strong>问题:</strong> {divination.question}
                </div>
                {divination.event_type && (
                  <div className="item-event-type">
                    <strong>事件类型:</strong> {divination.event_type}
                  </div>
                )}
                {divination.result_summary && (
                  <div className="item-summary">
                    <strong>结果摘要:</strong> {divination.result_summary}
                  </div>
                )}
              </div>
              <div className="item-footer">
                <button 
                  className="view-detail-btn"
                  onClick={() => onViewDetail(divination)}
                >
                  查看详情
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="page-btn"
            disabled={currentPage === 1}
            onClick={() => onPageChange(currentPage - 1)}
          >
            上一页
          </button>
          <span className="page-info">
            第 {currentPage} / {totalPages} 页
          </span>
          <button
            className="page-btn"
            disabled={currentPage === totalPages}
            onClick={() => onPageChange(currentPage + 1)}
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
}


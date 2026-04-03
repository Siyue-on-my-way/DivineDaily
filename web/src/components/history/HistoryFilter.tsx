import './HistoryFilter.css';

interface FilterOption {
  id: string;
  label: string;
  icon?: string;
}

interface Props {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  activeFilter: string;
  onFilterChange: (filter: string) => void;
}

const FILTER_OPTIONS: FilterOption[] = [
  { id: 'all', label: '全部', icon: '📋' },
  { id: 'week', label: '本周', icon: '📅' },
  { id: 'month', label: '本月', icon: '🗓️' },
  { id: 'divination', label: '周易', icon: '☯' },
  { id: 'tarot', label: '塔罗', icon: '🎴' },
  { id: 'fortune', label: '运势', icon: '⭐' },
  { id: 'saved', label: '收藏', icon: '❤️' }
];

export default function HistoryFilter({
  searchQuery,
  onSearchChange,
  activeFilter,
  onFilterChange
}: Props) {
  return (
    <div>
      {/* 搜索栏 */}
      <div className="history-search">
        <div className="history-search__wrapper">
          <div className="history-search__icon">🔍</div>
          <input
            type="text"
            className="history-search__input"
            placeholder="搜索问题、日期或结果..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
      </div>

      {/* 筛选 Chips */}
      <div className="history-filters">
        {FILTER_OPTIONS.map((option) => (
          <button
            key={option.id}
            className={`history-filter-chip ${
              activeFilter === option.id ? 'history-filter-chip--active' : ''
            }`}
            onClick={() => onFilterChange(option.id)}
          >
            {option.icon && (
              <span className="history-filter-chip__icon">{option.icon}</span>
            )}
            <span>{option.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

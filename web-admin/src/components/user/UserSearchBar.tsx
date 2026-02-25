import { useState } from 'react';
import './UserSearchBar.css';

interface UserSearchBarProps {
  onSearch: (keyword: string) => void;
  onExport?: () => void;
  onCreate?: () => void;
}

export default function UserSearchBar({ onSearch, onExport, onCreate }: UserSearchBarProps) {
  const [keyword, setKeyword] = useState('');

  const handleSearch = () => {
    onSearch(keyword);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="user-search-bar">
      <div className="search-input-group">
        <input
          type="text"
          className="search-input"
          placeholder="搜索用户名、邮箱、手机号..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="search-btn" onClick={handleSearch}>
          🔍 搜索
        </button>
      </div>
      
      <div className="search-actions">
        {onCreate && (
          <button className="action-btn create-btn" onClick={onCreate}>
            ➕ 新建用户
          </button>
        )}
        {onExport && (
          <button className="action-btn export-btn" onClick={onExport}>
            📥 导出
          </button>
        )}
      </div>
    </div>
  );
}


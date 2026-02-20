import React from 'react';
import { useAuth } from '../../lib/AuthContext';
import './TopBar.css';

export const TopBar: React.FC = () => {
  const { isAuthenticated, user, logout, setShowLoginModal } = useAuth();
  const [showUserMenu, setShowUserMenu] = React.useState(false);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
  };

  return (
    <header className="topbar">
      <div className="topbar__left">
        <h1 className="topbar__title">Divine Daily</h1>
        <span className="topbar__subtitle">让占卜更智能</span>
      </div>

      <div className="topbar__right">
        {/* 通知按钮 */}
        <button className="topbar__icon-btn" aria-label="通知">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </button>

        {/* 用户菜单 */}
        {isAuthenticated ? (
          <div className="topbar__user-menu">
            <button 
              className="topbar__user-btn"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              <div className="topbar__user-avatar">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="topbar__user-name">{user?.username || '用户'}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>

            {showUserMenu && (
              <div className="topbar__dropdown">
                <div className="topbar__dropdown-header">
                  <div className="topbar__dropdown-name">{user?.username}</div>
                  <div className="topbar__dropdown-email">{user?.email || '未设置邮箱'}</div>
                </div>
                <div className="topbar__dropdown-divider" />
                <button className="topbar__dropdown-item" onClick={handleLogout}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16 17 21 12 16 7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                  </svg>
                  退出登录
                </button>
              </div>
            )}
          </div>
        ) : (
          <button 
            className="topbar__login-btn"
            onClick={() => setShowLoginModal(true)}
          >
            登录
          </button>
        )}
      </div>
    </header>
  );
};


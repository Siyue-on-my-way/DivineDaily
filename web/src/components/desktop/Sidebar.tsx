import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../lib/AuthContext';
import './Sidebar.css';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();

  const navItems = [
    {
      id: 'home',
      label: '首页',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      ),
      path: '/',
    },
    {
      id: 'divination',
      label: '周易占卜',
      icon: <span style={{ fontSize: '24px' }}>🔮</span>,
      path: '/divination',
    },
    {
      id: 'tarot',
      label: '塔罗牌',
      icon: <span style={{ fontSize: '24px' }}>🎴</span>,
      path: '/tarot',
    },
    {
      id: 'history',
      label: '历史记录',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
      ),
      path: '/history',
    },
    {
      id: 'profile',
      label: '个人中心',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      ),
      path: '/profile',
    },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <aside className={`sidebar ${collapsed ? 'sidebar--collapsed' : ''}`}>
      <div className="sidebar__header">
        {!collapsed && (
          <div className="sidebar__logo">
            <span className="sidebar__logo-icon">🌿</span>
            <span className="sidebar__logo-text">Divine Daily</span>
          </div>
        )}
        <button 
          className="sidebar__toggle"
          onClick={onToggle}
          aria-label={collapsed ? '展开侧边栏' : '收起侧边栏'}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
      </div>

      <nav className="sidebar__nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar__nav-item ${isActive(item.path) ? 'sidebar__nav-item--active' : ''}`}
            onClick={() => navigate(item.path)}
            title={collapsed ? item.label : undefined}
          >
            <span className="sidebar__nav-icon">{item.icon}</span>
            {!collapsed && <span className="sidebar__nav-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      {!collapsed && isAuthenticated && (
        <div className="sidebar__user">
          <div className="sidebar__user-avatar">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="sidebar__user-info">
            <div className="sidebar__user-name">{user?.username || '用户'}</div>
            <div className="sidebar__user-role">
              {user?.role === 'admin' ? '管理员' : '普通用户'}
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};


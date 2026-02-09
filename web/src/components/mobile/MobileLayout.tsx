import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { MobileHeader } from './MobileHeader';
import { MobileFooter } from './MobileFooter';
import './MobileLayout.css';

interface MobileLayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
  showFooter?: boolean;
  headerProps?: React.ComponentProps<typeof MobileHeader>;
}

export const MobileLayout: React.FC<MobileLayoutProps> = ({
  children,
  showHeader = true,
  showFooter = true,
  headerProps
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  // 默认导航项配置
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
    },
    {
      id: 'divination',
      label: '占卜',
      icon: <span style={{ fontSize: '20px' }}>🔮</span>,
    },
    {
      id: 'tarot',
      label: '塔罗',
      icon: <span style={{ fontSize: '20px' }}>🎴</span>,
    },
    {
      id: 'profile',
      label: '我的',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      ),
    },
  ];

  // 根据当前路径确定激活的导航项
  const getActiveId = () => {
    const path = location.pathname;
    if (path === '/') return 'home';
    if (path.startsWith('/divination')) return 'divination';
    if (path.startsWith('/tarot')) return 'tarot';
    if (path.startsWith('/profile')) return 'profile';
    return 'home';
  };

  const handleNavClick = (id: string) => {
    const routes: Record<string, string> = {
      home: '/',
      divination: '/divination',
      tarot: '/tarot',
      profile: '/profile',
    };
    navigate(routes[id] || '/');
  };

  return (
    <div className="mobile-layout">
      {showHeader && <MobileHeader {...headerProps} />}
      
      <main className={`mobile-layout__content ${!showHeader ? 'mobile-layout__content--no-header' : ''} ${!showFooter ? 'mobile-layout__content--no-footer' : ''}`}>
        {children}
      </main>
      
      {showFooter && (
        <MobileFooter 
          items={navItems}
          activeId={getActiveId()}
          onItemClick={handleNavClick}
        />
      )}
    </div>
  );
};

interface MobilePageProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  fullWidth?: boolean;
  centered?: boolean;
  loading?: boolean;
  empty?: boolean;
  emptyIcon?: React.ReactNode;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: React.ReactNode;
}

export const MobilePage: React.FC<MobilePageProps> = ({
  children,
  title,
  subtitle,
  fullWidth = false,
  centered = false,
  loading = false,
  empty = false,
  emptyIcon,
  emptyTitle = '暂无内容',
  emptyDescription,
  emptyAction
}) => {
  const pageClasses = [
    'mobile-page',
    fullWidth && 'mobile-page--full',
    centered && 'mobile-page--centered'
  ].filter(Boolean).join(' ');

  if (loading) {
    return (
      <div className={pageClasses}>
        <div className="mobile-page__loading">
          <div className="mobile-page__loading-spinner" />
          <span className="mobile-page__loading-text">加载中...</span>
        </div>
      </div>
    );
  }

  if (empty) {
    return (
      <div className={pageClasses}>
        <div className="mobile-page__empty">
          {emptyIcon && <div className="mobile-page__empty-icon">{emptyIcon}</div>}
          <h3 className="mobile-page__empty-title">{emptyTitle}</h3>
          {emptyDescription && (
            <p className="mobile-page__empty-description">{emptyDescription}</p>
          )}
          {emptyAction}
        </div>
      </div>
    );
  }

  return (
    <div className={pageClasses}>
      {title && <h1 className="mobile-page__title">{title}</h1>}
      {subtitle && <p className="mobile-page__subtitle">{subtitle}</p>}
      {children}
    </div>
  );
};

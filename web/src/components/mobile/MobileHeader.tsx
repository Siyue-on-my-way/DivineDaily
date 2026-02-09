import React from 'react';
import './MobileHeader.css';

interface MobileHeaderProps {
  title?: string;
  onMenuClick?: () => void;
  onNotificationClick?: () => void;
  onAvatarClick?: () => void;
  showNotificationBadge?: boolean;
  avatarText?: string;
  leftAction?: React.ReactNode;
  rightAction?: React.ReactNode;
}

export const MobileHeader: React.FC<MobileHeaderProps> = ({
  title = 'Divine Daily',
  onMenuClick,
  onNotificationClick,
  onAvatarClick,
  showNotificationBadge = false,
  avatarText = 'U',
  leftAction,
  rightAction
}) => {
  return (
    <header className="mobile-header">
      <div className="mobile-header__left">
        {leftAction || (
          <button className="mobile-header__icon-button" onClick={onMenuClick}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
        )}
      </div>
      
      <div className="mobile-header__center">
        <h1 className="mobile-header__title">{title}</h1>
      </div>
      
      <div className="mobile-header__right">
        {rightAction || (
          <>
            <button 
              className={`mobile-header__icon-button ${showNotificationBadge ? 'mobile-header__badge' : ''}`}
              onClick={onNotificationClick}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
            </button>
            <div className="mobile-header__avatar" onClick={onAvatarClick}>
              {avatarText}
            </div>
          </>
        )}
      </div>
    </header>
  );
};

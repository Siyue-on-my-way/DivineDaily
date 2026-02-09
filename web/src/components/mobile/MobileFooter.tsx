import React from 'react';
import './MobileFooter.css';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

interface MobileFooterProps {
  items: NavItem[];
  activeId: string;
  onItemClick: (id: string) => void;
}

export const MobileFooter: React.FC<MobileFooterProps> = ({
  items,
  activeId,
  onItemClick
}) => {
  return (
    <nav className="mobile-footer">
      {items.map((item) => (
        <button
          key={item.id}
          className={`mobile-footer__item ${activeId === item.id ? 'mobile-footer__item--active' : ''}`}
          onClick={() => onItemClick(item.id)}
        >
          <span className="mobile-footer__icon">{item.icon}</span>
          <span className="mobile-footer__label">{item.label}</span>
          {item.badge && item.badge > 0 && (
            <span className="mobile-footer__badge">
              {item.badge > 99 ? '99+' : item.badge}
            </span>
          )}
        </button>
      ))}
    </nav>
  );
};

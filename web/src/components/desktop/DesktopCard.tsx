import React from 'react';
import './DesktopCard.css';

interface DesktopCardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning';
  size?: 'default' | 'compact' | 'spacious';
  hoverable?: boolean;
  onClick?: () => void;
  className?: string;
}

export const DesktopCard: React.FC<DesktopCardProps> = ({
  children,
  title,
  subtitle,
  actions,
  variant = 'default',
  size = 'default',
  hoverable = false,
  onClick,
  className = '',
}) => {
  const classes = [
    'desktop-card',
    `desktop-card--${variant}`,
    `desktop-card--${size}`,
    hoverable && 'desktop-card--hoverable',
    onClick && 'desktop-card--clickable',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} onClick={onClick}>
      {(title || subtitle || actions) && (
        <div className="desktop-card__header">
          <div className="desktop-card__header-content">
            {title && <h3 className="desktop-card__title">{title}</h3>}
            {subtitle && <p className="desktop-card__subtitle">{subtitle}</p>}
          </div>
          {actions && <div className="desktop-card__actions">{actions}</div>}
        </div>
      )}
      <div className="desktop-card__body">{children}</div>
    </div>
  );
};


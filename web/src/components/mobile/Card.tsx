import React from 'react';
import './Card.css';

interface CardProps {
  variant?: 'default' | 'elevated' | 'flat' | 'gradient' | 'primary';
  size?: 'sm' | 'md' | 'lg';
  clickable?: boolean;
  onClick?: () => void;
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  size = 'md',
  clickable = false,
  onClick,
  className = '',
  children
}) => {
  const classes = [
    'mobile-card',
    variant !== 'default' && `mobile-card--${variant}`,
    `mobile-card--${size}`,
    clickable && 'mobile-card--clickable',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} onClick={onClick}>
      {children}
    </div>
  );
};

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ title, subtitle, action, icon }) => (
  <div className="mobile-card__header">
    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
      {icon && <div className="mobile-card__icon">{icon}</div>}
      <div>
        <h3 className="mobile-card__title">{title}</h3>
        {subtitle && <p className="mobile-card__subtitle">{subtitle}</p>}
      </div>
    </div>
    {action && <div>{action}</div>}
  </div>
);

export const CardContent: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="mobile-card__content">{children}</div>
);

export const CardFooter: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="mobile-card__footer">{children}</div>
);

export const CardBadge: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => (
  <span className={`mobile-card__badge ${className}`}>{children}</span>
);

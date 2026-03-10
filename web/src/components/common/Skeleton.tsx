import React from 'react';
import './Skeleton.css';

interface SkeletonProps {
  variant?: 'text' | 'title' | 'avatar' | 'rectangular' | 'circular';
  width?: string | number;
  height?: string | number;
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ 
  variant = 'text',
  width,
  height,
  className = ''
}) => {
  const getVariantClass = () => {
    switch (variant) {
      case 'text':
        return 'skeleton-text';
      case 'title':
        return 'skeleton-title';
      case 'avatar':
        return 'skeleton-avatar';
      case 'circular':
        return 'skeleton-avatar';
      default:
        return '';
    }
  };

  const style: React.CSSProperties = {
    width: width || (variant === 'avatar' || variant === 'circular' ? '40px' : '100%'),
    height: height || (variant === 'avatar' || variant === 'circular' ? '40px' : undefined)
  };

  return (
    <div 
      className={`skeleton ${getVariantClass()} ${className}`}
      style={style}
    />
  );
};

interface SkeletonGroupProps {
  count?: number;
  variant?: 'text' | 'title' | 'avatar' | 'rectangular';
}

export const SkeletonGroup: React.FC<SkeletonGroupProps> = ({ 
  count = 3,
  variant = 'text'
}) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <Skeleton key={index} variant={variant} />
      ))}
    </>
  );
};

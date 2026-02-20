import React from 'react';
import { useResponsive } from '../../hooks/useResponsive';
import { MobileLayout } from '../mobile/MobileLayout';
import { DesktopLayout } from './DesktopLayout';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
  showFooter?: boolean;
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ 
  children, 
  showHeader = true, 
  showFooter = true 
}) => {
  const { isMobile, isTablet } = useResponsive();

  // 移动端和平板使用 MobileLayout
  if (isMobile || isTablet) {
    return (
      <MobileLayout showHeader={showHeader} showFooter={showFooter}>
        {children}
      </MobileLayout>
    );
  }

  // 桌面端使用 DesktopLayout
  return <DesktopLayout>{children}</DesktopLayout>;
};


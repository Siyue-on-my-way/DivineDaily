import { useState, useEffect } from 'react';

export const breakpoints = {
  mobile: 0,
  tablet: 768,
  desktop: 1024,
  wide: 1440,
};

export type ScreenSize = 'mobile' | 'tablet' | 'desktop' | 'wide';
export type LayoutMode = 'mobile' | 'desktop';

export function useResponsive() {
  const [screenSize, setScreenSize] = useState<ScreenSize>('mobile');
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('mobile');

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      
      // 确定屏幕尺寸
      if (width >= breakpoints.wide) {
        setScreenSize('wide');
      } else if (width >= breakpoints.desktop) {
        setScreenSize('desktop');
      } else if (width >= breakpoints.tablet) {
        setScreenSize('tablet');
      } else {
        setScreenSize('mobile');
      }

      // 确定布局模式
      if (width >= breakpoints.desktop) {
        setLayoutMode('desktop');
      } else {
        setLayoutMode('mobile');
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    // 屏幕尺寸判断
    isMobile: screenSize === 'mobile',
    isTablet: screenSize === 'tablet',
    isDesktop: screenSize === 'desktop' || screenSize === 'wide',
    isWide: screenSize === 'wide',
    screenSize,
    
    // 布局模式判断
    layoutMode,
    isDesktopLayout: layoutMode === 'desktop',
    isMobileLayout: layoutMode === 'mobile',
    
    // 断点值
    breakpoints,
    
    // 当前宽度
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
  };
}

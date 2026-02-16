import { useState, useEffect } from 'react';

export const breakpoints = {
  mobile: 0,
  tablet: 768,
  desktop: 1024,
  wide: 1440,
};

export type ScreenSize = 'mobile' | 'tablet' | 'desktop' | 'wide';

export function useResponsive() {
  const [screenSize, setScreenSize] = useState<ScreenSize>('mobile');

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width >= breakpoints.wide) {
        setScreenSize('wide');
      } else if (width >= breakpoints.desktop) {
        setScreenSize('desktop');
      } else if (width >= breakpoints.tablet) {
        setScreenSize('tablet');
      } else {
        setScreenSize('mobile');
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    isMobile: screenSize === 'mobile',
    isTablet: screenSize === 'tablet',
    isDesktop: screenSize === 'desktop' || screenSize === 'wide',
    isWide: screenSize === 'wide',
    screenSize,
  };
}

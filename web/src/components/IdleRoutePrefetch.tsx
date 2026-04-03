import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * 在首页空闲时预取高频路由 chunk，减少首次点击「占卜/塔罗/历史」时的等待。
 * 与 App.tsx 中 lazy() 使用相同的 import 路径，以便命中同一分包。
 */
export function IdleRoutePrefetch() {
  const location = useLocation();

  useEffect(() => {
    if (location.pathname !== '/') {
      return;
    }

    const run = () => {
      void import('../pages/DivinationPage');
      void import('../pages/TarotPage');
      void import('../pages/HistoryPage');
    };

    const ric = window.requestIdleCallback;
    if (typeof ric === 'function') {
      const id = ric(run, { timeout: 3000 });
      return () => window.cancelIdleCallback(id);
    }

    const t = window.setTimeout(run, 1800);
    return () => window.clearTimeout(t);
  }, [location.pathname]);

  return null;
}

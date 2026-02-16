import { useEffect, useState } from 'react';
import './OfflineBanner.css';

export default function OfflineBanner() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setTimeout(() => setShowBanner(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowBanner(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // 初始检查
    if (!navigator.onLine) {
      setShowBanner(true);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = () => {
    window.location.reload();
  };

  if (!showBanner) return null;

  return (
    <div className={`offline-banner ${isOnline ? 'offline-banner--online' : ''}`}>
      <div className="offline-banner__content">
        <div className="offline-banner__icon">
          {isOnline ? '✅' : '📡'}
        </div>
        <div className="offline-banner__text">
          {isOnline ? '网络已恢复' : '网络连接已断开，部分功能可能受限'}
        </div>
        {!isOnline && (
          <button className="offline-banner__button" onClick={handleRetry}>
            重试
          </button>
        )}
      </div>
    </div>
  );
}

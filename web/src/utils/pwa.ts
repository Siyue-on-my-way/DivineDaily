/**
 * PWA 工具类
 * 提供 PWA 相关功能的辅助方法
 */

export class PWAUtils {
  /**
   * 检查是否支持 PWA
   */
  static isPWASupported(): boolean {
    return 'serviceWorker' in navigator && 'PushManager' in window;
  }

  /**
   * 检查是否已安装为 PWA
   */
  static isInstalled(): boolean {
    return window.matchMedia('(display-mode: standalone)').matches ||
           (window.navigator as any).standalone === true;
  }

  /**
   * 检查是否可以安装 PWA
   */
  static canInstall(): boolean {
    return !this.isInstalled() && this.isPWASupported();
  }

  /**
   * 提示用户安装 PWA
   */
  static promptInstall(deferredPrompt: any): Promise<boolean> {
    if (!deferredPrompt) {
      return Promise.resolve(false);
    }

    return deferredPrompt.prompt().then(() => {
      return deferredPrompt.userChoice.then((choiceResult: any) => {
        return choiceResult.outcome === 'accepted';
      });
    });
  }

  /**
   * 检查 Service Worker 状态
   */
  static async getServiceWorkerStatus(): Promise<{
    registered: boolean;
    active: boolean;
    waiting: boolean;
  }> {
    if (!('serviceWorker' in navigator)) {
      return { registered: false, active: false, waiting: false };
    }

    const registration = await navigator.serviceWorker.getRegistration();
    
    return {
      registered: !!registration,
      active: !!registration?.active,
      waiting: !!registration?.waiting
    };
  }

  /**
   * 更新 Service Worker
   */
  static async updateServiceWorker(): Promise<boolean> {
    if (!('serviceWorker' in navigator)) {
      return false;
    }

    const registration = await navigator.serviceWorker.getRegistration();
    if (!registration) {
      return false;
    }

    await registration.update();
    return true;
  }

  /**
   * 卸载 Service Worker
   */
  static async unregisterServiceWorker(): Promise<boolean> {
    if (!('serviceWorker' in navigator)) {
      return false;
    }

    const registration = await navigator.serviceWorker.getRegistration();
    if (!registration) {
      return false;
    }

    return await registration.unregister();
  }

  /**
   * 清除所有缓存
   */
  static async clearAllCaches(): Promise<void> {
    if (!('caches' in window)) {
      return;
    }

    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames.map(cacheName => caches.delete(cacheName))
    );
  }

  /**
   * 获取缓存大小（估算）
   */
  static async getCacheSize(): Promise<number> {
    if (!('caches' in window)) {
      return 0;
    }

    let totalSize = 0;
    const cacheNames = await caches.keys();

    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const requests = await cache.keys();
      
      for (const request of requests) {
        const response = await cache.match(request);
        if (response) {
          const blob = await response.blob();
          totalSize += blob.size;
        }
      }
    }

    return totalSize;
  }

  /**
   * 格式化缓存大小
   */
  static formatCacheSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
}

/**
 * PWA 安装提示 Hook
 */
export function usePWAInstall() {
  const [deferredPrompt, setDeferredPrompt] = React.useState<any>(null);
  const [isInstallable, setIsInstallable] = React.useState(false);

  React.useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const install = async () => {
    if (!deferredPrompt) {
      return false;
    }

    const accepted = await PWAUtils.promptInstall(deferredPrompt);
    setDeferredPrompt(null);
    setIsInstallable(false);
    
    return accepted;
  };

  return {
    isInstallable,
    install,
    isInstalled: PWAUtils.isInstalled()
  };
}

// React import for TypeScript
import React from 'react';

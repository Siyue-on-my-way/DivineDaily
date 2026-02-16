import { lazy, Suspense } from 'react';

/**
 * 代码分割工具
 */
export const lazyLoad = (importFunc: () => Promise<any>) => {
  const LazyComponent = lazy(importFunc);
  
  return (props: any) => (
    <Suspense fallback={<div>加载中...</div>}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * 图片懒加载
 */
export class ImageLazyLoader {
  private observer: IntersectionObserver | null = null;

  constructor() {
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement;
              const src = img.dataset.src;
              
              if (src) {
                img.src = src;
                img.removeAttribute('data-src');
                this.observer?.unobserve(img);
              }
            }
          });
        },
        {
          rootMargin: '50px'
        }
      );
    }
  }

  observe(element: HTMLImageElement) {
    if (this.observer) {
      this.observer.observe(element);
    } else {
      // 降级方案：直接加载
      const src = element.dataset.src;
      if (src) {
        element.src = src;
      }
    }
  }

  disconnect() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

/**
 * 性能监控
 */
export class PerformanceMonitor {
  /**
   * 测量函数执行时间
   */
  static measure(name: string, fn: () => void): number {
    const start = performance.now();
    fn();
    const end = performance.now();
    const duration = end - start;
    
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
    return duration;
  }

  /**
   * 测量异步函数执行时间
   */
  static async measureAsync(name: string, fn: () => Promise<void>): Promise<number> {
    const start = performance.now();
    await fn();
    const end = performance.now();
    const duration = end - start;
    
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
    return duration;
  }

  /**
   * 获取页面性能指标
   */
  static getMetrics() {
    if (!('performance' in window)) {
      return null;
    }

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    
    if (!navigation) {
      return null;
    }

    return {
      // DNS 查询时间
      dns: navigation.domainLookupEnd - navigation.domainLookupStart,
      // TCP 连接时间
      tcp: navigation.connectEnd - navigation.connectStart,
      // 请求时间
      request: navigation.responseStart - navigation.requestStart,
      // 响应时间
      response: navigation.responseEnd - navigation.responseStart,
      // DOM 解析时间
      domParse: navigation.domInteractive - navigation.responseEnd,
      // 资源加载时间
      resourceLoad: navigation.loadEventStart - navigation.domContentLoadedEventEnd,
      // 总时间
      total: navigation.loadEventEnd - navigation.fetchStart,
      // 首次内容绘制 (FCP)
      fcp: this.getFCP(),
      // 最大内容绘制 (LCP)
      lcp: this.getLCP()
    };
  }

  /**
   * 获取 FCP (First Contentful Paint)
   */
  private static getFCP(): number | null {
    const entries = performance.getEntriesByType('paint');
    const fcp = entries.find((entry) => entry.name === 'first-contentful-paint');
    return fcp ? fcp.startTime : null;
  }

  /**
   * 获取 LCP (Largest Contentful Paint)
   */
  private static getLCP(): number | null {
    const entries = performance.getEntriesByType('largest-contentful-paint');
    const lcp = entries[entries.length - 1];
    return lcp ? lcp.startTime : null;
  }

  /**
   * 上报性能数据
   */
  static report() {
    const metrics = this.getMetrics();
    
    if (metrics) {
      console.table(metrics);
      
      // 这里可以上报到分析服务
      // analytics.track('performance', metrics);
    }
  }
}

/**
 * 虚拟滚动辅助类
 */
export class VirtualScroller {
  private container: HTMLElement;
  private itemHeight: number;
  private visibleCount: number;
  private totalCount: number;
  private scrollTop: number = 0;

  constructor(
    container: HTMLElement,
    itemHeight: number,
    totalCount: number
  ) {
    this.container = container;
    this.itemHeight = itemHeight;
    this.totalCount = totalCount;
    this.visibleCount = Math.ceil(container.clientHeight / itemHeight) + 2;
  }

  getVisibleRange(): { start: number; end: number } {
    const start = Math.floor(this.scrollTop / this.itemHeight);
    const end = Math.min(start + this.visibleCount, this.totalCount);
    
    return { start, end };
  }

  updateScroll(scrollTop: number) {
    this.scrollTop = scrollTop;
  }

  getTotalHeight(): number {
    return this.totalCount * this.itemHeight;
  }

  getOffsetY(): number {
    const { start } = this.getVisibleRange();
    return start * this.itemHeight;
  }
}

/**
 * 请求缓存
 */
export class RequestCache {
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private ttl: number;

  constructor(ttl: number = 5 * 60 * 1000) {
    this.ttl = ttl;
  }

  get(key: string): any | null {
    const cached = this.cache.get(key);
    
    if (!cached) {
      return null;
    }

    const now = Date.now();
    if (now - cached.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  set(key: string, data: any) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  clear() {
    this.cache.clear();
  }

  delete(key: string) {
    this.cache.delete(key);
  }
}

/**
 * 批量请求合并
 */
export class RequestBatcher<T> {
  private queue: Array<{
    resolve: (value: T) => void;
    reject: (error: any) => void;
  }> = [];
  private timer: NodeJS.Timeout | null = null;
  private batchFn: (items: number) => Promise<T[]>;
  private delay: number;

  constructor(batchFn: (items: number) => Promise<T[]>, delay: number = 50) {
    this.batchFn = batchFn;
    this.delay = delay;
  }

  add(): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push({ resolve, reject });

      if (this.timer) {
        clearTimeout(this.timer);
      }

      this.timer = setTimeout(() => {
        this.flush();
      }, this.delay);
    });
  }

  private async flush() {
    if (this.queue.length === 0) {
      return;
    }

    const items = this.queue.splice(0);
    
    try {
      const results = await this.batchFn(items.length);
      
      items.forEach((item, index) => {
        item.resolve(results[index]);
      });
    } catch (error) {
      items.forEach((item) => {
        item.reject(error);
      });
    }
  }
}

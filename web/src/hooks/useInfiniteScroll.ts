import { useEffect, useRef, useCallback, useState } from 'react';

/**
 * 无限滚动配置选项
 */
interface UseInfiniteScrollOptions {
  /** 加载更多数据的回调函数 */
  onLoadMore: () => Promise<void>;
  /** 是否还有更多数据，默认 true */
  hasMore?: boolean;
  /** 触发加载的距离阈值（像素），默认 100 */
  threshold?: number;
  /** 是否禁用，默认 false */
  disabled?: boolean;
}

/**
 * 无限滚动 Hook
 * 
 * 使用 Intersection Observer API 监听滚动到底部，自动加载更多数据
 * 
 * @param options - 配置选项
 * @returns 加载状态和观察器引用
 * 
 * @example
 * ```tsx
 * const { loading, observerRef } = useInfiniteScroll({
 *   onLoadMore: async () => {
 *     await loadMoreData();
 *   },
 *   hasMore: hasMoreData
 * });
 * 
 * return (
 *   <div>
 *     {items.map(item => <Item key={item.id} {...item} />)}
 *     <div ref={observerRef}>
 *       {loading && <div>加载中...</div>}
 *       {!hasMore && <div>没有更多了</div>}
 *     </div>
 *   </div>
 * );
 * ```
 */
export const useInfiniteScroll = ({
  onLoadMore,
  hasMore = true,
  threshold = 100,
  disabled = false
}: UseInfiniteScrollOptions) => {
  const [loading, setLoading] = useState(false);
  const observerRef = useRef<HTMLDivElement | null>(null);
  const observerInstanceRef = useRef<IntersectionObserver | null>(null);
  const isLoadingRef = useRef(false);

  /**
   * 加载更多数据
   */
  const loadMore = useCallback(async () => {
    // 防止重复加载
    if (isLoadingRef.current || !hasMore || disabled) {
      return;
    }

    isLoadingRef.current = true;
    setLoading(true);

    try {
      await onLoadMore();
    } catch (error) {
      console.error('加载更多失败:', error);
    } finally {
      setLoading(false);
      isLoadingRef.current = false;
    }
  }, [onLoadMore, hasMore, disabled]);

  /**
   * 设置 Intersection Observer
   */
  useEffect(() => {
    if (disabled || !hasMore) {
      return;
    }

    // 创建观察器
    const options: IntersectionObserverInit = {
      root: null, // 使用视口作为根元素
      rootMargin: `${threshold}px`, // 提前触发
      threshold: 0.1, // 10% 可见时触发
    };

    observerInstanceRef.current = new IntersectionObserver((entries) => {
      const [entry] = entries;
      
      // 当目标元素进入视口时触发加载
      if (entry.isIntersecting && !isLoadingRef.current) {
        loadMore();
      }
    }, options);

    // 开始观察目标元素
    const currentObserver = observerRef.current;
    if (currentObserver) {
      observerInstanceRef.current.observe(currentObserver);
    }

    // 清理函数
    return () => {
      if (observerInstanceRef.current && currentObserver) {
        observerInstanceRef.current.unobserve(currentObserver);
      }
    };
  }, [loadMore, hasMore, disabled, threshold]);

  return {
    /** 是否正在加载 */
    loading,
    /** 观察器目标元素的 ref */
    observerRef,
  };
};

import { useCallback, useRef, useState } from 'react';

/**
 * 下拉刷新配置选项
 */
interface UseRefreshOptions {
  /** 刷新回调函数 */
  onRefresh: () => Promise<void>;
  /** 触发刷新的下拉距离阈值（像素），默认 80 */
  threshold?: number;
  /** 是否禁用刷新，默认 false */
  disabled?: boolean;
}

/**
 * 下拉刷新状态
 */
export type RefreshState = 'idle' | 'pulling' | 'ready' | 'refreshing';

/**
 * 下拉刷新 Hook
 * 
 * 实现移动端下拉刷新功能，监听触摸事件并在下拉超过阈值时触发刷新
 * 
 * @param options - 配置选项
 * @returns 刷新状态和绑定属性
 * 
 * @example
 * ```tsx
 * const { refreshState, pullDistance, bind } = useRefresh({
 *   onRefresh: async () => {
 *     await loadData();
 *   }
 * });
 * 
 * return (
 *   <div {...bind()}>
 *     {refreshState === 'refreshing' && <div>刷新中...</div>}
 *     <YourContent />
 *   </div>
 * );
 * ```
 */
export const useRefresh = ({
  onRefresh,
  threshold = 80,
  disabled = false
}: UseRefreshOptions) => {
  const [refreshState, setRefreshState] = useState<RefreshState>('idle');
  const [pullDistance, setPullDistance] = useState(0);
  
  const startYRef = useRef<number>(0);
  const scrollTopRef = useRef<number>(0);
  const isRefreshingRef = useRef(false);

  /**
   * 触摸开始
   */
  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (disabled || isRefreshingRef.current) return;
    
    // 记录初始触摸位置和滚动位置
    startYRef.current = e.touches[0].clientY;
    scrollTopRef.current = window.scrollY || document.documentElement.scrollTop;
  }, [disabled]);

  /**
   * 触摸移动
   */
  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (disabled || isRefreshingRef.current) return;
    
    const currentY = e.touches[0].clientY;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    
    // 只在页面顶部且向下拉时触发
    if (scrollTop === 0 && scrollTopRef.current === 0) {
      const distance = currentY - startYRef.current;
      
      if (distance > 0) {
        // 阻止默认滚动行为
        e.preventDefault();
        
        // 计算下拉距离（添加阻尼效果）
        const dampedDistance = Math.min(distance * 0.5, threshold * 1.5);
        setPullDistance(dampedDistance);
        
        // 更新状态
        if (dampedDistance >= threshold) {
          setRefreshState('ready');
        } else {
          setRefreshState('pulling');
        }
      }
    }
  }, [disabled, threshold]);

  /**
   * 触摸结束
   */
  const handleTouchEnd = useCallback(async () => {
    if (disabled || isRefreshingRef.current) return;
    
    // 如果达到阈值，触发刷新
    if (refreshState === 'ready') {
      setRefreshState('refreshing');
      isRefreshingRef.current = true;
      
      try {
        await onRefresh();
      } catch (error) {
        console.error('刷新失败:', error);
      } finally {
        // 刷新完成，重置状态
        setTimeout(() => {
          setRefreshState('idle');
          setPullDistance(0);
          isRefreshingRef.current = false;
        }, 300);
      }
    } else {
      // 未达到阈值，回弹
      setRefreshState('idle');
      setPullDistance(0);
    }
  }, [disabled, refreshState, onRefresh]);

  /**
   * 绑定触摸事件到容器元素
   */
  const bind = useCallback(() => {
    return {
      onTouchStart: handleTouchStart as any,
      onTouchMove: handleTouchMove as any,
      onTouchEnd: handleTouchEnd as any,
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd]);

  return {
    /** 当前刷新状态 */
    refreshState,
    /** 当前下拉距离 */
    pullDistance,
    /** 绑定事件到容器 */
    bind,
  };
};

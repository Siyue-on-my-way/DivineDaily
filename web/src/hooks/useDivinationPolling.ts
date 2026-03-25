import { useEffect, useRef, useCallback } from 'react';
import axiosInstance from '../lib/axios';
import type { DivinationResult } from '../types/divination';

/**
 * 占卜轮询 Hook 配置选项
 */
interface UseDivinationPollingOptions {
  /** 占卜会话ID */
  sessionId: string;
  /** 成功回调 */
  onSuccess: (result: DivinationResult) => void;
  /** 错误回调 */
  onError: (error: DivinationPollingError) => void;
  /** 进度回调（可选） */
  onProgress?: (elapsed: number, attempts: number) => void;
  /** 最大尝试次数，默认60次 */
  maxAttempts?: number;
  /** 轮询间隔（毫秒），默认1000ms */
  interval?: number;
}

/**
 * 占卜轮询错误类型
 */
export interface DivinationPollingError extends Error {
  /** 错误类型 */
  type: 'timeout' | 'network' | 'server' | 'cancelled' | 'unknown';
  /** HTTP 状态码（如果有） */
  statusCode?: number;
  /** 原始错误对象 */
  originalError?: any;
}

/**
 * 创建友好的错误对象
 */
function createPollingError(
  type: DivinationPollingError['type'],
  message: string,
  statusCode?: number,
  originalError?: any
): DivinationPollingError {
  const error = new Error(message) as DivinationPollingError;
  error.type = type;
  error.statusCode = statusCode;
  error.originalError = originalError;
  return error;
}

/**
 * 占卜结果轮询 Hook
 * 
 * 用于异步获取占卜结果，支持：
 * - 自动轮询直到结果返回
 * - 超时处理
 * - 错误分类和友好提示
 * - 进度回调
 * - 手动取消
 * 
 * @param options - 轮询配置选项
 * @returns 包含 cancel 方法的对象
 */
export const useDivinationPolling = ({
  sessionId,
  onSuccess,
  onError,
  onProgress,
  maxAttempts = 60,
  interval = 1000,
}: UseDivinationPollingOptions) => {
  const BACKOFF_STEP_MS = 500;
  const MAX_INTERVAL_MS = 5000;
  const attemptsRef = useRef(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isMountedRef = useRef(true);
  const startTimeRef = useRef<number>(0);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  const onProgressRef = useRef(onProgress);

  const getNextInterval = useCallback(() => {
    const backoff = interval + (attemptsRef.current - 1) * BACKOFF_STEP_MS;
    return Math.min(MAX_INTERVAL_MS, Math.max(interval, backoff));
  }, [interval]);

  useEffect(() => {
    onSuccessRef.current = onSuccess;
    onErrorRef.current = onError;
    onProgressRef.current = onProgress;
  }, [onSuccess, onError, onProgress]);

  /**
   * 清理资源（定时器和请求）
   */
  const cleanup = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  /**
   * 轮询占卜结果
   */
  const pollResult = useCallback(async () => {
    // 如果没有 sessionId，不执行轮询
    if (!sessionId) {
      return;
    }

    if (!isMountedRef.current) {
      cleanup();
      return;
    }

    // 检查是否超过最大尝试次数
    if (attemptsRef.current >= maxAttempts) {
      cleanup();
      const error = createPollingError(
        'timeout',
        '占卜处理超时，请稍后在历史记录中查看结果，或重新占卜',
        undefined,
        undefined
      );
      onErrorRef.current(error);
      return;
    }

    attemptsRef.current += 1;

    // 计算已用时间并触发进度回调
    const elapsed = Date.now() - startTimeRef.current;
    if (onProgressRef.current) {
      onProgressRef.current(elapsed, attemptsRef.current);
    }

    try {
      // 创建新的 AbortController
      abortControllerRef.current = new AbortController();

      // 调用 API 获取结果
      const response = await axiosInstance.get<DivinationResult>(
        `/divinations/${sessionId}`,
        { 
          signal: abortControllerRef.current.signal,
          timeout: 10000, // 单次请求10秒超时
          headers: {
            'X-Silent-Error': '1',
          },
        }
      );

      if (!isMountedRef.current) {
        cleanup();
        return;
      }

      // 根据状态判断是否继续轮询
      const result = response.data;
      if (result.status === 'processing' || result.status === 'pending') {
        if (attemptsRef.current < maxAttempts) {
          timerRef.current = setTimeout(pollResult, getNextInterval());
        } else {
          cleanup();
          const timeoutError = createPollingError(
            'timeout',
            '占卜处理超时，请稍后在历史记录中查看结果',
            undefined,
            undefined
          );
          onErrorRef.current(timeoutError);
        }
        return;
      }

      if (result.status === 'failed') {
        cleanup();
        const failedError = createPollingError(
          'server',
          result.error_message || result.detail || result.summary || '占卜处理失败，请稍后重试',
          500,
          result
        );
        onErrorRef.current(failedError);
        return;
      }

      // completed 或无状态（兼容老接口）
      cleanup();
      onSuccessRef.current(result);

    } catch (error: any) {
      if (!isMountedRef.current) {
        cleanup();
        return;
      }

      // 如果是取消请求，直接返回
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        return;
      }

      // 分类处理错误
      const statusCode = error.response?.status;
      
      // 404 表示结果还未生成，继续轮询
      if (statusCode === 404) {
        if (attemptsRef.current < maxAttempts) {
          timerRef.current = setTimeout(pollResult, getNextInterval());
        } else {
          cleanup();
          const timeoutError = createPollingError(
            'timeout',
            '占卜处理超时，请稍后在历史记录中查看结果',
            statusCode,
            error
          );
          onErrorRef.current(timeoutError);
        }
        return;
      }

      // 500 服务器错误
      if (statusCode && statusCode >= 500) {
        cleanup();
        const serverError = createPollingError(
          'server',
          '服务器繁忙，请稍后重试',
          statusCode,
          error
        );
        onErrorRef.current(serverError);
        return;
      }

      // 401 认证错误
      if (statusCode === 401) {
        cleanup();
        const authError = createPollingError(
          'server',
          '登录已过期，请重新登录',
          statusCode,
          error
        );
        onErrorRef.current(authError);
        return;
      }

      // 网络错误
      if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK' || !statusCode) {
        // 网络错误，继续重试
        if (attemptsRef.current < maxAttempts) {
          timerRef.current = setTimeout(pollResult, getNextInterval());
        } else {
          cleanup();
          const networkError = createPollingError(
            'network',
            '网络连接失败，请检查网络后重试',
            undefined,
            error
          );
          onErrorRef.current(networkError);
        }
        return;
      }

      // 其他错误，继续重试
      if (attemptsRef.current < maxAttempts) {
        timerRef.current = setTimeout(pollResult, getNextInterval());
      } else {
        cleanup();
        const unknownError = createPollingError(
          'unknown',
          error.response?.data?.detail || error.message || '占卜失败，请重试',
          statusCode,
          error
        );
        onErrorRef.current(unknownError);
      }
    }
  }, [sessionId, maxAttempts, cleanup, getNextInterval]);

  useEffect(() => {
    // 如果没有 sessionId，不启动轮询
    if (!sessionId) {
      return;
    }

    isMountedRef.current = true;
    attemptsRef.current = 0; // 重置尝试次数
    startTimeRef.current = Date.now(); // 记录开始时间
    
    // 延迟 2 秒后开始第一次轮询（给后端处理时间）
    timerRef.current = setTimeout(pollResult, 2000);

    // 清理函数
    return () => {
      isMountedRef.current = false;
      cleanup();
    };
  }, [sessionId, pollResult, cleanup]);

  return { 
    /**
     * 手动取消轮询
     */
    cancel: cleanup 
  };
};

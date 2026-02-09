import { useEffect, useRef, useCallback } from 'react';
import axiosInstance from '../lib/axios';
import type { DivinationResult } from '../types/divination';

interface UseDivinationPollingOptions {
  sessionId: string;
  onSuccess: (result: DivinationResult) => void;
  onError: (error: Error) => void;
  maxAttempts?: number;
  interval?: number;
}

export const useDivinationPolling = ({
  sessionId,
  onSuccess,
  onError,
  maxAttempts = 30,
  interval = 1000,
}: UseDivinationPollingOptions) => {
  const attemptsRef = useRef(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isMountedRef = useRef(true);

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

  const pollResult = useCallback(async () => {
    // 如果没有 sessionId，不执行轮询
    if (!sessionId) {
      return;
    }

    if (!isMountedRef.current) {
      cleanup();
      return;
    }

    if (attemptsRef.current >= maxAttempts) {
      cleanup();
      onError(new Error('占卜超时，请重试'));
      return;
    }

    attemptsRef.current += 1;

    try {
      // 创建新的 AbortController
      abortControllerRef.current = new AbortController();

      const response = await axiosInstance.get<DivinationResult>(
        `/divinations/${sessionId}/result`,
        { signal: abortControllerRef.current.signal }
      );

      if (!isMountedRef.current) {
        cleanup();
        return;
      }

      // 成功获取结果
      cleanup();
      onSuccess(response.data);
    } catch (error: any) {
      if (!isMountedRef.current) {
        cleanup();
        return;
      }

      // 如果是取消请求，直接返回
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        return;
      }

      // 如果还有重试次数，继续轮询
      if (attemptsRef.current < maxAttempts) {
        timerRef.current = setTimeout(pollResult, interval);
      } else {
        cleanup();
        onError(error);
      }
    }
  }, [sessionId, maxAttempts, interval, onSuccess, onError, cleanup]);

  useEffect(() => {
    // 如果没有 sessionId，不启动轮询
    if (!sessionId) {
      return;
    }

    isMountedRef.current = true;
    attemptsRef.current = 0; // 重置尝试次数
    
    // 延迟 2 秒后开始第一次轮询
    timerRef.current = setTimeout(pollResult, 2000);

    // 清理函数
    return () => {
      isMountedRef.current = false;
      cleanup();
    };
  }, [sessionId, pollResult, cleanup]);

  return { cancel: cleanup };
};

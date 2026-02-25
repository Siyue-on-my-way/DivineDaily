import { ToastType } from '../components/ui/Toast';

export const toast = {
  success: (message: string, duration?: number) => {
    window.dispatchEvent(new CustomEvent('toast:success', {
      detail: { message, duration }
    }));
  },

  error: (message: string, duration?: number) => {
    window.dispatchEvent(new CustomEvent('toast:error', {
      detail: { message, duration }
    }));
  },

  warning: (message: string, duration?: number) => {
    window.dispatchEvent(new CustomEvent('toast:warning', {
      detail: { message, duration }
    }));
  },

  info: (message: string, duration?: number) => {
    window.dispatchEvent(new CustomEvent('toast:info', {
      detail: { message, duration }
    }));
  },
};

/**
 * useToast Hook
 * 提供 toast 通知功能
 */
export const useToast = () => {
  const showToast = (message: string, type: ToastType = 'info', duration?: number) => {
    window.dispatchEvent(new CustomEvent(`toast:${type}`, {
      detail: { message, duration }
    }));
  };

  return {
    showToast,
    success: (message: string, duration?: number) => toast.success(message, duration),
    error: (message: string, duration?: number) => toast.error(message, duration),
    warning: (message: string, duration?: number) => toast.warning(message, duration),
    info: (message: string, duration?: number) => toast.info(message, duration),
  };
};

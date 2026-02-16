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

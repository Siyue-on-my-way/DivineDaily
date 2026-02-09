import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface UIState {
  // Toast 通知
  toasts: ToastMessage[];
  
  // Modal 状态
  modals: Record<string, boolean>;
  
  // Actions
  addToast: (toast: Omit<ToastMessage, 'id'>) => void;
  removeToast: (id: string) => void;
  openModal: (modalId: string) => void;
  closeModal: (modalId: string) => void;
  toggleModal: (modalId: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  toasts: [],
  modals: {},

  addToast: (toast) => set((state) => ({
    toasts: [
      ...state.toasts,
      {
        ...toast,
        id: `toast_${Date.now()}_${Math.random()}`,
      },
    ],
  })),

  removeToast: (id) => set((state) => ({
    toasts: state.toasts.filter((t) => t.id !== id),
  })),

  openModal: (modalId) => set((state) => ({
    modals: { ...state.modals, [modalId]: true },
  })),

  closeModal: (modalId) => set((state) => ({
    modals: { ...state.modals, [modalId]: false },
  })),

  toggleModal: (modalId) => set((state) => ({
    modals: { ...state.modals, [modalId]: !state.modals[modalId] },
  })),
}));

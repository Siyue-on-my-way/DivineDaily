import { create } from 'zustand';
import type { DivinationResult } from '../types/divination';

interface DivinationState {
  // 当前占卜结果
  currentResult: DivinationResult | null;
  
  // 历史记录缓存
  history: DivinationResult[];
  
  // 加载状态
  isLoading: boolean;
  
  // Actions
  setCurrentResult: (result: DivinationResult | null) => void;
  addToHistory: (result: DivinationResult) => void;
  setHistory: (history: DivinationResult[]) => void;
  setLoading: (isLoading: boolean) => void;
  clearCurrent: () => void;
}

export const useDivinationStore = create<DivinationState>((set) => ({
  currentResult: null,
  history: [],
  isLoading: false,

  setCurrentResult: (result) => set({ currentResult: result }),
  
  addToHistory: (result) => set((state) => ({
    history: [result, ...state.history].slice(0, 50), // 最多保留 50 条
  })),
  
  setHistory: (history) => set({ history }),
  setLoading: (isLoading) => set({ isLoading }),
  clearCurrent: () => set({ currentResult: null }),
}));

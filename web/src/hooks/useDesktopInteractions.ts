/* 键盘快捷键支持 */
export const useKeyboardShortcuts = (shortcuts: Record<string, () => void>) => {
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();
      const ctrl = e.ctrlKey || e.metaKey;
      const shift = e.shiftKey;
      
      let shortcutKey = '';
      if (ctrl) shortcutKey += 'ctrl+';
      if (shift) shortcutKey += 'shift+';
      shortcutKey += key;
      
      if (shortcuts[shortcutKey]) {
        e.preventDefault();
        shortcuts[shortcutKey]();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
};

/* 拖拽排序支持 */
export const useDragAndDrop = <T,>(
  items: T[],
  onReorder: (items: T[]) => void
) => {
  const [draggedIndex, setDraggedIndex] = React.useState<number | null>(null);
  
  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };
  
  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;
    
    const newItems = [...items];
    const draggedItem = newItems[draggedIndex];
    newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, draggedItem);
    
    onReorder(newItems);
    setDraggedIndex(index);
  };
  
  const handleDragEnd = () => {
    setDraggedIndex(null);
  };
  
  return {
    draggedIndex,
    handleDragStart,
    handleDragOver,
    handleDragEnd,
  };
};

import React from 'react';


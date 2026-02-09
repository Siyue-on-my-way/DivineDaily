import React, { useEffect, useState } from 'react';
import './Toast.css';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastProps {
  message: ToastMessage;
  onClose: (id: string) => void;
}

const Toast: React.FC<ToastProps> = ({ message, onClose }) => {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const duration = message.duration || 3000;
    
    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(() => onClose(message.id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [message, onClose]);

  const getIcon = () => {
    switch (message.type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'warning':
        return '⚠';
      case 'info':
        return 'ℹ';
      default:
        return 'ℹ';
    }
  };

  return (
    <div className={`toast toast--${message.type} ${isExiting ? 'toast--exit' : ''}`}>
      <div className="toast__icon">{getIcon()}</div>
      <div className="toast__message">{message.message}</div>
      <button 
        className="toast__close" 
        onClick={() => {
          setIsExiting(true);
          setTimeout(() => onClose(message.id), 300);
        }}
      >
        ✕
      </button>
    </div>
  );
};

export const ToastContainer: React.FC = () => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const handleToast = (event: Event) => {
      const customEvent = event as CustomEvent<{ message: string; duration?: number }>;
      const type = event.type.split(':')[1] as ToastType;
      
      const newToast: ToastMessage = {
        id: `toast_${Date.now()}_${Math.random()}`,
        type,
        message: customEvent.detail.message,
        duration: customEvent.detail.duration,
      };

      setToasts(prev => [...prev, newToast]);
    };

    window.addEventListener('toast:success', handleToast);
    window.addEventListener('toast:error', handleToast);
    window.addEventListener('toast:warning', handleToast);
    window.addEventListener('toast:info', handleToast);

    return () => {
      window.removeEventListener('toast:success', handleToast);
      window.removeEventListener('toast:error', handleToast);
      window.removeEventListener('toast:warning', handleToast);
      window.removeEventListener('toast:info', handleToast);
    };
  }, []);

  const handleClose = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <Toast key={toast.id} message={toast} onClose={handleClose} />
      ))}
    </div>
  );
};

export default ToastContainer;

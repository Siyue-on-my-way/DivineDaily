import React, { useState } from 'react';
import './Input.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  required?: boolean;
  error?: string;
  helpText?: string;
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  required = false,
  error,
  helpText,
  icon,
  className = '',
  ...props
}) => {
  const inputClasses = [
    'mobile-input',
    icon && 'mobile-input--with-icon',
    error && 'mobile-input--error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="mobile-input-wrapper">
      {label && (
        <label className={`mobile-input-label ${required ? 'mobile-input-label--required' : ''}`}>
          {label}
        </label>
      )}
      <div className="mobile-input-container">
        {icon && <span className="mobile-input__icon">{icon}</span>}
        <input className={inputClasses} {...props} />
      </div>
      {error && (
        <span className="mobile-input-error">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </span>
      )}
      {helpText && !error && (
        <span className="mobile-input-help">{helpText}</span>
      )}
    </div>
  );
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  required?: boolean;
  error?: string;
  helpText?: string;
  showCounter?: boolean;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  required = false,
  error,
  helpText,
  showCounter = false,
  maxLength,
  className = '',
  value,
  ...props
}) => {
  // 使用 useMemo 从 value 计算字符数，避免状态不同步
  const charCount = React.useMemo(() => {
    return typeof value === 'string' ? value.length : 0;
  }, [value]);

  const textareaClasses = [
    'mobile-input',
    'mobile-textarea',
    error && 'mobile-input--error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="mobile-input-wrapper">
      {label && (
        <label className={`mobile-input-label ${required ? 'mobile-input-label--required' : ''}`}>
          {label}
        </label>
      )}
      <textarea 
        className={textareaClasses} 
        maxLength={maxLength}
        value={value}
        {...props} 
      />
      {showCounter && maxLength && (
        <div className={`mobile-input-counter ${charCount >= maxLength ? 'mobile-input-counter--limit' : ''}`}>
          {charCount} / {maxLength}
        </div>
      )}
      {error && (
        <span className="mobile-input-error">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </span>
      )}
      {helpText && !error && (
        <span className="mobile-input-help">{helpText}</span>
      )}
    </div>
  );
};

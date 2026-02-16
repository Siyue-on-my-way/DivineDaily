import React from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';

interface MysticButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  loading?: boolean;
  fullWidth?: boolean;
}

export const MysticButton = ({
  children,
  variant = 'primary',
  size = 'md',
  className,
  loading = false,
  fullWidth = false,
  disabled,
  ...props
}: MysticButtonProps) => {
  const baseStyles = "relative inline-flex items-center justify-center rounded-lg font-medium transition-all duration-300 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden";
  
  const variants = {
    primary: "bg-[var(--color-ethereal-gold)] text-[var(--color-deep-void)] shadow-[0_0_15px_var(--color-ethereal-gold-glow)] hover:shadow-[0_0_25px_var(--color-ethereal-gold-glow)] hover:scale-[1.02] active:scale-[0.98]",
    secondary: "bg-[var(--glass-bg)] border border-[var(--glass-border)] text-[var(--color-starlight)] hover:bg-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)]",
    ghost: "bg-transparent text-[var(--color-starlight-dim)] hover:text-[var(--color-starlight)] hover:bg-[rgba(255,255,255,0.03)]"
  };

  const sizes = {
    sm: "h-8 px-4 text-xs",
    md: "h-10 px-6 text-sm",
    lg: "h-12 px-8 text-base"
  };

  return (
    <motion.button
      className={cn(baseStyles, variants[variant], sizes[size], fullWidth && "w-full", className)}
      whileTap={{ scale: 0.98 }}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span className="absolute inset-0 flex items-center justify-center bg-inherit">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </span>
      )}
      <span className={cn("flex items-center gap-2", loading && "opacity-0")}>
        {children}
      </span>
      
      {/* Shine Effect for Primary */}
      {variant === 'primary' && (
        <div className="absolute inset-0 -translate-x-full hover:animate-[shine_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12" />
      )}
    </motion.button>
  );
};

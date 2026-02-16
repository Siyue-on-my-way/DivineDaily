import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface MysticInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  containerClassName?: string;
}

export const MysticInput = forwardRef<HTMLInputElement, MysticInputProps>(
  ({ className, containerClassName, label, error, ...props }, ref) => {
    return (
      <div className={cn("flex flex-col gap-1.5", containerClassName)}>
        {label && (
          <label className="text-xs font-medium text-[var(--color-starlight-dim)] uppercase tracking-wider pl-1">
            {label}
          </label>
        )}
        <div className="relative group">
          <input
            ref={ref}
            className={cn(
              "w-full bg-[rgba(0,0,0,0.2)] border border-[var(--glass-border)] rounded-lg px-4 py-3 text-[var(--color-starlight)] placeholder:text-[var(--color-starlight-dim)]/50 focus:outline-none focus:border-[var(--color-nebula-purple)] focus:ring-1 focus:ring-[var(--color-nebula-purple-glow)] transition-all duration-300",
              error && "border-red-500 focus:border-red-500 focus:ring-red-500/20",
              className
            )}
            {...props}
          />
          {/* Bottom Glow Line */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-[1px] bg-[var(--color-nebula-purple)] transition-all duration-300 group-focus-within:w-full opacity-0 group-focus-within:opacity-100" />
        </div>
        {error && (
          <span className="text-xs text-red-400 pl-1">{error}</span>
        )}
      </div>
    );
  }
);

MysticInput.displayName = "MysticInput";

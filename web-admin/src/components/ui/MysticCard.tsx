import React from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';

interface MysticCardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  variant?: 'default' | 'glow' | 'interactive';
  className?: string;
}

export const MysticCard = ({ 
  children, 
  variant = 'default', 
  className,
  ...props 
}: MysticCardProps) => {
  const baseStyles = "relative overflow-hidden rounded-xl border border-[var(--glass-border)] bg-[var(--glass-bg)] backdrop-blur-md shadow-lg";
  
  const variants = {
    default: "",
    glow: "shadow-[0_0_20px_var(--color-nebula-purple-glow)] border-[var(--color-nebula-purple-glow)]",
    interactive: "hover:bg-[rgba(255,255,255,0.05)] hover:border-[rgba(255,255,255,0.15)] transition-colors duration-300 cursor-pointer"
  };

  return (
    <motion.div 
      className={cn(baseStyles, variants[variant], className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      {...props}
    >
      {/* Glossy Reflection Effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  );
};

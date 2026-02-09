import React from 'react';
import { MysticBackground } from '../ui/MysticBackground';
import { motion } from 'framer-motion';

interface SanctuaryLayoutProps {
  children: React.ReactNode;
}

export const SanctuaryLayout = ({ children }: SanctuaryLayoutProps) => {
  return (
    <div className="relative min-h-screen w-full text-[var(--color-starlight)] font-sans selection:bg-[var(--color-nebula-purple-glow)] selection:text-white">
      <MysticBackground />
      
      {/* Header / Nav */}
      <header className="fixed top-0 left-0 right-0 z-50 px-6 py-4 flex items-center justify-between border-b border-[var(--glass-border)] bg-[var(--glass-bg)] backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[var(--color-nebula-purple)] to-[var(--color-ethereal-gold)] shadow-[0_0_15px_var(--color-nebula-purple-glow)]" />
          <h1 className="text-xl font-serif font-bold tracking-wider text-[var(--color-starlight)]">
            Divine Daily <span className="text-[var(--color-ethereal-gold)] text-sm font-normal ml-1">· 数字圣所</span>
          </h1>
        </div>
        
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-[var(--color-starlight-dim)]">
          <a href="/" className="hover:text-[var(--color-starlight)] transition-colors">占卜</a>
          <a href="/tarot" className="hover:text-[var(--color-starlight)] transition-colors">塔罗</a>
          <a href="/history" className="hover:text-[var(--color-starlight)] transition-colors">历史</a>
          <a href="/configs" className="hover:text-[var(--color-starlight)] transition-colors">配置</a>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 pt-24 pb-12 px-4 md:px-8 max-w-7xl mx-auto flex flex-col min-h-[calc(100vh-6rem)]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="flex-1 flex flex-col"
        >
          {children}
        </motion.div>
      </main>
      
      {/* Footer */}
      <footer className="relative z-10 py-6 text-center text-xs text-[var(--color-starlight-dim)]/40">
        <p>© 2026 Divine Daily. All paths lead inward.</p>
      </footer>
    </div>
  );
};

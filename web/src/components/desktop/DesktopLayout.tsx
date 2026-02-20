import React from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import './DesktopLayout.css';

interface DesktopLayoutProps {
  children: React.ReactNode;
}

export const DesktopLayout: React.FC<DesktopLayoutProps> = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);

  return (
    <div className="desktop-layout">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      <div className={`desktop-layout__main ${sidebarCollapsed ? 'desktop-layout__main--expanded' : ''}`}>
        <TopBar />
        <main className="desktop-layout__content">
          {children}
        </main>
      </div>
    </div>
  );
};


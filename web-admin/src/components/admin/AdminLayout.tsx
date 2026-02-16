import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useResponsive } from '../../hooks/useResponsive';
import AdminSidebar from './AdminSidebar';
import AdminHeader from './AdminHeader';
import AdminMobileNav from './AdminMobileNav';
import './AdminLayout.css';

export default function AdminLayout() {
  const { isMobile } = useResponsive();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="admin-layout">
      {/* 侧边栏 */}
      <AdminSidebar 
        isOpen={sidebarOpen} 
        onClose={closeSidebar}
        isMobile={isMobile}
      />
      
      {/* 主内容区 */}
      <div className="admin-main">
        <AdminHeader 
          onMenuClick={toggleSidebar}
          isMobile={isMobile}
        />
        
        <div className="admin-content">
          <Outlet />
        </div>
      </div>

      {/* 移动端底部导航 */}
      {isMobile && <AdminMobileNav />}
      
      {/* 遮罩层（移动端侧边栏打开时） */}
      {isMobile && sidebarOpen && (
        <div 
          className="admin-overlay" 
          onClick={closeSidebar}
        />
      )}
    </div>
  );
}

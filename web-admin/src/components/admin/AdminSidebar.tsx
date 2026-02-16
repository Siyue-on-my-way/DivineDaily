import { NavLink } from 'react-router-dom';
import './AdminSidebar.css';

interface AdminSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isMobile: boolean;
}

export default function AdminSidebar({ isOpen, onClose, isMobile }: AdminSidebarProps) {
  const menuItems = [
    { path: '/admin', label: '管理首页', icon: '🏠', exact: true },
    { path: '/admin/llm-config', label: 'LLM 配置', icon: '🤖' },
    { path: '/admin/assistant-config', label: 'Assistant 配置', icon: '📝' },
  ];

  const handleNavClick = () => {
    if (isMobile) {
      onClose();
    }
  };

  return (
    <aside className={`admin-sidebar ${isOpen ? 'open' : ''}`}>
      <div className="admin-sidebar-header">
        <h2>管理中心</h2>
        {isMobile && (
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        )}
      </div>

      <nav className="admin-sidebar-nav">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.exact}
            className={({ isActive }) => 
              `nav-item ${isActive ? 'active' : ''}`
            }
            onClick={handleNavClick}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="admin-sidebar-footer">
        <NavLink to="/" className="back-to-app">
          ← 返回主应用
        </NavLink>
      </div>
    </aside>
  );
}

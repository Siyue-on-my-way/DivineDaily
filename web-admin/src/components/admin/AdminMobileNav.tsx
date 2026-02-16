import { NavLink } from 'react-router-dom';
import './AdminMobileNav.css';

export default function AdminMobileNav() {
  const navItems = [
    { path: '/admin', label: '首页', icon: '🏠', exact: true },
    { path: '/admin/llm-config', label: 'LLM', icon: '🤖' },
    { path: '/admin/prompt-config', label: 'Prompt', icon: '📝' },
  ];

  return (
    <nav className="admin-mobile-nav">
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          end={item.exact}
          className={({ isActive }) => 
            `mobile-nav-item ${isActive ? 'active' : ''}`
          }
        >
          <span className="mobile-nav-icon">{item.icon}</span>
          <span className="mobile-nav-label">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

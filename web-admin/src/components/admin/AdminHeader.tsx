import './AdminHeader.css';

interface AdminHeaderProps {
  onMenuClick: () => void;
  isMobile: boolean;
}

export default function AdminHeader({ onMenuClick, isMobile }: AdminHeaderProps) {
  return (
    <header className="admin-header">
      <div className="admin-header-left">
        {isMobile && (
          <button className="menu-btn" onClick={onMenuClick}>
            ☰
          </button>
        )}
        <h1 className="admin-title">Divine Daily 管理后台</h1>
      </div>

      <div className="admin-header-right">
        <div className="admin-user">
          <span className="user-avatar">👤</span>
          <span className="user-name">管理员</span>
        </div>
      </div>
    </header>
  );
}

import { useState } from 'react';
import { User } from '../../types/user';
import { formatUserRole, formatUserStatus, getUserStatusColor, getUserRoleColor, formatDateTime, formatRelativeTime } from '../../utils/userUtils';
import './UserTable.css';

interface UserTableProps {
  users: User[];
  loading?: boolean;
  selectedIds: number[];
  onSelectChange: (ids: number[]) => void;
  onEdit: (user: User) => void;
  onDelete: (user: User) => void;
  onViewDetail: (user: User) => void;
  onResetPassword: (user: User) => void;
  currentPage: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onSort?: (field: string, direction: 'asc' | 'desc') => void;
}

export default function UserTable({
  users,
  loading = false,
  selectedIds,
  onSelectChange,
  onEdit,
  onDelete,
  onViewDetail,
  onResetPassword,
  currentPage,
  pageSize,
  total,
  onPageChange,
  onSort,
}: UserTableProps) {
  const [sortField, setSortField] = useState<string>('created_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectChange(users.map(u => u.id));
    } else {
      onSelectChange([]);
    }
  };

  const handleSelectOne = (userId: number, checked: boolean) => {
    if (checked) {
      onSelectChange([...selectedIds, userId]);
    } else {
      onSelectChange(selectedIds.filter(id => id !== userId));
    }
  };

  const handleSort = (field: string) => {
    const newDirection = sortField === field && sortDirection === 'desc' ? 'asc' : 'desc';
    setSortField(field);
    setSortDirection(newDirection);
    onSort?.(field, newDirection);
  };

  const totalPages = Math.ceil(total / pageSize);
  const isAllSelected = users.length > 0 && selectedIds.length === users.length;
  const isSomeSelected = selectedIds.length > 0 && selectedIds.length < users.length;

  if (loading) {
    return (
      <div className="user-table-loading">
        <div className="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div className="user-table-empty">
        <div className="empty-icon">👥</div>
        <p>暂无用户数据</p>
      </div>
    );
  }

  return (
    <div className="user-table-container">
      <div className="user-table-wrapper">
        <table className="user-table">
          <thead>
            <tr>
              <th className="checkbox-cell">
                <input
                  type="checkbox"
                  checked={isAllSelected}
                  ref={input => {
                    if (input) input.indeterminate = isSomeSelected;
                  }}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                />
              </th>
              <th onClick={() => handleSort('id')} className="sortable">
                ID {sortField === 'id' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('username')} className="sortable">
                用户名 {sortField === 'username' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>邮箱</th>
              <th>手机号</th>
              <th>昵称</th>
              <th>角色</th>
              <th>状态</th>
              <th onClick={() => handleSort('last_login_at')} className="sortable">
                最后登录 {sortField === 'last_login_at' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('created_at')} className="sortable">
                注册时间 {sortField === 'created_at' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="actions-cell">操作</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className={selectedIds.includes(user.id) ? 'selected' : ''}>
                <td className="checkbox-cell">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(user.id)}
                    onChange={(e) => handleSelectOne(user.id, e.target.checked)}
                  />
                </td>
                <td>{user.id}</td>
                <td className="username-cell">
                  <div className="user-info">
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.username} className="user-avatar" />
                    ) : (
                      <div className="user-avatar-placeholder">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <span className="username">{user.username}</span>
                  </div>
                </td>
                <td>{user.email || '-'}</td>
                <td>{user.phone || '-'}</td>
                <td>{user.nickname || '-'}</td>
                <td>
                  <span className="role-badge" style={{ backgroundColor: getUserRoleColor(user.role) }}>
                    {formatUserRole(user.role)}
                  </span>
                </td>
                <td>
                  <span className="status-badge" style={{ backgroundColor: getUserStatusColor(user.status) }}>
                    {formatUserStatus(user.status)}
                  </span>
                </td>
                <td className="time-cell" title={formatDateTime(user.last_login_at)}>
                  {formatRelativeTime(user.last_login_at)}
                </td>
                <td className="time-cell" title={formatDateTime(user.created_at)}>
                  {formatDateTime(user.created_at)}
                </td>
                <td className="actions-cell">
                  <div className="action-buttons">
                    <button
                      className="action-btn view-btn"
                      onClick={() => onViewDetail(user)}
                      title="查看详情"
                    >
                      👁️
                    </button>
                    <button
                      className="action-btn edit-btn"
                      onClick={() => onEdit(user)}
                      title="编辑"
                    >
                      ✏️
                    </button>
                    <button
                      className="action-btn reset-btn"
                      onClick={() => onResetPassword(user)}
                      title="重置密码"
                    >
                      🔑
                    </button>
                    <button
                      className="action-btn delete-btn"
                      onClick={() => onDelete(user)}
                      title="删除"
                      disabled={user.id === 1}
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 分页 */}
      <div className="user-table-pagination">
        <div className="pagination-info">
          共 {total} 条记录，第 {currentPage} / {totalPages} 页
        </div>
        <div className="pagination-controls">
          <button
            className="pagination-btn"
            onClick={() => onPageChange(1)}
            disabled={currentPage === 1}
          >
            首页
          </button>
          <button
            className="pagination-btn"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            上一页
          </button>
          <span className="pagination-current">第 {currentPage} 页</span>
          <button
            className="pagination-btn"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
          >
            下一页
          </button>
          <button
            className="pagination-btn"
            onClick={() => onPageChange(totalPages)}
            disabled={currentPage >= totalPages}
          >
            末页
          </button>
        </div>
      </div>
    </div>
  );
}


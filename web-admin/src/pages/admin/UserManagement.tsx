import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, UserStats, UserListParams } from '../../types/user';
import { getUserList, getUserStats, deleteUser, batchDeleteUsers, exportUsersToCSV } from '../../api/user';
import UserStatsCard from '../../components/user/UserStatsCard';
import UserSearchBar from '../../components/user/UserSearchBar';
import UserFilterPanel from '../../components/user/UserFilterPanel';
import UserTable from '../../components/user/UserTable';
import { useToast } from '../../hooks/useToast';
import './UserManagement.css';

export default function UserManagement() {
  const navigate = useNavigate();
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  
  // 分页和筛选
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filters, setFilters] = useState<Partial<UserListParams>>({});
  
  const { showToast } = useToast();

  // 加载用户列表
  const loadUsers = async () => {
    setLoading(true);
    try {
      const params: UserListParams = {
        page: currentPage,
        page_size: pageSize,
        search: searchKeyword || undefined,
        ...filters,
      };
      
      const response = await getUserList(params);
      setUsers(response.users);
      setTotal(response.total);
    } catch (error: any) {
      showToast(error.response?.data?.detail || '加载用户列表失败', 'error');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const loadStats = async () => {
    setStatsLoading(true);
    try {
      const data = await getUserStats();
      setStats(data);
    } catch (error: any) {
      showToast(error.response?.data?.detail || '加载统计数据失败', 'error');
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [currentPage, searchKeyword, filters]);

  useEffect(() => {
    loadStats();
  }, []);

  // 搜索
  const handleSearch = (keyword: string) => {
    setSearchKeyword(keyword);
    setCurrentPage(1);
  };

  // 筛选
  const handleFilter = (newFilters: Partial<UserListParams>) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  // 重置筛选
  const handleResetFilter = () => {
    setFilters({});
    setCurrentPage(1);
  };

  // 排序
  const handleSort = (field: string, direction: 'asc' | 'desc') => {
    setFilters({
      ...filters,
      order_by: field,
      order_direction: direction,
    });
  };

  // 导出
  const handleExport = () => {
    exportUsersToCSV(users);
    showToast('导出成功', 'success');
  };

  // 创建用户
  const handleCreate = () => {
    // TODO: 打开创建用户弹窗
    showToast('创建用户功能开发中...', 'info');
  };

  // 编辑用户
  const handleEdit = (user: User) => {
    // TODO: 打开编辑用户弹窗
    showToast(`编辑用户: ${user.username}`, 'info');
  };

  // 删除用户
  const handleDelete = async (user: User) => {
    if (!confirm(`确定要删除用户 "${user.username}" 吗？此操作不可恢复！`)) {
      return;
    }

    try {
      await deleteUser(user.id);
      showToast('删除成功', 'success');
      loadUsers();
      loadStats();
    } catch (error: any) {
      showToast(error.response?.data?.detail || '删除失败', 'error');
    }
  };

  // 查看详情
  const handleViewDetail = (user: User) => {
    navigate(`/admin/users/${user.id}`);
  };

  // 重置密码
  const handleResetPassword = (user: User) => {
    // TODO: 打开重置密码弹窗
    showToast(`重置密码: ${user.username}`, 'info');
  };

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedIds.length === 0) {
      showToast('请先选择要删除的用户', 'warning');
      return;
    }

    if (!confirm(`确定要删除选中的 ${selectedIds.length} 个用户吗？此操作不可恢复！`)) {
      return;
    }

    try {
      const result = await batchDeleteUsers(selectedIds);
      showToast(`成功删除 ${result.deleted_count} 个用户${result.skipped_count > 0 ? `，跳过 ${result.skipped_count} 个` : ''}`, 'success');
      setSelectedIds([]);
      loadUsers();
      loadStats();
    } catch (error: any) {
      showToast(error.response?.data?.detail || '批量删除失败', 'error');
    }
  };

  // 批量启用/禁用
  const handleBatchChangeStatus = async (status: 0 | 1) => {
    if (selectedIds.length === 0) {
      showToast('请先选择要操作的用户', 'warning');
      return;
    }

    // TODO: 调用批量修改状态 API
    showToast(`批量${status === 1 ? '启用' : '禁用'}功能开发中...`, 'info');
  };

  return (
    <div className="user-management-page">
      <div className="page-header">
        <h1>用户管理</h1>
        <p>管理系统用户账号、权限和状态</p>
      </div>

      {/* 统计卡片 */}
      <UserStatsCard stats={stats} loading={statsLoading} />

      {/* 搜索栏 */}
      <UserSearchBar
        onSearch={handleSearch}
        onExport={handleExport}
        onCreate={handleCreate}
      />

      {/* 筛选面板 */}
      <UserFilterPanel
        onFilter={handleFilter}
        onReset={handleResetFilter}
      />

      {/* 批量操作栏 */}
      {selectedIds.length > 0 && (
        <div className="batch-operation-bar">
          <div className="batch-info">
            已选择 <strong>{selectedIds.length}</strong> 个用户
          </div>
          <div className="batch-actions">
            <button
              className="batch-btn enable-btn"
              onClick={() => handleBatchChangeStatus(1)}
            >
              批量启用
            </button>
            <button
              className="batch-btn disable-btn"
              onClick={() => handleBatchChangeStatus(0)}
            >
              批量禁用
            </button>
            <button
              className="batch-btn delete-btn"
              onClick={handleBatchDelete}
            >
              批量删除
            </button>
            <button
              className="batch-btn cancel-btn"
              onClick={() => setSelectedIds([])}
            >
              取消选择
            </button>
          </div>
        </div>
      )}

      {/* 用户表格 */}
      <UserTable
        users={users}
        loading={loading}
        selectedIds={selectedIds}
        onSelectChange={setSelectedIds}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onViewDetail={handleViewDetail}
        onResetPassword={handleResetPassword}
        currentPage={currentPage}
        pageSize={pageSize}
        total={total}
        onPageChange={setCurrentPage}
        onSort={handleSort}
      />
    </div>
  );
}

/**
 * 用户管理 API
 */

import axios from '../lib/axios';

// ==================== 类型定义 ====================

export interface User {
  id: number;
  username: string;
  email?: string;
  phone?: string;
  nickname?: string;
  avatar?: string;
  role: 'admin' | 'normal';
  status: 0 | 1;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

export interface UserDetail extends User {
  divination_count: number;
  iching_count: number;
  tarot_count: number;
  fortune_count: number;
  last_divination_at?: string;
  birth_date?: string;
  animal?: string;
  zodiac_sign?: string;
}

export interface UserListParams {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  status?: number;
  order_by?: string;
  order_direction?: 'asc' | 'desc';
  start_date?: string;
  end_date?: string;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UserStats {
  total_users: number;
  admin_users: number;
  normal_users: number;
  active_users: number;
  disabled_users: number;
  today_new_users: number;
  week_new_users: number;
  month_new_users: number;
  active_7days: number;
  active_30days: number;
}

export interface AuditLog {
  id: number;
  operator_id: number;
  operator_name: string;
  action: string;
  target_user_id?: number;
  target_username?: string;
  details?: any;
  ip_address?: string;
  created_at: string;
}

export interface LoginHistory {
  id: number;
  user_id: number;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
  expires_at: string;
}

export interface UserDivination {
  id: string;
  version: string;
  question: string;
  event_type?: string;
  status: string;
  result_summary?: string;
  created_at: string;
}

export interface CreateUserData {
  username: string;
  email?: string;
  phone?: string;
  password: string;
  nickname?: string;
  avatar?: string;
  role: 'admin' | 'normal';
  status: 0 | 1;
}

export interface UpdateUserData {
  username?: string;
  email?: string;
  phone?: string;
  nickname?: string;
  avatar?: string;
  role?: 'admin' | 'normal';
  status?: 0 | 1;
}

// ==================== API 函数 ====================

/**
 * 获取用户列表
 */
export const getUserList = async (params: UserListParams = {}): Promise<UserListResponse> => {
  const response = await axios.get('/admin/users', { params });
  return response.data;
};

/**
 * 获取用户详情
 */
export const getUserDetail = async (userId: number): Promise<UserDetail> => {
  const response = await axios.get(`/admin/users/${userId}`);
  return response.data;
};

/**
 * 创建用户
 */
export const createUser = async (data: CreateUserData): Promise<User> => {
  const response = await axios.post('/admin/users', data);
  return response.data;
};

/**
 * 更新用户
 */
export const updateUser = async (userId: number, data: UpdateUserData): Promise<User> => {
  const response = await axios.put(`/admin/users/${userId}`, data);
  return response.data;
};

/**
 * 删除用户
 */
export const deleteUser = async (userId: number): Promise<void> => {
  await axios.delete(`/admin/users/${userId}`);
};

/**
 * 批量删除用户
 */
export const batchDeleteUsers = async (userIds: number[]): Promise<{ deleted_count: number; skipped_count: number }> => {
  const response = await axios.delete('/admin/users/batch', { data: { user_ids: userIds } });
  return response.data;
};

/**
 * 重置密码
 */
export const resetPassword = async (
  userId: number,
  data: { new_password?: string; generate_random?: boolean; send_email?: boolean }
): Promise<{ success: boolean; new_password?: string }> => {
  const response = await axios.post(`/admin/users/${userId}/reset-password`, data);
  return response.data;
};

/**
 * 修改角色
 */
export const changeRole = async (userId: number, role: 'admin' | 'normal'): Promise<User> => {
  const response = await axios.put(`/admin/users/${userId}/role`, { role });
  return response.data;
};

/**
 * 修改状态
 */
export const changeStatus = async (
  userId: number,
  status: 0 | 1,
  reason?: string
): Promise<User> => {
  const response = await axios.put(`/admin/users/${userId}/status`, { status, reason });
  return response.data;
};

/**
 * 批量修改状态
 */
export const batchChangeStatus = async (
  userIds: number[],
  status: 0 | 1,
  reason?: string
): Promise<{ updated_count: number; skipped_count: number }> => {
  const response = await axios.put('/admin/users/batch/status', { user_ids: userIds, status, reason });
  return response.data;
};

/**
 * 获取用户统计
 */
export const getUserStats = async (): Promise<UserStats> => {
  const response = await axios.get('/admin/users/stats');
  return response.data;
};

/**
 * 获取用户占卜历史
 */
export const getUserDivinations = async (
  userId: number,
  page: number = 1,
  pageSize: number = 20
): Promise<{ divinations: UserDivination[]; total: number }> => {
  const response = await axios.get(`/admin/users/${userId}/divinations`, {
    params: { page, page_size: pageSize }
  });
  return response.data;
};

/**
 * 获取用户登录历史
 */
export const getUserLoginHistory = async (
  userId: number,
  page: number = 1,
  pageSize: number = 20
): Promise<{ history: LoginHistory[]; total: number }> => {
  const response = await axios.get(`/admin/users/${userId}/login-history`, {
    params: { page, page_size: pageSize }
  });
  return response.data;
};

/**
 * 获取操作日志
 */
export const getAuditLogs = async (params: {
  page?: number;
  page_size?: number;
  operator_id?: number;
  target_user_id?: number;
  action?: string;
  start_date?: string;
  end_date?: string;
} = {}): Promise<{ logs: AuditLog[]; total: number; page: number; page_size: number }> => {
  const response = await axios.get('/admin/audit-logs', { params });
  return response.data;
};

/**
 * 导出用户数据为 CSV
 */
export const exportUsersToCSV = (users: User[]): void => {
  if (!users || users.length === 0) {
    return;
  }

  // CSV 表头
  const headers = ['ID', '用户名', '邮箱', '手机', '昵称', '角色', '状态', '最后登录', '创建时间'];
  
  // CSV 数据行
  const rows = users.map(user => [
    user.id,
    user.username,
    user.email || '',
    user.phone || '',
    user.nickname || '',
    user.role === 'admin' ? '管理员' : '普通用户',
    user.status === 1 ? '正常' : '禁用',
    user.last_login_at || '',
    user.created_at,
  ]);

  // 组合 CSV 内容
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  // 创建 Blob 并下载
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `users_${new Date().toISOString().slice(0, 10)}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export default {
  getUserList,
  getUserDetail,
  createUser,
  updateUser,
  deleteUser,
  batchDeleteUsers,
  resetPassword,
  changeRole,
  changeStatus,
  batchChangeStatus,
  getUserStats,
  getUserDivinations,
  getUserLoginHistory,
  getAuditLogs,
  exportUsersToCSV,
};

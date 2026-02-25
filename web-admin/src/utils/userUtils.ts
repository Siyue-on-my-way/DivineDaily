/**
 * 用户管理工具函数
 */

/**
 * 格式化用户角色
 */
export const formatUserRole = (role: string): string => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    normal: '普通用户',
  };
  return roleMap[role] || role;
};

/**
 * 格式化用户状态
 */
export const formatUserStatus = (status: number): string => {
  return status === 1 ? '正常' : '禁用';
};

/**
 * 获取用户状态颜色
 */
export const getUserStatusColor = (status: number): string => {
  return status === 1 ? '#4CAF50' : '#F44336';
};

/**
 * 获取用户角色颜色
 */
export const getUserRoleColor = (role: string): string => {
  const colorMap: Record<string, string> = {
    admin: '#FF9800',
    normal: '#2196F3',
  };
  return colorMap[role] || '#9E9E9E';
};

/**
 * 验证用户名
 */
export const validateUsername = (username: string): { valid: boolean; message?: string } => {
  if (!username) {
    return { valid: false, message: '用户名不能为空' };
  }
  if (username.length < 3 || username.length > 50) {
    return { valid: false, message: '用户名长度必须在 3-50 个字符之间' };
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return { valid: false, message: '用户名只能包含字母、数字和下划线' };
  }
  return { valid: true };
};

/**
 * 验证邮箱
 */
export const validateEmail = (email: string): { valid: boolean; message?: string } => {
  if (!email) {
    return { valid: true }; // 邮箱可选
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, message: '邮箱格式不正确' };
  }
  return { valid: true };
};

/**
 * 验证手机号
 */
export const validatePhone = (phone: string): { valid: boolean; message?: string } => {
  if (!phone) {
    return { valid: true }; // 手机号可选
  }
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(phone)) {
    return { valid: false, message: '手机号格式不正确' };
  }
  return { valid: true };
};

/**
 * 验证密码
 */
export const validatePassword = (password: string): { valid: boolean; message?: string } => {
  if (!password) {
    return { valid: false, message: '密码不能为空' };
  }
  if (password.length < 8 || password.length > 50) {
    return { valid: false, message: '密码长度必须在 8-50 个字符之间' };
  }
  if (!/[A-Z]/.test(password)) {
    return { valid: false, message: '密码必须包含至少一个大写字母' };
  }
  if (!/[a-z]/.test(password)) {
    return { valid: false, message: '密码必须包含至少一个小写字母' };
  }
  if (!/\d/.test(password)) {
    return { valid: false, message: '密码必须包含至少一个数字' };
  }
  return { valid: true };
};

/**
 * 生成随机密码
 */
export const generateRandomPassword = (length: number = 12): string => {
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lowercase = 'abcdefghijklmnopqrstuvwxyz';
  const numbers = '0123456789';
  const allChars = uppercase + lowercase + numbers;
  
  let password = '';
  
  // 确保包含至少一个大写字母、小写字母和数字
  password += uppercase[Math.floor(Math.random() * uppercase.length)];
  password += lowercase[Math.floor(Math.random() * lowercase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  
  // 填充剩余字符
  for (let i = 3; i < length; i++) {
    password += allChars[Math.floor(Math.random() * allChars.length)];
  }
  
  // 打乱顺序
  return password.split('').sort(() => Math.random() - 0.5).join('');
};

/**
 * 格式化日期时间
 */
export const formatDateTime = (dateString?: string): string => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

/**
 * 格式化相对时间
 */
export const formatRelativeTime = (dateString?: string): string => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 7) {
    return formatDateTime(dateString);
  } else if (days > 0) {
    return `${days} 天前`;
  } else if (hours > 0) {
    return `${hours} 小时前`;
  } else if (minutes > 0) {
    return `${minutes} 分钟前`;
  } else {
    return '刚刚';
  }
};

/**
 * 格式化操作类型
 */
export const formatActionType = (action: string): string => {
  const actionMap: Record<string, string> = {
    create_user: '创建用户',
    update_user: '更新用户',
    delete_user: '删除用户',
    batch_delete_users: '批量删除用户',
    reset_password: '重置密码',
    change_role: '修改角色',
    change_status: '修改状态',
    batch_change_status: '批量修改状态',
  };
  return actionMap[action] || action;
};

/**
 * 获取操作类型颜色
 */
export const getActionTypeColor = (action: string): string => {
  if (action.includes('create')) return '#4CAF50';
  if (action.includes('update') || action.includes('change')) return '#2196F3';
  if (action.includes('delete')) return '#F44336';
  if (action.includes('reset')) return '#FF9800';
  return '#9E9E9E';
};

/**
 * 复制到剪贴板
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('复制失败:', error);
    return false;
  }
};

/**
 * 下载文件
 */
export const downloadFile = (content: string, filename: string, type: string = 'text/plain') => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * 导出用户列表为 CSV
 */
export const exportUsersToCSV = (users: any[]) => {
  const headers = ['ID', '用户名', '邮箱', '手机号', '昵称', '角色', '状态', '注册时间', '最后登录'];
  const rows = users.map(user => [
    user.id,
    user.username,
    user.email || '',
    user.phone || '',
    user.nickname || '',
    formatUserRole(user.role),
    formatUserStatus(user.status),
    formatDateTime(user.created_at),
    formatDateTime(user.last_login_at),
  ]);
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');
  
  // 添加 BOM 以支持中文
  const bom = '\uFEFF';
  downloadFile(bom + csvContent, `用户列表_${new Date().toISOString().split('T')[0]}.csv`, 'text/csv;charset=utf-8');
};


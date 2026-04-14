/**
 * 用户管理相关类型定义
 */

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

export interface UserDivinationDetail extends UserDivination {
  user_id?: string;
  result_detail?: string;
  result_data?: {
    hexagram_info?: {
      number?: number;
      name?: string;
      upper_trigram?: string;
      lower_trigram?: string;
      outcome?: string;
      wuxing?: string;
      changing_lines?: number[];
      line_values?: number[];
    };
    recommendations?: Array<{ title?: string; content?: string }>;
    yarrow_trace?: {
      method?: string;
      lines?: Array<{
        line_index?: number;
        line_value?: number;
        line_type?: string;
        is_changing?: boolean;
      }>;
    };
    [key: string]: any;
  };
  updated_at?: string;
}


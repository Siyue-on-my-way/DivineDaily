/**
 * 占卜相关类型定义
 * 
 * 包含占卜结果、会话、卦象信息等核心数据结构
 */

/**
 * 占卜状态枚举
 */
export type DivinationStatus = 'processing' | 'completed' | 'failed' | 'pending';

/**
 * 占卜版本类型
 */
export type DivinationVersion = 'CN' | 'Global' | 'TAROT';

/**
 * 事件类型
 */
export type EventType = 'decision' | 'career' | 'relationship' | 'fortune' | 'knowledge' | 'health' | 'wealth' | 'general';

/**
 * 占卜结果
 */
export interface DivinationResult {
  /** 会话ID */
  session_id: string;
  /** 占卜结果（吉/凶/平） */
  outcome?: string;
  /** 标题 */
  title?: string;
  /** 牌阵类型 */
  spread?: string;
  /** 塔罗牌抽取结果 */
  cards?: TarotCardDraw[];
  
  /** 结果摘要（50-100字） */
  summary: string;
  
  /** 详细内容（点击展开） */
  detail: string;
  
  /** 卦象信息（决策类） */
  hexagram_info?: HexagramInfo;
  /** 推荐列表（推荐类） */
  recommendations?: RecommendationItem[];
  /** 每日运势（运势类） */
  daily_fortune?: DailyFortuneInfo;
  /** 大衍筮法起卦过程（仅周易六爻） */
  yarrow_trace?: YarrowProcessTrace;
  
  /** 原始数据 */
  raw_data?: string;
  /** 场景建议 */
  scene_advice?: SceneAdviceItem[];
  /** 是否需要追问 */
  needs_follow_up: boolean;
  /** 追问问题 */
  follow_up_question?: FollowUpQuestion;
  /** 创建时间 */
  created_at: string;
  /** 状态 */
  status?: DivinationStatus;
}

/**
 * 卦象信息
 */
export interface HexagramInfo {
  /** 卦序号（1-64） */
  number: number;
  /** 卦名 */
  name: string;
  /** 上卦 */
  upper_trigram: string;
  /** 下卦 */
  lower_trigram: string;
  /** 吉凶 */
  outcome: string;
  /** 卦辞摘要 */
  summary: string;
  /** 五行 */
  wuxing: string;
  /** 变爻位置 */
  changing_lines?: number[];
  /** 六爻值（自下而上，6/7/8/9） */
  line_values?: number[];
}

/**
 * 大衍筮法：单次变的记录
 */
export interface YarrowChangeStep {
  /** 第几变（1-3） */
  step_index: number;
  /** 本变开始前蓍草数 */
  stalks_before: number;
  /** 左手蓍草数 */
  left_pile: number;
  /** 右手蓍草数（挂一前） */
  right_pile_before_hang: number;
  /** 挂一数量（固定为1） */
  right_hang_one: number;
  /** 右手蓍草数（挂一后） */
  right_pile_after_hang: number;
  /** 左手取四余数（0按4计） */
  left_remainder: number;
  /** 右手取四余数（0按4计） */
  right_remainder: number;
  /** 本次去除总数 */
  removed: number;
  /** 本变结束后蓍草数 */
  stalks_after: number;
}

/**
 * 大衍筮法：单爻生成过程
 */
export interface YarrowLineTrace {
  /** 爻位（1-6，自下而上） */
  line_index: number;
  /** 初始蓍草数（通常49） */
  initial_stalks: number;
  /** 三变过程 */
  changes: YarrowChangeStep[];
  /** 三变后剩余蓍草数 */
  final_stalks: number;
  /** 爻值（6/7/8/9） */
  line_value: number;
  /** 爻类型（老阴/少阳/少阴/老阳） */
  line_type: string;
  /** 是否变爻 */
  is_changing: boolean;
}

/**
 * 大衍筮法：完整起卦过程
 */
export interface YarrowProcessTrace {
  /** 起卦方法，固定为 "dayan_yarrow" */
  method: string;
  /** 总蓍草数（50） */
  total_stalks: number;
  /** 参与演算蓍草数（49） */
  effective_stalks: number;
  /** 六爻过程（自下而上） */
  lines: YarrowLineTrace[];
}

/**
 * 推荐项
 */
export interface RecommendationItem {
  /** 推荐内容 */
  content: string;
  /** 推荐理由 */
  reason: string;
}

/**
 * 每日运势信息
 */
export interface DailyFortuneInfo {
  /** 综合评分 */
  overall_score: number;
  /** 财运评分 */
  wealth_score: number;
  /** 事业评分 */
  career_score: number;
  /** 爱情评分 */
  love_score: number;
  /** 健康评分 */
  health_score: number;
  /** 运势内容 */
  content: string;
  
  /** 幸运颜色 */
  lucky_color: string;
  /** 幸运数字 */
  lucky_number: number;
  /** 幸运方位 */
  lucky_direction: string;
  /** 幸运时辰 */
  lucky_time: string;
  
  /** 宜（逗号分隔） */
  yi: string;
  /** 忌（逗号分隔） */
  ji: string;
  
  /** 节气 */
  solar_term: string;
  /** 节日 */
  festival: string;
}

/**
 * 场景建议项
 */
export interface SceneAdviceItem {
  /** 标题 */
  title: string;
  /** 内容 */
  content: string;
  /** 类型 */
  type: string;
}

/**
 * 追问问题
 */
export interface FollowUpQuestion {
  /** 问题ID */
  id: string;
  /** 会话ID */
  session_id: string;
  /** 问题内容 */
  question: string;
  /** 选项列表 */
  options?: string[];
}

/**
 * 塔罗牌抽取结果
 */
export interface TarotCardDraw {
  /** 牌名 */
  name: string;
  /** 英文名 */
  name_en?: string;
  /** 位置 */
  position: string;
  /** 是否逆位 */
  is_reversed: boolean;
}

/**
 * 创建占卜请求
 */
export interface CreateDivinationRequest {
  /** 用户ID */
  user_id: string;
  /** 问题 */
  question: string;
  /** 事件类型 */
  event_type?: EventType;
  /** 版本 */
  version?: DivinationVersion;
  /** 方位 */
  orientation?: string;
  /** 牌阵 */
  spread?: string;
  /** 额外上下文信息（用于传递洗牌/切牌交互等） */
  context?: any;
}

/**
 * 占卜会话
 */
export interface DivinationSession {
  /** 会话ID */
  id: string;
  /** 用户ID */
  user_id: string;
  /** 版本 */
  version: DivinationVersion;
  /** 问题 */
  question: string;
  /** 事件类型 */
  event_type: EventType;
  /** 方位 */
  orientation?: string;
  /** 牌阵 */
  spread?: string;
  /** 状态 */
  status: DivinationStatus;
  /** 追问次数 */
  follow_up_count: number;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at?: string;
  /** 占卜结果（可选） */
  outcome?: string;
}

/**
 * API 错误响应
 */
export interface DivinationError {
  /** 错误消息 */
  message: string;
  /** 错误代码 */
  code?: string;
  /** 详细信息 */
  detail?: string;
  /** HTTP 状态码 */
  statusCode?: number;
}

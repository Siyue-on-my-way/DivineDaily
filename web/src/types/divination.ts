// 占卜相关类型定义

export interface DivinationResult {
  session_id: string;
  outcome?: string; // 吉/凶/平（决策类）
  title?: string;
  spread?: string;
  cards?: TarotCardDraw[];
  
  // 结果卡内容（默认显示）
  summary: string; // 直接答案/推荐列表（50-100字）
  
  // 详情内容（点击展开）
  detail: string; // 算卦过程/推荐逻辑
  
  // 结构化数据（详情中使用）
  hexagram_info?: HexagramInfo; // 卦象信息（决策类）
  recommendations?: RecommendationItem[]; // 推荐列表（推荐类）
  daily_fortune?: DailyFortuneInfo; // 每日运势（运势类）
  
  raw_data?: string;
  scene_advice?: SceneAdviceItem[];
  needs_follow_up: boolean;
  follow_up_question?: FollowUpQuestion;
  created_at: string;
}

export interface HexagramInfo {
  number: number; // 卦序号（1-64）
  name: string; // 卦名
  upper_trigram: string; // 上卦
  lower_trigram: string; // 下卦
  outcome: string; // 吉/凶/平
  summary: string; // 卦辞摘要
  wuxing: string; // 五行
  changing_lines?: number[]; // 变爻位置
}

export interface RecommendationItem {
  content: string; // 推荐内容
  reason: string; // 推荐理由
}

export interface DailyFortuneInfo {
  id: number;
  user_id: string;
  date: string;
  score: number;
  summary: string;
  
  // 详细建议
  wealth: string;
  career: string;
  love: string;
  health: string;
  
  // 幸运指南
  lucky_color: string;
  lucky_number: string;
  lucky_direction: string;
  lucky_time: string;
  
  // 宜忌
  yi: string[];
  ji: string[];
  
  // 节气/节日
  solar_term: string;
  festival: string;
}

export interface SceneAdviceItem {
  title: string;
  content: string;
  type: string;
}

export interface FollowUpQuestion {
  id: string;
  session_id: string;
  question: string;
  options?: string[];
}

export interface TarotCardDraw {
  name: string;
  name_en?: string;
  position: string;
  is_reversed: boolean;
}

export interface CreateDivinationRequest {
  user_id: string;
  question: string;
  event_type?: string;
  version?: string;
  orientation?: string;
  spread?: string;
}

export interface DivinationSession {
  id: string;
  user_id: string;
  version: string;
  question: string;
  event_type: string;
  orientation?: string;
  spread?: string;
  status: string;
  follow_up_count: number;
  created_at: string;
  updated_at?: string;
}

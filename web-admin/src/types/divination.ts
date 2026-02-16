export interface DivinationResult {
  session_id: string;
  outcome?: string;
  title?: string;
  spread?: string;
  cards?: any[];
  summary: string;
  detail: string;
  hexagram_info?: any;
  recommendations?: any[];
  daily_fortune?: any;
  needs_follow_up: boolean;
  created_at: string;
}

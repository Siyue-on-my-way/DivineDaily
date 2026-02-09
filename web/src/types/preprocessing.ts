export interface QuestionContext {
  timestamp: string;
  location?: string;
  previous_sessions?: string[];
}

export interface PreprocessRequest {
  user_id: string;
  raw_question: string;
  context: QuestionContext;
}

export interface EnhancementSuggestion {
  type: string;
  message: string;
  auto_applied: boolean;
}

export interface PreprocessResponse {
  original_question: string;
  enhanced_question: string;
  use_enhanced: boolean;
  quality_score: number;
  quality_breakdown: {
    specificity: number;
    personal_relevance: number;
    decision_value: number;
    temporal_relevance: number;
    [key: string]: number;
  };
  suggestions: EnhancementSuggestion[];
  recommended_approach: string;
  intent?: string;
}

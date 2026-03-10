import axiosInstance from '../lib/axios';

/**
 * 问题质量评估请求参数
 */
export interface QuestionQualityRequest {
  /** 用户输入的问题文本 */
  question: string;
}

/**
 * 质量改进建议
 */
export interface QualitySuggestion {
  /** 建议类型 (e.g., 'specificity', 'personal_relevance') */
  type: string;
  /** 建议内容 */
  message: string;
  /** 优先级: 'high' | 'medium' | 'low' */
  priority: 'high' | 'medium' | 'low';
}

/**
 * 问题质量评估结果
 */
export interface QuestionQualityResult {
  /** 总体质量评分 (0-100) */
  overall_score: number;
  /** 具体性评分 (0-100) */
  specificity_score: number;
  /** 个人相关性评分 (0-100) */
  personal_relevance_score: number;
  /** 决策价值评分 (0-100) */
  decision_value_score: number;
  /** 时效性评分 (0-100) */
  temporal_relevance_score: number;
  /** 质量因子（用于计算评分的原始数据） */
  quality_factors: {
    /** 问题长度（字符数） */
    length: number;
    /** 是否包含问号 (0 或 1) */
    has_question_mark: number;
    /** 词语数量 */
    word_count: number;
  };
  /** 改进建议列表 */
  suggestions: QualitySuggestion[];
}

/**
 * 问题质量历史记录
 */
export interface QuestionQualityHistory {
  /** 记录ID */
  id: number;
  /** 原始问题 */
  original_question: string;
  /** 增强后的问题（可选） */
  enhanced_question?: string;
  /** 质量评分 */
  overall_score: number;
  /** 是否使用了增强版本 */
  used_enhanced: boolean;
  /** 创建时间 */
  created_at: string;
}

/**
 * API 错误响应
 */
export interface QuestionQualityError {
  /** 错误消息 */
  message: string;
  /** 错误代码（可选） */
  code?: string;
  /** 详细信息（可选） */
  detail?: string;
}

/**
 * 问题质量评估 API
 */
export const questionQualityApi = {
  /**
   * 评估问题质量
   * 
   * @param data - 包含问题文本的请求参数
   * @returns 问题质量评估结果
   * @throws {QuestionQualityError} 当评估失败时抛出错误
   */
  evaluate: async (data: QuestionQualityRequest): Promise<QuestionQualityResult> => {
    try {
      const response = await axiosInstance.post<QuestionQualityResult>(
        '/question_quality/evaluate', 
        data
      );
      return response.data;
    } catch (error: any) {
      throw {
        message: error.response?.data?.message || '质量评估失败',
        code: error.response?.data?.code,
        detail: error.response?.data?.detail || error.message
      } as QuestionQualityError;
    }
  },

  /**
   * 获取问题质量历史记录
   * 
   * @param userId - 用户ID
   * @param limit - 返回记录数量限制，默认20条
   * @returns 历史记录列表
   * @throws {QuestionQualityError} 当获取失败时抛出错误
   */
  getHistory: async (userId: number, limit: number = 20): Promise<QuestionQualityHistory[]> => {
    try {
      const response = await axiosInstance.get<QuestionQualityHistory[]>(
        '/question_quality/history',
        {
          params: { user_id: userId, limit }
        }
      );
      return response.data;
    } catch (error: any) {
      throw {
        message: error.response?.data?.message || '获取历史记录失败',
        code: error.response?.data?.code,
        detail: error.response?.data?.detail || error.message
      } as QuestionQualityError;
    }
  }
};

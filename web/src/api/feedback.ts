import axiosInstance from '../lib/axios';

export interface FeedbackData {
  rating: number;
  comment?: string;
  tags: string[];
  isHelpful?: boolean;
}

export interface DivinationFeedbackRequest extends FeedbackData {
  session_id: string;
  feedback_type: 'quality' | 'accuracy' | 'helpfulness';
}

export interface QualityFeedbackRequest {
  quality_history_id: number;
  rating: number;
  comment?: string;
}

export interface FeedbackResponse {
  id: number;
  message: string;
  success: boolean;
}

export const feedbackApi = {
  submitDivinationFeedback: async (
    data: DivinationFeedbackRequest
  ): Promise<FeedbackResponse> => {
    const response = await axiosInstance.post('/feedback/divination', data);
    return response.data;
  },

  submitQualityFeedback: async (
    data: QualityFeedbackRequest
  ): Promise<FeedbackResponse> => {
    const response = await axiosInstance.post('/feedback/quality', data);
    return response.data;
  },

  getStatistics: async (): Promise<any> => {
    const response = await axiosInstance.get('/feedback/statistics');
    return response.data;
  }
};

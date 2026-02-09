import axios from 'axios';
import type { PreprocessRequest, PreprocessResponse } from '../types/preprocessing';

const API_BASE = '/api/v1';

export const preprocessQuestion = async (req: PreprocessRequest): Promise<PreprocessResponse> => {
  const response = await axios.post<PreprocessResponse>(`${API_BASE}/intelligent/preprocess`, req);
  return response.data;
};

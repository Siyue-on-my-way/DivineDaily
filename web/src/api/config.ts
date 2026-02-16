import axiosInstance from '../lib/axios';
import type {
  LLMConfig,
  LLMConfigCreateRequest,
  LLMConfigUpdateRequest,
  PromptConfig,
  PromptConfigCreateRequest,
  PromptConfigUpdateRequest,
  PromptRenderRequest,
  PromptRenderResponse,
  ApiResponse,
} from '../types/config';

const api = axiosInstance;

// LLM配置API
export const llmConfigApi = {
  // 获取所有LLM配置
  list: async (): Promise<LLMConfig[]> => {
    const response = await api.get<ApiResponse<LLMConfig[]>>('/configs/llm');
    return response.data.data;
  },

  // 获取单个LLM配置
  get: async (id: number): Promise<LLMConfig> => {
    const response = await api.get<ApiResponse<LLMConfig>>(`/configs/llm/${id}`);
    return response.data.data;
  },

  // 创建LLM配置
  create: async (data: LLMConfigCreateRequest): Promise<LLMConfig> => {
    const response = await api.post<ApiResponse<LLMConfig>>('/configs/llm', data);
    return response.data.data;
  },

  // 更新LLM配置
  update: async (id: number, data: LLMConfigUpdateRequest): Promise<LLMConfig> => {
    const response = await api.put<ApiResponse<LLMConfig>>(`/configs/llm/${id}`, data);
    return response.data.data;
  },

  // 删除LLM配置
  delete: async (id: number): Promise<void> => {
    await api.delete(`/configs/llm/${id}`);
  },

  // 设置默认LLM配置
  setDefault: async (id: number): Promise<void> => {
    await api.post(`/configs/llm/${id}/set-default`);
  },

  // 测试LLM配置
  test: async (id: number, mode: 'block' | 'stream' = 'block'): Promise<any> => {
    const response = await api.post<ApiResponse<any>>(`/configs/llm/${id}/test`, { mode });
    return response.data.data;
  },
};

// Prompt配置API
export const promptConfigApi = {
  // 获取所有Prompt配置
  list: async (): Promise<PromptConfig[]> => {
    const response = await api.get<ApiResponse<PromptConfig[]>>('/configs/prompt');
    return response.data.data;
  },

  // 获取单个Prompt配置
  get: async (id: number): Promise<PromptConfig> => {
    const response = await api.get<ApiResponse<PromptConfig>>(`/configs/prompt/${id}`);
    return response.data.data;
  },

  // 创建Prompt配置
  create: async (data: PromptConfigCreateRequest): Promise<PromptConfig> => {
    const response = await api.post<ApiResponse<PromptConfig>>('/configs/prompt', data);
    return response.data.data;
  },

  // 更新Prompt配置
  update: async (id: number, data: PromptConfigUpdateRequest): Promise<PromptConfig> => {
    const response = await api.put<ApiResponse<PromptConfig>>(`/configs/prompt/${id}`, data);
    return response.data.data;
  },

  // 删除Prompt配置
  delete: async (id: number): Promise<void> => {
    await api.delete(`/configs/prompt/${id}`);
  },

  // 设置默认Prompt配置
  setDefault: async (id: number): Promise<void> => {
    await api.post(`/configs/prompt/${id}/set-default`);
  },

  // 预览Prompt渲染结果
  render: async (data: PromptRenderRequest): Promise<string> => {
    const response = await api.post<ApiResponse<PromptRenderResponse>>('/configs/prompt/render', data);
    return response.data.data.rendered;
  },
};

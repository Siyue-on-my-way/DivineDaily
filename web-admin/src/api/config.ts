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
  test: async (id: number, message?: string): Promise<any> => {
    const response = await api.post<any>(`/configs/llm/${id}/test`, { 
      message: message || "你好，请介绍一下你自己",
      mode: "block" 
    });
    return response.data;
  },
};

// Assistant配置API（原Prompt配置）
export const assistantConfigApi = {
  // 获取所有Assistant配置
  list: async (): Promise<PromptConfig[]> => {
    const response = await api.get<ApiResponse<PromptConfig[]>>('/configs/assistant');
    return response.data.data;
  },

  // 获取单个Assistant配置
  get: async (id: number): Promise<PromptConfig> => {
    const response = await api.get<ApiResponse<PromptConfig>>(`/configs/assistant/${id}`);
    return response.data.data;
  },

  // 创建Assistant配置
  create: async (data: PromptConfigCreateRequest): Promise<PromptConfig> => {
    const response = await api.post<ApiResponse<PromptConfig>>('/configs/assistant', data);
    return response.data.data;
  },

  // 更新Assistant配置
  update: async (id: number, data: PromptConfigUpdateRequest): Promise<PromptConfig> => {
    const response = await api.put<ApiResponse<PromptConfig>>(`/configs/assistant/${id}`, data);
    return response.data.data;
  },

  // 删除Assistant配置
  delete: async (id: number): Promise<void> => {
    await api.delete(`/configs/assistant/${id}`);
  },

  // 设置默认Assistant配置
  setDefault: async (id: number): Promise<void> => {
    await api.post(`/configs/assistant/${id}/set-default`);
  },

  // 预览Prompt渲染结果
  render: async (data: PromptRenderRequest): Promise<string> => {
    const response = await api.post<ApiResponse<PromptRenderResponse>>('/configs/assistant/render', data);
    return response.data.data.rendered;
  },

  // 获取测试用例
  getTestCases: async (): Promise<any> => {
    const response = await api.get<ApiResponse<any>>('/configs/assistant/test-cases');
    return response.data.data;
  },

  // 测试Assistant配置
  test: async (id: number): Promise<any> => {
    const response = await api.post<any>(`/configs/assistant/${id}/test`);
    return response.data;
  },
};

// 向后兼容：保留旧的 promptConfigApi 别名
export const promptConfigApi = assistantConfigApi;

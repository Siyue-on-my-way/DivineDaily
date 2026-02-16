// LLM 配置类型（与后端返回字段一致）
export interface LLMConfig {
  id: number;
  name: string;
  provider: string;
  url_type: string;
  model: string;  // 后端返回的是 model
  model_name: string;  // 兼容字段
  api_key: string | null;
  api_key_masked?: string;  // 前端显示用
  endpoint: string;
  is_default: boolean;
  is_enabled: boolean;
  description: string | null;
  temperature: number | null;
  max_tokens: number | null;
  timeout: number | null;
  created_at: string;
  updated_at: string;
}

// 创建/更新 LLM 配置请求（与后端 API 一致）
export interface LLMConfigCreateRequest {
  name: string;
  provider: string;
  url_type?: string;
  api_key?: string;
  endpoint?: string;
  model_name: string;  // 后端接收的是 model_name
  is_default?: boolean;
  is_enabled?: boolean;
  description?: string;
  temperature?: number | null;
  max_tokens?: number | null;
  timeout?: number | null;  // 后端接收的是 timeout，不是 timeout_seconds
}

// 更新 LLM 配置请求（与创建请求相同）
export interface LLMConfigUpdateRequest extends LLMConfigCreateRequest {}

// Prompt 变量类型
export interface PromptVariable {
  name: string;
  type: string;
  required: boolean;
  description?: string;
}

// Prompt 配置类型（Assistant 配置，与后端返回字段完全一致）
export interface PromptConfig {
  id: number;
  name: string;
  scene: string;                      // divination/tarot/daily_fortune
  llm_config_id: number;
  llm_config_name?: string;           // 关联的 LLM 配置名称
  temperature: number;
  max_tokens: number;
  timeout_seconds: number;
  prompt_type: string;                // answer/detail/recommendation
  question_type: string;              // decision/relationship/career
  template: string;
  variables: PromptVariable[] | null;
  is_default: boolean;
  is_enabled: boolean;
  description: string;
  created_at: string;
  updated_at: string;
}

// 创建 Prompt 配置请求
export interface PromptConfigCreateRequest {
  name: string;
  scene: string;
  prompt_type: string;
  question_type: string;
  template: string;
  llm_config_id: number;
  variables?: PromptVariable[];
  temperature?: number;
  max_tokens?: number;
  timeout_seconds?: number;
  is_enabled?: boolean;
  description?: string;
}

// 更新 Prompt 配置请求
export interface PromptConfigUpdateRequest extends PromptConfigCreateRequest {}

// Prompt 渲染请求
export interface PromptRenderRequest {
  template: string;
  variables: Record<string, any>;
}

// Prompt 渲染响应
export interface PromptRenderResponse {
  rendered: string;
}

// API 响应包装
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

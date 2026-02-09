// 配置管理相关类型定义

export interface LLMConfig {
  id: number;
  name: string;
  provider: string; // openai/anthropic/local
  url_type?: string; // openai_compatible/custom
  api_key?: string; // 真实API Key
  api_key_masked?: string; // 脱敏后的API Key
  endpoint?: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
  timeout_seconds: number;
  is_default: boolean;
  is_enabled: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface LLMConfigCreateRequest {
  name: string;
  provider: string;
  url_type?: string;
  api_key?: string;
  endpoint?: string;
  model_name: string;
  temperature?: number;
  max_tokens?: number;
  timeout_seconds?: number;
  is_enabled?: boolean;
  description?: string;
}

export interface LLMConfigUpdateRequest {
  name?: string;
  provider?: string;
  url_type?: string;
  api_key?: string;
  endpoint?: string;
  model_name?: string;
  temperature?: number;
  max_tokens?: number;
  timeout_seconds?: number;
  is_enabled?: boolean;
  description?: string;
}

export interface PromptVariable {
  name: string;
  type: string; // string/int/float/bool
  description: string;
  required: boolean;
}

export interface PromptConfig {
  id: number;
  name: string;
  prompt_type: string; // answer/detail/recommendation
  question_type: string; // decision/recommendation
  template: string;
  variables?: PromptVariable[];
  is_default: boolean;
  is_enabled: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface PromptConfigCreateRequest {
  name: string;
  prompt_type: string;
  question_type: string;
  template: string;
  variables?: PromptVariable[];
  is_enabled?: boolean;
  description?: string;
}

export interface PromptConfigUpdateRequest {
  name?: string;
  prompt_type?: string;
  question_type?: string;
  template?: string;
  variables?: PromptVariable[];
  is_enabled?: boolean;
  description?: string;
}

export interface PromptRenderRequest {
  template: string;
  variables: Record<string, any>;
}

export interface PromptRenderResponse {
  rendered: string;
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  detail?: string;
}


// 环境变量验证和类型定义
interface ImportMetaEnv {
  readonly VITE_API_PROXY_TARGET?: string;
  readonly VITE_APP_BASE_URL?: string;
  readonly VITE_DEBUG?: string;
  readonly VITE_SENTRY_DSN?: string;
  readonly VITE_ANALYTICS_ID?: string;
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly MODE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// 环境变量配置
export const env = {
  // API 配置
  apiProxyTarget: import.meta.env.VITE_API_PROXY_TARGET || 'http://localhost:8080',
  appBaseUrl: import.meta.env.VITE_APP_BASE_URL || '',
  
  // 调试配置
  debug: import.meta.env.VITE_DEBUG === 'true',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  mode: import.meta.env.MODE,
  
  // 第三方服务
  sentryDsn: import.meta.env.VITE_SENTRY_DSN || '',
  analyticsId: import.meta.env.VITE_ANALYTICS_ID || '',
};

// 验证必需的环境变量
export const validateEnv = () => {
  const requiredEnvVars: (keyof typeof env)[] = [];
  
  const missing = requiredEnvVars.filter(key => !env[key]);
  
  if (missing.length > 0) {
    console.warn('Missing required environment variables:', missing);
  }
};

// 在开发环境打印配置
if (env.isDevelopment && env.debug) {
  console.log('Environment configuration:', env);
}

export default env;

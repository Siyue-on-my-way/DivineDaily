import { useState, useEffect } from 'react';
import { llmConfigApi } from '../../api/config';
import type { LLMConfig } from '../../types/config';
import LLMConfigList from '../../components/config/LLMConfigList';
import './LLMConfigPage.css';

export default function LLMConfigPage() {
  const [configs, setConfigs] = useState<LLMConfig[]>([]);
  const [loading, setLoading] = useState(false);

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const data = await llmConfigApi.list();
      setConfigs(data);
    } catch (error) {
      console.error('加载LLM配置失败:', error);
      alert('加载LLM配置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfigs();
  }, []);

  return (
    <div className="llm-config-page">
      <div className="page-header">
        <h1>LLM 配置管理</h1>
        <p>管理 LLM 模型配置，包括 API 密钥、端点等</p>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <LLMConfigList configs={configs} onRefresh={loadConfigs} />
      )}
    </div>
  );
}

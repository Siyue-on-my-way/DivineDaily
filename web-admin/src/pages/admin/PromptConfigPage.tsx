import { useState, useEffect } from 'react';
import { promptConfigApi } from '../../api/config';
import type { PromptConfig } from '../../types/config';
import PromptConfigList from '../../components/config/PromptConfigList';
import './PromptConfigPage.css';

export default function PromptConfigPage() {
  const [configs, setConfigs] = useState<PromptConfig[]>([]);
  const [loading, setLoading] = useState(false);

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const data = await promptConfigApi.list();
      setConfigs(data);
    } catch (error) {
      console.error('加载 Assistant 配置失败:', error);
      alert('加载 Assistant 配置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfigs();
  }, []);

  return (
    <div className="prompt-config-page">
      <div className="page-header">
        <h1>Assistant 配置管理</h1>
        <p>管理 AI Assistant 配置，包括 Prompt 模板、LLM 模型选择等</p>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <PromptConfigList configs={configs} onRefresh={loadConfigs} />
      )}
    </div>
  );
}

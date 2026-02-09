import { useState, useEffect } from 'react';
import { llmConfigApi, promptConfigApi } from '../api/config';
import type { LLMConfig, PromptConfig } from '../types/config';
import LLMConfigList from '../components/config/LLMConfigList';
import PromptConfigList from '../components/config/PromptConfigList';
import { MobilePage } from '../components/mobile';
import './ConfigManagement.css';

type TabType = 'llm' | 'prompt';

export default function ConfigManagement() {
  const [activeTab, setActiveTab] = useState<TabType>('llm');
  const [llmConfigs, setLlmConfigs] = useState<LLMConfig[]>([]);
  const [promptConfigs, setPromptConfigs] = useState<PromptConfig[]>([]);
  const [loading, setLoading] = useState(false);

  // 加载LLM配置
  const loadLLMConfigs = async () => {
    setLoading(true);
    try {
      const configs = await llmConfigApi.list();
      setLlmConfigs(configs);
    } catch (error) {
      console.error('加载LLM配置失败:', error);
      alert('加载LLM配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载Prompt配置
  const loadPromptConfigs = async () => {
    setLoading(true);
    try {
      const configs = await promptConfigApi.list();
      setPromptConfigs(configs);
    } catch (error) {
      console.error('加载Prompt配置失败:', error);
      alert('加载Prompt配置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'llm') {
      loadLLMConfigs();
    } else {
      loadPromptConfigs();
    }
  }, [activeTab]);

  return (
    <MobilePage title="配置管理">
      <div className="config-header">
        <div className="config-tabs">
          <button
            className={`tab ${activeTab === 'llm' ? 'active' : ''}`}
            onClick={() => setActiveTab('llm')}
          >
            LLM配置
          </button>
          <button
            className={`tab ${activeTab === 'prompt' ? 'active' : ''}`}
            onClick={() => setActiveTab('prompt')}
          >
            Prompt配置
          </button>
        </div>
      </div>

      <div className="config-content">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : activeTab === 'llm' ? (
          <LLMConfigList
            configs={llmConfigs}
            onRefresh={loadLLMConfigs}
          />
        ) : (
          <PromptConfigList
            configs={promptConfigs}
            onRefresh={loadPromptConfigs}
          />
        )}
      </div>
    </MobilePage>
  );
}


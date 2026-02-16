import { useState, useEffect } from 'react';
import type { LLMConfig, LLMConfigCreateRequest } from '../../types/config';
import './ConfigForm.css';

interface Props {
  config?: LLMConfig | null;
  onSubmit: (data: LLMConfigCreateRequest) => void;
  onCancel: () => void;
}

export default function LLMConfigForm({ config, onSubmit, onCancel }: Props) {
  const [formData, setFormData] = useState<LLMConfigCreateRequest>({
    name: '',
    provider: 'local',
    url_type: 'openai_compatible',
    api_key: '',
    endpoint: '',
    model_name: '',
    temperature: 0.7,
    max_tokens: 1000,
    timeout: 30,
    is_enabled: true,
    description: '',
  });

  useEffect(() => {
    if (config) {
      setFormData({
        name: config.name,
        provider: config.provider,
        url_type: config.url_type || 'openai_compatible',
        api_key: config.api_key || '',
        endpoint: config.endpoint || '',
        model_name: config.model_name || config.model,
        temperature: config.temperature,
        max_tokens: config.max_tokens,
        timeout: config.timeout,
        is_enabled: config.is_enabled,
        description: config.description || '',
      });
    }
  }, [config]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="config-form-overlay">
      <div className="config-form">
        <div className="config-form-header">
          <h3>{config ? '编辑LLM配置' : '新建LLM配置'}</h3>
          <button className="btn-close" onClick={onCancel}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>配置名称 *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>服务商 *</label>
            <select
              value={formData.provider}
              onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
              required
            >
              <option value="local">本地模型</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </div>

          <div className="form-group">
            <label>URL处理方式</label>
            <div className="radio-group" style={{ display: 'flex', gap: '20px', marginTop: '5px' }}>
              <label style={{ display: 'flex', alignItems: 'center', fontWeight: 'normal' }}>
                <input
                  type="radio"
                  name="url_type"
                  value="openai_compatible"
                  checked={formData.url_type === 'openai_compatible' || !formData.url_type}
                  onChange={(e) => setFormData({ ...formData, url_type: e.target.value })}
                  style={{ marginRight: '5px' }}
                />
                OpenAI兼容 (自动补全 /chat/completions)
              </label>
              <label style={{ display: 'flex', alignItems: 'center', fontWeight: 'normal' }}>
                <input
                  type="radio"
                  name="url_type"
                  value="custom"
                  checked={formData.url_type === 'custom'}
                  onChange={(e) => setFormData({ ...formData, url_type: e.target.value })}
                  style={{ marginRight: '5px' }}
                />
                自定义 (使用完整URL)
              </label>
            </div>
            <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
              {formData.url_type === 'custom' 
                ? '请填写完整的 API URL，例如：http://host:port/v1/chat/completions' 
                : '系统不会自动追加 /chat/completions，需输入完整 URL，例如：https://once.novai.su/v1/chat/completions'}
            </small>
          </div>

          <div className="form-group">
            <label>API Key {config && '(留空则不更新)'}</label>
            <input
              type="password"
              value={formData.api_key}
              onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
              placeholder={config ? '留空则不更新API Key' : '请输入API Key'}
            />
          </div>

          <div className="form-group">
            <label>Endpoint</label>
            <input
              type="text"
              value={formData.endpoint}
              onChange={(e) => setFormData({ ...formData, endpoint: e.target.value })}
              placeholder="本地模型需要填写Endpoint"
            />
          </div>

          <div className="form-group">
            <label>模型名称 *</label>
            <input
              type="text"
              value={formData.model_name}
              onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>温度</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="2"
                value={formData.temperature ?? ''}
                onChange={(e) => setFormData({ ...formData, temperature: e.target.value ? parseFloat(e.target.value) : null })}
              />
            </div>

            <div className="form-group">
              <label>最大Token</label>
              <input
                type="number"
                min="1"
                value={formData.max_tokens ?? ''}
                onChange={(e) => setFormData({ ...formData, max_tokens: e.target.value ? parseInt(e.target.value) : null })}
              />
            </div>

            <div className="form-group">
              <label>超时时间(秒)</label>
              <input
                type="number"
                min="1"
                value={formData.timeout ?? ''}
                onChange={(e) => setFormData({ ...formData, timeout: e.target.value ? parseInt(e.target.value) : null })}
              />
            </div>
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={formData.is_enabled}
                onChange={(e) => setFormData({ ...formData, is_enabled: e.target.checked })}
              />
              启用
            </label>
          </div>

          <div className="form-group">
            <label>描述</label>
            <textarea
              value={formData.description ?? ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onCancel}>
              取消
            </button>
            <button type="submit" className="btn-primary">
              {config ? '更新' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

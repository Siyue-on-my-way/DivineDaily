import { useState, useEffect } from 'react';
import { llmConfigApi } from '../../api/config';
import type { LLMConfig, LLMConfigCreateRequest } from '../../types/config';
import { toast } from '../../hooks/useToast';
import './LLMConfigModal.css';

interface Props {
  config: LLMConfig | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function LLMConfigModal({ config, onClose, onSuccess }: Props) {
  const [formData, setFormData] = useState<LLMConfigCreateRequest>({
    name: '',
    provider: 'openai',
    url_type: 'openai_compatible',
    api_key: '',
    endpoint: '',
    model_name: '',
    is_enabled: true,
    description: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (config) {
      setFormData({
        name: config.name,
        provider: config.provider,
        url_type: config.url_type || 'openai_compatible',
        api_key: config.api_key || '',
        endpoint: config.endpoint || '',
        model_name: config.model_name,
        is_enabled: config.is_enabled,
        description: config.description || '',
      });
    }
  }, [config]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      if (config) {
        await llmConfigApi.update(config.id, formData);
        toast.success('更新成功');
      } else {
        await llmConfigApi.create(formData);
        toast.success('创建成功');
      }
      onSuccess();
    } catch (error: any) {
      console.error('操作失败:', error);
      toast.error(error.response?.data?.detail || '操作失败');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{config ? '编辑配置' : '新建配置'}</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>配置名称 *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：GPT-4"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>服务商 *</label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  required
                >
                  <option value="openai">OpenAI</option>
                  <option value="local">本地模型</option>
                  <option value="custom">自定义</option>
                </select>
              </div>

              <div className="form-group">
                <label>URL类型</label>
                <select
                  value={formData.url_type}
                  onChange={(e) => setFormData({ ...formData, url_type: e.target.value })}
                >
                  <option value="openai_compatible">OpenAI兼容</option>
                  <option value="custom">自定义</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>模型名称 *</label>
              <input
                type="text"
                value={formData.model_name}
                onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                placeholder="例如：gpt-4, deepseek-chat"
                required
              />
            </div>

            <div className="form-group">
              <label>API 端点</label>
              <input
                type="text"
                value={formData.endpoint}
                onChange={(e) => setFormData({ ...formData, endpoint: e.target.value })}
                placeholder="例如：https://api.openai.com/v1"
              />
              <small className="form-hint">留空则使用默认端点</small>
            </div>

            <div className="form-group">
              <label>API Key</label>
              <input
                type="password"
                value={formData.api_key}
                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                placeholder="sk-..."
              />
              {config && (
                <small className="form-hint">留空则保持原有密钥不变</small>
              )}
            </div>

            <div className="form-group">
              <label>描述</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="配置说明（可选）"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.is_enabled}
                  onChange={(e) => setFormData({ ...formData, is_enabled: e.target.checked })}
                />
                <span>启用此配置</span>
              </label>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              取消
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? '提交中...' : config ? '更新' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { llmConfigApi } from '../../api/config';
import type { PromptConfig, PromptConfigCreateRequest, PromptVariable, LLMConfig } from '../../types/config';
import './ConfigForm.css';

interface Props {
  config?: PromptConfig | null;
  onSubmit: (data: PromptConfigCreateRequest) => void;
  onCancel: () => void;
}

export default function PromptConfigForm({ config, onSubmit, onCancel }: Props) {
  const [formData, setFormData] = useState<PromptConfigCreateRequest>({
    name: '',
    prompt_type: 'answer',
    question_type: 'decision',
    template: '',
    variables: [],
    llm_config_id: undefined,
    temperature: 0.7,
    max_tokens: 2000,
    timeout_seconds: 30,
    scene: 'divination',
    is_enabled: true,
    description: '',
  });

  const [llmConfigs, setLlmConfigs] = useState<LLMConfig[]>([]);
  const [loadingLLMs, setLoadingLLMs] = useState(false);

  // 加载 LLM 配置列表
  useEffect(() => {
    const loadLLMConfigs = async () => {
      setLoadingLLMs(true);
      try {
        const configs = await llmConfigApi.list();
        setLlmConfigs(configs.filter(c => c.is_enabled));
      } catch (error) {
        console.error('加载 LLM 配置失败:', error);
      } finally {
        setLoadingLLMs(false);
      }
    };
    loadLLMConfigs();
  }, []);

  useEffect(() => {
    if (config) {
      setFormData({
        name: config.name,
        prompt_type: config.prompt_type,
        question_type: config.question_type,
        template: config.template,
        variables: config.variables || [],
        llm_config_id: config.llm_config_id || undefined,
        temperature: config.temperature || 0.7,
        max_tokens: config.max_tokens || 2000,
        timeout_seconds: config.timeout_seconds || 30,
        scene: config.scene || 'divination',
        is_enabled: config.is_enabled,
        description: config.description || '',
      });
    }
  }, [config]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const addVariable = () => {
    setFormData({
      ...formData,
      variables: [
        ...(formData.variables || []),
        { name: '', type: 'string', description: '', required: false },
      ],
    });
  };

  const removeVariable = (index: number) => {
    const newVariables = [...(formData.variables || [])];
    newVariables.splice(index, 1);
    setFormData({ ...formData, variables: newVariables });
  };

  const updateVariable = (index: number, field: keyof PromptVariable, value: string | boolean) => {
    const newVariables = [...(formData.variables || [])];
    newVariables[index] = { ...newVariables[index], [field]: value };
    setFormData({ ...formData, variables: newVariables });
  };

  return (
    <div className="config-form-overlay">
      <div className="config-form config-form-large">
        <div className="config-form-header">
          <h3>{config ? '编辑 Assistant 配置' : '新建 Assistant 配置'}</h3>
          <button className="btn-close" onClick={onCancel}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>配置名称 *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="例如：塔罗牌-结果卡"
              />
            </div>

            <div className="form-group">
              <label>场景 *</label>
              <select
                value={formData.scene}
                onChange={(e) => setFormData({ ...formData, scene: e.target.value })}
                required
              >
                <option value="divination">占卜 (divination)</option>
                <option value="tarot">塔罗牌 (tarot)</option>
                <option value="daily_fortune">每日运势 (daily_fortune)</option>
                <option value="preprocessing">预处理 (preprocessing)</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Prompt类型 *</label>
              <select
                value={formData.prompt_type}
                onChange={(e) => setFormData({ ...formData, prompt_type: e.target.value })}
                required
              >
                <option value="answer">结果卡 (answer)</option>
                <option value="detail">详情 (detail)</option>
                <option value="recommendation">推荐 (recommendation)</option>
              </select>
            </div>

            <div className="form-group">
              <label>问题类型 *</label>
              <select
                value={formData.question_type}
                onChange={(e) => setFormData({ ...formData, question_type: e.target.value })}
                required
              >
                <option value="decision">决策类</option>
                <option value="recommendation">推荐类</option>
                <option value="fortune">运势类</option>
                <option value="knowledge">知识类</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>关联 LLM 模型</label>
            <select
              value={formData.llm_config_id || ''}
              onChange={(e) => setFormData({ 
                ...formData, 
                llm_config_id: e.target.value ? parseInt(e.target.value) : undefined 
              })}
              disabled={loadingLLMs}
            >
              <option value="">使用默认模型</option>
              {llmConfigs.map((llm) => (
                <option key={llm.id} value={llm.id}>
                  {llm.name} ({llm.model_name})
                </option>
              ))}
            </select>
            <small className="form-hint">
              留空则使用系统默认 LLM 模型，或选择特定模型
            </small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Temperature</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="2"
                value={formData.temperature}
                onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
              />
              <small className="form-hint">0-2，越高越随机</small>
            </div>

            <div className="form-group">
              <label>Max Tokens</label>
              <input
                type="number"
                min="1"
                max="10000"
                value={formData.max_tokens}
                onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
              />
            </div>

            <div className="form-group">
              <label>超时时间（秒）</label>
              <input
                type="number"
                min="5"
                max="300"
                value={formData.timeout_seconds}
                onChange={(e) => setFormData({ ...formData, timeout_seconds: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Prompt 模板 *</label>
            <textarea
              value={formData.template}
              onChange={(e) => setFormData({ ...formData, template: e.target.value })}
              rows={15}
              required
              placeholder={`使用 {{.variable_name}} 作为变量占位符，例如：{{.Question}}`}
              className="template-editor"
            />
            <small className="form-hint">
              使用 Go template 语法，变量格式：{`{{.VariableName}}`}
            </small>
          </div>

          <div className="form-group">
            <div className="form-group-header">
              <label>变量说明（可选）</label>
              <button type="button" className="btn-link" onClick={addVariable}>
                + 添加变量
              </button>
            </div>
            {formData.variables && formData.variables.length > 0 && (
              <div className="variables-list">
                {formData.variables.map((variable, index) => (
                  <div key={index} className="variable-item">
                    <input
                      type="text"
                      placeholder="变量名"
                      value={variable.name}
                      onChange={(e) => updateVariable(index, 'name', e.target.value)}
                      className="variable-name"
                    />
                    <select
                      value={variable.type}
                      onChange={(e) => updateVariable(index, 'type', e.target.value)}
                      className="variable-type"
                    >
                      <option value="string">string</option>
                      <option value="int">int</option>
                      <option value="float">float</option>
                      <option value="bool">bool</option>
                    </select>
                    <input
                      type="text"
                      placeholder="描述"
                      value={variable.description}
                      onChange={(e) => updateVariable(index, 'description', e.target.value)}
                      className="variable-desc"
                    />
                    <label className="variable-required">
                      <input
                        type="checkbox"
                        checked={variable.required}
                        onChange={(e) => updateVariable(index, 'required', e.target.checked)}
                      />
                      必填
                    </label>
                    <button
                      type="button"
                      className="btn-link btn-danger"
                      onClick={() => removeVariable(index)}
                    >
                      删除
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="form-group">
            <label>描述</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={2}
              placeholder="配置说明（可选）"
            />
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.is_enabled}
                onChange={(e) => setFormData({ ...formData, is_enabled: e.target.checked })}
              />
              启用此配置
            </label>
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

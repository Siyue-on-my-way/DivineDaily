import { useState, useEffect } from 'react';
import type { PromptConfig, PromptConfigCreateRequest, PromptVariable } from '../../types/config';
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
    is_enabled: true,
    description: '',
  });

  useEffect(() => {
    if (config) {
      setFormData({
        name: config.name,
        prompt_type: config.prompt_type,
        question_type: config.question_type,
        template: config.template,
        variables: config.variables || [],
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
          <h3>{config ? '编辑Prompt配置' : '新建Prompt配置'}</h3>
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
              />
            </div>

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
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Prompt模板 *</label>
            <textarea
              value={formData.template}
              onChange={(e) => setFormData({ ...formData, template: e.target.value })}
              rows={15}
              required
              placeholder={`使用 {{.variable_name}} 作为变量占位符，例如：{{.question}}`}
              className="template-editor"
            />
            <small className="form-hint">
              使用 Go template 语法，变量格式：{`{{.variable_name}}`}
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
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={2}
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


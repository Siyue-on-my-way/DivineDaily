import { useState } from 'react';
import { promptConfigApi } from '../../api/config';
import type { PromptConfig } from '../../types/config';
import './ConfigForm.css';

interface Props {
  config: PromptConfig;
  onClose: () => void;
}

export default function PromptPreview({ config, onClose }: Props) {
  const [variables, setVariables] = useState<Record<string, any>>({});
  const [rendered, setRendered] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleRender = async () => {
    setLoading(true);
    try {
      const result = await promptConfigApi.render({
        template: config.template,
        variables,
      });
      setRendered(result);
    } catch (error: any) {
      console.error('渲染失败:', error);
      alert(error.response?.data?.detail || '渲染失败');
    } finally {
      setLoading(false);
    }
  };

  const updateVariable = (name: string, value: any) => {
    setVariables({ ...variables, [name]: value });
  };

  return (
    <div className="config-form-overlay">
      <div className="config-form config-form-large">
        <div className="config-form-header">
          <h3>Prompt预览 - {config.name}</h3>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>

        <div className="preview-content">
          <div className="preview-section">
            <h4>变量输入</h4>
            <div className="variables-input">
              {config.variables && config.variables.length > 0 ? (
                config.variables.map((variable) => (
                  <div key={variable.name} className="form-group">
                    <label>
                      {variable.name} ({variable.type})
                      {variable.required && <span className="required">*</span>}
                    </label>
                    <input
                      type="text"
                      value={variables[variable.name] || ''}
                      onChange={(e) => updateVariable(variable.name, e.target.value)}
                      placeholder={variable.description}
                    />
                  </div>
                ))
              ) : (
                <p className="text-muted">此Prompt没有定义变量</p>
              )}
            </div>
            <button
              className="btn-primary"
              onClick={handleRender}
              disabled={loading}
            >
              {loading ? '渲染中...' : '渲染预览'}
            </button>
          </div>

          {rendered && (
            <div className="preview-section">
              <h4>渲染结果</h4>
              <div className="rendered-output">
                <pre>{rendered}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="form-actions">
          <button className="btn-secondary" onClick={onClose}>
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}


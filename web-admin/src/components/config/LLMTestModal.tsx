import { useState } from 'react';
import { llmConfigApi } from '../../api/config';
import './LLMTestModal.css';

interface Props {
  configId: number;
  configName: string;
  onClose: () => void;
}

export default function LLMTestModal({ configId, configName, onClose }: Props) {
  const [message, setMessage] = useState('你好，请介绍一下你自己');
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleTest = async () => {
    if (!message.trim()) {
      alert('请输入测试消息');
      return;
    }

    setTesting(true);
    setResult(null);

    try {
      const response = await llmConfigApi.test(configId, message);
      setResult(response);
    } catch (error: any) {
      setResult({
        success: false,
        error: error.response?.data?.detail || error.message || '测试失败'
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content llm-test-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>测试 LLM 配置</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="config-info">
            <span className="label">配置名称：</span>
            <span className="value">{configName}</span>
          </div>

          <div className="test-input-section">
            <label>测试消息：</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="输入一句话测试 LLM..."
              rows={4}
              disabled={testing}
            />
          </div>

          <button 
            className="btn-primary test-btn" 
            onClick={handleTest}
            disabled={testing}
          >
            {testing ? '测试中...' : '开始测试'}
          </button>

          {result && (
            <div className={`test-result ${result.success ? 'success' : 'error'}`}>
              <div className="result-header">
                {result.success ? '✅ 测试成功' : '❌ 测试失败'}
              </div>

              {result.success ? (
                <div className="result-content">
                  <div className="result-section">
                    <div className="section-title">📤 发送消息：</div>
                    <div className="message-box user-message">
                      {result.request?.user_message}
                    </div>
                  </div>

                  <div className="result-section">
                    <div className="section-title">📥 LLM 回复：</div>
                    <div className="message-box llm-response">
                      {result.response}
                    </div>
                  </div>

                  <div className="result-meta">
                    <span>模型: {result.request?.model}</span>
                    <span>Endpoint: {result.request?.endpoint}</span>
                  </div>
                </div>
              ) : (
                <div className="error-content">
                  <div className="error-message">{result.error || result.message}</div>
                  {result.request && (
                    <div className="error-details">
                      <div>模型: {result.request.model}</div>
                      <div>Endpoint: {result.request.endpoint}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
}


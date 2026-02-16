import { useState } from 'react';
import { llmConfigApi } from '../../api/config';
import type { LLMConfig } from '../../types/config';
import { toast } from '../../hooks/useToast';
import './LLMConfigCard.css';

interface Props {
  config: LLMConfig;
  onEdit: (config: LLMConfig) => void;
  onDelete: (id: number) => void;
  onSetDefault: (id: number) => void;
  onRefresh: () => void;
}

type TestMode = 'block' | 'stream';

export default function LLMConfigCard({ config, onEdit, onDelete, onSetDefault, onRefresh }: Props) {
  const [testing, setTesting] = useState(false);
  const [testMode, setTestMode] = useState<TestMode>('block');
  const [testResult, setTestResult] = useState<string>('');
  const [showTestResult, setShowTestResult] = useState(false);

  // 阻塞式测试
  const handleTestBlock = async () => {
    setTesting(true);
    setTestMode('block');
    setTestResult('');
    setShowTestResult(true);

    try {
      const response = await llmConfigApi.test(config.id, 'block');
      setTestResult(`✅ 测试成功\n\n响应: ${response.response}\n\nToken数: ${response.token_count}\n耗时: ${response.duration_ms}ms`);
      toast.success('阻塞式测试成功');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || '测试失败';
      setTestResult(`❌ 测试失败\n\n${errorMsg}`);
      toast.error('阻塞式测试失败');
    } finally {
      setTesting(false);
    }
  };

  // 流式测试
  const handleTestStream = async () => {
    setTesting(true);
    setTestMode('stream');
    setTestResult('');
    setShowTestResult(true);

    try {
      const eventSource = new EventSource(
        `/api/v1/configs/llm/${config.id}/test?mode=stream`,
        { withCredentials: true }
      );

      let fullText = '';
      let tokenCount = 0;

      eventSource.addEventListener('message', (e) => {
        const chunk = e.data;
        fullText += chunk;
        setTestResult(`🔄 流式接收中...\n\n${fullText}`);
      });

      eventSource.addEventListener('done', (e) => {
        const data = JSON.parse(e.data);
        tokenCount = data.token_count;
        setTestResult(`✅ 流式测试成功\n\n响应: ${fullText}\n\nToken数: ${tokenCount}`);
        toast.success('流式测试成功');
        eventSource.close();
        setTesting(false);
      });

      eventSource.addEventListener('error', (e: any) => {
        const errorData = e.data ? JSON.parse(e.data) : {};
        const errorMsg = errorData.error || '流式连接失败';
        setTestResult(`❌ 测试失败\n\n${errorMsg}`);
        toast.error('流式测试失败');
        eventSource.close();
        setTesting(false);
      });

      eventSource.onerror = () => {
        if (!testResult.includes('✅')) {
          setTestResult(`❌ 测试失败\n\n流式连接中断`);
          toast.error('流式连接中断');
        }
        eventSource.close();
        setTesting(false);
      };
    } catch (error: any) {
      const errorMsg = error.message || '测试失败';
      setTestResult(`❌ 测试失败\n\n${errorMsg}`);
      toast.error('流式测试失败');
      setTesting(false);
    }
  };

  return (
    <div className={`llm-config-card ${config.is_default ? 'default' : ''}`}>
      <div className="card-header">
        <div className="card-title-row">
          <h3 className="card-title">{config.name}</h3>
          <div className="card-badges">
            {config.is_default && <span className="badge badge-primary">默认</span>}
            {config.is_enabled ? (
              <span className="badge badge-success">启用</span>
            ) : (
              <span className="badge badge-disabled">禁用</span>
            )}
          </div>
        </div>
        {config.description && <p className="card-description">{config.description}</p>}
      </div>

      <div className="card-body">
        <div className="config-info">
          <div className="info-row">
            <span className="info-label">服务商</span>
            <span className="info-value">{config.provider}</span>
          </div>
          <div className="info-row">
            <span className="info-label">模型</span>
            <span className="info-value">{config.model_name}</span>
          </div>
          {config.endpoint && (
            <div className="info-row">
              <span className="info-label">端点</span>
              <span className="info-value info-url">{config.endpoint}</span>
            </div>
          )}
          {config.api_key_masked && (
            <div className="info-row">
              <span className="info-label">API Key</span>
              <span className="info-value info-key">{config.api_key_masked}</span>
            </div>
          )}
        </div>

        <div className="test-section">
          <div className="test-buttons">
            <button
              className="btn-test btn-block"
              onClick={handleTestBlock}
              disabled={testing}
            >
              {testing && testMode === 'block' ? '测试中...' : '🔲 阻塞式测试'}
            </button>
            <button
              className="btn-test btn-stream"
              onClick={handleTestStream}
              disabled={testing}
            >
              {testing && testMode === 'stream' ? '测试中...' : '⚡ 流式测试'}
            </button>
          </div>

          {showTestResult && (
            <div className="test-result">
              <pre>{testResult}</pre>
            </div>
          )}
        </div>
      </div>

      <div className="card-footer">
        <button className="btn-link" onClick={() => onEdit(config)}>
          编辑
        </button>
        {!config.is_default && (
          <button className="btn-link" onClick={() => onSetDefault(config.id)}>
            设为默认
          </button>
        )}
        <button className="btn-link btn-danger" onClick={() => onDelete(config.id)}>
          删除
        </button>
      </div>
    </div>
  );
}

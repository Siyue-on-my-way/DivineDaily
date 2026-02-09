import { useState } from 'react';
import { llmConfigApi } from '../../api/config';
import type { LLMConfig, LLMConfigCreateRequest } from '../../types/config';
import LLMConfigForm from './LLMConfigForm';
import './ConfigList.css';

interface Props {
  configs: LLMConfig[];
  onRefresh: () => void;
}

export default function LLMConfigList({ configs, onRefresh }: Props) {
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<LLMConfig | null>(null);
  const [testingId, setTestingId] = useState<number | null>(null);

  const handleCreate = () => {
    setEditingConfig(null);
    setShowForm(true);
  };

  const handleEdit = (config: LLMConfig) => {
    setEditingConfig(config);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个配置吗？')) {
      return;
    }
    try {
      await llmConfigApi.delete(id);
      alert('删除成功');
      onRefresh();
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败');
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await llmConfigApi.setDefault(id);
      alert('设置默认配置成功');
      onRefresh();
    } catch (error) {
      console.error('设置默认配置失败:', error);
      alert('设置默认配置失败');
    }
  };

  const handleTest = async (id: number) => {
    setTestingId(id);
    try {
      const response = await llmConfigApi.test(id);
      alert(`测试成功！\nLLM回复: ${response}`);
    } catch (error: any) {
      console.error('测试失败:', error);
      alert(error.response?.data?.detail || '测试失败');
    } finally {
      setTestingId(null);
    }
  };

  const handleFormSubmit = async (data: LLMConfigCreateRequest) => {
    try {
      if (editingConfig) {
        await llmConfigApi.update(editingConfig.id, data);
        alert('更新成功');
      } else {
        await llmConfigApi.create(data);
        alert('创建成功');
      }
      setShowForm(false);
      setEditingConfig(null);
      onRefresh();
    } catch (error: any) {
      console.error('操作失败:', error);
      alert(error.response?.data?.detail || '操作失败');
    }
  };

  return (
    <div className="config-list">
      <div className="config-list-header">
        <h2>LLM配置列表</h2>
        <button className="btn-primary" onClick={handleCreate}>
          + 新建配置
        </button>
      </div>

      {showForm && (
        <LLMConfigForm
          config={editingConfig}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setShowForm(false);
            setEditingConfig(null);
          }}
        />
      )}

      <div className="config-table-container">
        <table className="config-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>服务商</th>
              <th>模型名称</th>
              <th>温度</th>
              <th>最大Token</th>
              <th>默认</th>
              <th>启用</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {configs.length === 0 ? (
              <tr>
                <td colSpan={8} className="empty-state">
                  暂无配置，点击"新建配置"创建
                </td>
              </tr>
            ) : (
              configs.map((config) => (
                <tr key={config.id}>
                  <td>{config.name}</td>
                  <td>{config.provider}</td>
                  <td>{config.model_name}</td>
                  <td>{config.temperature}</td>
                  <td>{config.max_tokens}</td>
                  <td>
                    {config.is_default ? (
                      <span className="badge badge-success">是</span>
                    ) : (
                      <span className="badge">否</span>
                    )}
                  </td>
                  <td>
                    {config.is_enabled ? (
                      <span className="badge badge-success">启用</span>
                    ) : (
                      <span className="badge badge-disabled">禁用</span>
                    )}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn-link"
                        onClick={() => handleTest(config.id)}
                        disabled={testingId === config.id}
                      >
                        {testingId === config.id ? '测试中...' : '测试'}
                      </button>
                      <button
                        className="btn-link"
                        onClick={() => handleEdit(config)}
                      >
                        编辑
                      </button>
                      {!config.is_default && (
                        <button
                          className="btn-link"
                          onClick={() => handleSetDefault(config.id)}
                        >
                          设默认
                        </button>
                      )}
                      <button
                        className="btn-link btn-danger"
                        onClick={() => handleDelete(config.id)}
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}


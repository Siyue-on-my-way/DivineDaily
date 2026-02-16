import { useState } from 'react';
import { promptConfigApi } from '../../api/config';
import type { PromptConfig, PromptConfigCreateRequest } from '../../types/config';
import PromptConfigForm from './PromptConfigForm';
import PromptPreview from './PromptPreview';
import './ConfigList.css';

interface Props {
  configs: PromptConfig[];
  onRefresh: () => void;
}

export default function PromptConfigList({ configs, onRefresh }: Props) {
  const [showForm, setShowForm] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [editingConfig, setEditingConfig] = useState<PromptConfig | null>(null);
  const [previewConfig, setPreviewConfig] = useState<PromptConfig | null>(null);
  const [testingId, setTestingId] = useState<number | null>(null);

  const handleCreate = () => {
    setEditingConfig(null);
    setShowForm(true);
  };

  const handleEdit = (config: PromptConfig) => {
    setEditingConfig(config);
    setShowForm(true);
  };

  const handlePreview = (config: PromptConfig) => {
    setPreviewConfig(config);
    setShowPreview(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个配置吗？')) {
      return;
    }
    try {
      await promptConfigApi.delete(id);
      alert('删除成功');
      onRefresh();
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败');
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await promptConfigApi.setDefault(id);
      alert('设置默认配置成功');
      onRefresh();
    } catch (error) {
      console.error('设置默认配置失败:', error);
      alert('设置默认配置失败');
    }
  };

  const handleTest = async (config: PromptConfig) => {
    if (!confirm(`确定要测试 "${config.name}" 配置吗？\n\n将使用 test_case.json 中的测试数据进行测试。`)) {
      return;
    }
    
    setTestingId(config.id);
    try {
      const result = await promptConfigApi.test(config.id);
      
      if (result.success) {
        // 显示测试结果
        const message = `✅ 测试成功！\n\n` +
          `📝 测试用例: ${result.test_case.name}\n` +
          `🤖 LLM: ${result.config_info.llm_name} (${result.config_info.model})\n` +
          `🎯 关键词匹配: ${result.validation.keyword_match_rate}\n` +
          `✓ 找到: ${result.validation.found_keywords.join(', ')}\n` +
          `${result.validation.missing_keywords.length > 0 ? `✗ 缺失: ${result.validation.missing_keywords.join(', ')}\n` : ''}` +
          `\n📄 生成内容:\n${result.llm_response.substring(0, 200)}${result.llm_response.length > 200 ? '...' : ''}`;
        
        alert(message);
      } else {
        alert(`❌ 测试失败\n\n错误: ${result.error}`);
      }
    } catch (error: any) {
      console.error('测试失败:', error);
      const errorMsg = error.response?.data?.detail || error.message || '测试失败';
      alert(`❌ 测试失败\n\n${errorMsg}`);
    } finally {
      setTestingId(null);
    }
  };

  const handleFormSubmit = async (data: PromptConfigCreateRequest) => {
    try {
      if (editingConfig) {
        await promptConfigApi.update(editingConfig.id, data);
        alert('更新成功');
      } else {
        await promptConfigApi.create(data);
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
        <h2>Assistant 配置列表</h2>
        <button className="btn-primary" onClick={handleCreate}>
          + 新建配置
        </button>
      </div>

      {showForm && (
        <PromptConfigForm
          config={editingConfig}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setShowForm(false);
            setEditingConfig(null);
          }}
        />
      )}

      {showPreview && previewConfig && (
        <PromptPreview
          config={previewConfig}
          onClose={() => {
            setShowPreview(false);
            setPreviewConfig(null);
          }}
        />
      )}

      <div className="config-table-container">
        <table className="config-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>Prompt类型</th>
              <th>问题类型</th>
              <th>关联模型</th>
              <th>默认</th>
              <th>启用</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {configs.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-state">
                  暂无配置，点击"新建配置"创建
                </td>
              </tr>
            ) : (
              configs.map((config) => (
                <tr key={config.id}>
                  <td>{config.name}</td>
                  <td>
                    <span className="badge badge-info">{config.prompt_type}</span>
                  </td>
                  <td>
                    <span className="badge badge-info">{config.question_type}</span>
                  </td>
                  <td>
                    {config.llm_config_name ? (
                      <span className="badge badge-primary">{config.llm_config_name}</span>
                    ) : (
                      <span className="badge">未设置</span>
                    )}
                  </td>
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
                        onClick={() => handleEdit(config)}
                      >
                        编辑
                      </button>
                      <button
                        className="btn-link"
                        onClick={() => handlePreview(config)}
                      >
                        预览
                      </button>
                      <button
                        className="btn-link btn-test"
                        onClick={() => handleTest(config)}
                        disabled={testingId === config.id}
                      >
                        {testingId === config.id ? '测试中...' : '测试'}
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

import { useState, useEffect } from 'react';
import { llmConfigApi } from '../api/config';
import type { LLMConfig } from '../types/config';
import LLMConfigCard from '../components/config/LLMConfigCard';
import LLMConfigModal from '../components/config/LLMConfigModal';
import { toast } from '../hooks/useToast';
import './ConfigManagement.css';

export default function ConfigManagement() {
  const [configs, setConfigs] = useState<LLMConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingConfig, setEditingConfig] = useState<LLMConfig | null>(null);

  // 加载配置列表
  const loadConfigs = async () => {
    setLoading(true);
    try {
      const data = await llmConfigApi.list();
      setConfigs(data);
    } catch (error) {
      console.error('加载配置失败:', error);
      toast.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfigs();
  }, []);

  const handleCreate = () => {
    setEditingConfig(null);
    setShowModal(true);
  };

  const handleEdit = (config: LLMConfig) => {
    setEditingConfig(config);
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个模型配置吗？')) {
      return;
    }
    try {
      await llmConfigApi.delete(id);
      toast.success('删除成功');
      loadConfigs();
    } catch (error: any) {
      console.error('删除失败:', error);
      toast.error(error.response?.data?.detail || '删除失败');
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await llmConfigApi.setDefault(id);
      toast.success('设置默认成功');
      loadConfigs();
    } catch (error: any) {
      console.error('设置默认失败:', error);
      toast.error(error.response?.data?.detail || '设置默认失败');
    }
  };

  return (
    <div className="config-management">
      <div className="config-header">
        <div>
          <h1>LLM 模型配置</h1>
          <p className="config-subtitle">管理 LLM 模型配置，包括 API 密钥、端点等</p>
        </div>
        <button className="btn-primary" onClick={handleCreate}>
          + 新建配置
          </button>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>加载中...</p>
        </div>
      ) : configs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🤖</div>
          <h3>暂无模型配置</h3>
          <p>点击"新建配置"创建第一个 LLM 模型配置</p>
          <button className="btn-primary" onClick={handleCreate}>
            + 新建配置
          </button>
        </div>
      ) : (
        <div className="config-grid">
          {configs.map((config) => (
            <LLMConfigCard
              key={config.id}
              config={config}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onSetDefault={handleSetDefault}
              onRefresh={loadConfigs}
            />
          ))}
      </div>
      )}

      {showModal && (
        <LLMConfigModal
          config={editingConfig}
          onClose={() => {
            setShowModal(false);
            setEditingConfig(null);
          }}
          onSuccess={() => {
            setShowModal(false);
            setEditingConfig(null);
            loadConfigs();
          }}
          />
        )}
      </div>
  );
}

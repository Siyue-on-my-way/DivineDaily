import { useEffect, useState } from 'react';
import { UserDivination } from '../../types/user';
import './DivinationDetailModal.css';

interface DivinationDetailModalProps {
  divination: UserDivination | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function DivinationDetailModal({
  divination,
  isOpen,
  onClose,
}: DivinationDetailModalProps) {
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsClosing(false);
      onClose();
    }, 300);
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  if (!isOpen || !divination) return null;

  const getTypeIcon = (version: string) => {
    if (version.includes('iching') || version.includes('易经') || version === 'CN') return '☯️';
    if (version.includes('tarot') || version.includes('塔罗') || version === 'TAROT') return '🃏';
    if (version.includes('fortune') || version.includes('运势')) return '🔮';
    return '📖';
  };

  const getTypeName = (version: string) => {
    if (version.includes('iching') || version.includes('易经') || version === 'CN') return '易经占卜';
    if (version.includes('tarot') || version.includes('塔罗') || version === 'TAROT') return '塔罗占卜';
    if (version.includes('fortune') || version.includes('运势')) return '运势占卜';
    return '占卜';
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { text: string; className: string }> = {
      completed: { text: '已完成', className: 'completed' },
      pending: { text: '进行中', className: 'pending' },
      processing: { text: '处理中', className: 'pending' },
      failed: { text: '失败', className: 'failed' },
    };
    const statusInfo = statusMap[status] || { text: status, className: 'unknown' };
    return <span className={`status-badge ${statusInfo.className}`}>{statusInfo.text}</span>;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const renderMarkdown = (text: string) => {
    if (!text) return null;
    
    // 简单的 Markdown 渲染（支持标题、加粗、列表）
    const lines = text.split('\n');
    return lines.map((line, index) => {
      // 标题
      if (line.startsWith('## ')) {
        return <h3 key={index} className="md-h3">{line.substring(3)}</h3>;
      }
      if (line.startsWith('### ')) {
        return <h4 key={index} className="md-h4">{line.substring(4)}</h4>;
      }
      
      // 列表
      if (line.startsWith('- ')) {
        return <li key={index} className="md-li">{line.substring(2)}</li>;
      }
      
      // 加粗
      const boldText = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // 空行
      if (line.trim() === '') {
        return <br key={index} />;
      }
      
      return <p key={index} className="md-p" dangerouslySetInnerHTML={{ __html: boldText }} />;
    });
  };

  return (
    <div 
      className={`divination-modal-overlay ${isClosing ? 'closing' : ''}`}
      onClick={handleBackdropClick}
    >
      <div className={`divination-modal ${isClosing ? 'closing' : ''}`}>
        <div className="modal-header">
          <div className="modal-title">
            <span className="modal-icon">{getTypeIcon(divination.version)}</span>
            <h2>{getTypeName(divination.version)}</h2>
            {getStatusBadge(divination.status)}
          </div>
          <button className="close-btn" onClick={handleClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {/* 基本信息 */}
          <div className="detail-section">
            <div className="section-header">
              <span className="section-icon">📋</span>
              <h3>基本信息</h3>
            </div>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">占卜ID:</span>
                <span className="info-value">{divination.id}</span>
              </div>
              <div className="info-item">
                <span className="info-label">占卜时间:</span>
                <span className="info-value">{formatDate(divination.created_at)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">占卜类型:</span>
                <span className="info-value">{getTypeName(divination.version)}</span>
              </div>
              {divination.event_type && (
                <div className="info-item">
                  <span className="info-label">事件类型:</span>
                  <span className="info-value">{divination.event_type}</span>
                </div>
              )}
            </div>
          </div>

          {/* 问题 */}
          <div className="detail-section">
            <div className="section-header">
              <span className="section-icon">❓</span>
              <h3>占卜问题</h3>
            </div>
            <div className="question-box">
              {divination.question}
            </div>
          </div>

          {/* 结果摘要 */}
          {divination.result_summary && (
            <div className="detail-section">
              <div className="section-header">
                <span className="section-icon">✨</span>
                <h3>占卜结果</h3>
              </div>
              <div className="result-box">
                {renderMarkdown(divination.result_summary)}
              </div>
            </div>
          )}

          {/* 如果没有结果 */}
          {!divination.result_summary && divination.status === 'completed' && (
            <div className="detail-section">
              <div className="empty-result">
                <span className="empty-icon">📭</span>
                <p>暂无详细结果</p>
              </div>
            </div>
          )}

          {/* 处理中状态 */}
          {divination.status === 'processing' && (
            <div className="detail-section">
              <div className="processing-box">
                <span className="processing-icon">⏳</span>
                <p>占卜正在处理中，请稍候...</p>
              </div>
            </div>
          )}

          {/* 失败状态 */}
          {divination.status === 'failed' && (
            <div className="detail-section">
              <div className="error-box">
                <span className="error-icon">❌</span>
                <p>占卜处理失败</p>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={handleClose}>
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}

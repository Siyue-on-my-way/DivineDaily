import { useEffect, useState } from 'react';
import { getUserDivinationDetail } from '../../api/user';
import { UserDivination, UserDivinationDetail } from '../../types/user';
import './DivinationDetailModal.css';

interface DivinationDetailModalProps {
  userId: number;
  divination: UserDivination | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function DivinationDetailModal({
  userId,
  divination,
  isOpen,
  onClose,
}: DivinationDetailModalProps) {
  const [isClosing, setIsClosing] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState<string>('');
  const [divinationDetail, setDivinationDetail] = useState<UserDivinationDetail | null>(null);

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

  useEffect(() => {
    if (!isOpen || !divination?.id || !userId) return;

    const loadDetail = async () => {
      setLoadingDetail(true);
      setDetailError('');
      try {
        const detail = await getUserDivinationDetail(userId, divination.id);
        setDivinationDetail(detail);
      } catch (error: any) {
        setDetailError(error?.response?.data?.detail || '加载占卜详情失败');
        setDivinationDetail(null);
      } finally {
        setLoadingDetail(false);
      }
    };

    loadDetail();
  }, [isOpen, userId, divination?.id]);

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

  const currentDivination = divinationDetail || divination;
  const hexagramInfo = divinationDetail?.result_data?.hexagram_info;
  const recommendations = divinationDetail?.result_data?.recommendations || [];
  const yarrowLines = divinationDetail?.result_data?.yarrow_trace?.lines || [];

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
            <span className="modal-icon">{getTypeIcon(currentDivination.version)}</span>
            <h2>{getTypeName(currentDivination.version)}</h2>
            {getStatusBadge(currentDivination.status)}
          </div>
          <button className="close-btn" onClick={handleClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {loadingDetail && (
            <div className="detail-section">
              <div className="processing-box">
                <span className="processing-icon">⏳</span>
                <p>正在加载完整详情...</p>
              </div>
            </div>
          )}

          {!!detailError && (
            <div className="detail-section">
              <div className="error-box">
                <span className="error-icon">⚠️</span>
                <p>{detailError}</p>
              </div>
            </div>
          )}

          {/* 基本信息 */}
          <div className="detail-section">
            <div className="section-header">
              <span className="section-icon">📋</span>
              <h3>基本信息</h3>
            </div>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">占卜ID:</span>
                <span className="info-value">{currentDivination.id}</span>
              </div>
              <div className="info-item">
                <span className="info-label">占卜时间:</span>
                <span className="info-value">{formatDate(currentDivination.created_at)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">占卜类型:</span>
                <span className="info-value">{getTypeName(currentDivination.version)}</span>
              </div>
              {currentDivination.event_type && (
                <div className="info-item">
                  <span className="info-label">事件类型:</span>
                  <span className="info-value">{currentDivination.event_type}</span>
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
              {currentDivination.question}
            </div>
          </div>

          {/* 卦象信息 */}
          {hexagramInfo && (
            <div className="detail-section">
              <div className="section-header">
                <span className="section-icon">🧿</span>
                <h3>卦象信息</h3>
              </div>
              <div className="info-grid">
                <div className="info-item"><span className="info-label">卦号</span><span className="info-value">{hexagramInfo.number ?? '-'}</span></div>
                <div className="info-item"><span className="info-label">卦名</span><span className="info-value">{hexagramInfo.name || '-'}</span></div>
                <div className="info-item"><span className="info-label">上卦</span><span className="info-value">{hexagramInfo.upper_trigram || '-'}</span></div>
                <div className="info-item"><span className="info-label">下卦</span><span className="info-value">{hexagramInfo.lower_trigram || '-'}</span></div>
                <div className="info-item"><span className="info-label">吉凶</span><span className="info-value">{hexagramInfo.outcome || '-'}</span></div>
                <div className="info-item"><span className="info-label">五行</span><span className="info-value">{hexagramInfo.wuxing || '-'}</span></div>
              </div>
            </div>
          )}

          {/* 变爻与起卦过程 */}
          {(hexagramInfo?.changing_lines?.length || yarrowLines.length) && (
            <div className="detail-section">
              <div className="section-header">
                <span className="section-icon">📐</span>
                <h3>变爻与起卦过程</h3>
              </div>
              <div className="result-box">
                {hexagramInfo?.changing_lines?.length ? (
                  <p className="md-p">变爻：第 {hexagramInfo.changing_lines.map((i) => i + 1).join('、')} 爻</p>
                ) : (
                  <p className="md-p">无变爻</p>
                )}
                {yarrowLines.length > 0 && (
                  <div>
                    <p className="md-p"><strong>起卦过程（六爻）</strong></p>
                    <ul>
                      {yarrowLines.map((line, idx) => (
                        <li key={`${idx}-${line.line_index}`} className="md-li">
                          第{line.line_index ?? idx + 1}爻：{line.line_type || line.line_value || '-'}
                          {line.is_changing ? '（变）' : ''}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 建议 */}
          {recommendations.length > 0 && (
            <div className="detail-section">
              <div className="section-header">
                <span className="section-icon">🧭</span>
                <h3>建议</h3>
              </div>
              <div className="result-box">
                {recommendations.map((item, idx) => (
                  <div key={`rec-${idx}`}>
                    {item.title && <h4 className="md-h4">{item.title}</h4>}
                    {item.content && <p className="md-p">{item.content}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 原始摘要 */}
          {currentDivination.result_summary && (
            <div className="detail-section">
              <div className="section-header">
                <span className="section-icon">✨</span>
                <h3>原始摘要</h3>
              </div>
              <div className="result-box">
                {renderMarkdown(currentDivination.result_summary)}
              </div>
            </div>
          )}

          {/* 原始详情 */}
          {divinationDetail?.result_detail && (
            <div className="detail-section">
              <div className="section-header">
                <span className="section-icon">📜</span>
                <h3>原始详情</h3>
              </div>
              <div className="result-box">
                {renderMarkdown(divinationDetail.result_detail)}
              </div>
            </div>
          )}

          {!currentDivination.result_summary && currentDivination.status === 'completed' && (
            <div className="detail-section">
              <div className="empty-result">
                <span className="empty-icon">📭</span>
                <p>暂无详细结果</p>
              </div>
            </div>
          )}

          {currentDivination.status === 'processing' && (
            <div className="detail-section">
              <div className="processing-box">
                <span className="processing-icon">⏳</span>
                <p>占卜正在处理中，请稍候...</p>
              </div>
            </div>
          )}

          {currentDivination.status === 'failed' && (
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

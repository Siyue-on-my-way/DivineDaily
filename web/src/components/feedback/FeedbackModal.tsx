import { useState } from 'react';
import { Button } from '../mobile/Button';
import './FeedbackModal.css';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  feedbackType: 'quality' | 'accuracy' | 'helpfulness';
  onSubmit: (feedback: FeedbackData) => Promise<void>;
}

export interface FeedbackData {
  rating: number;
  comment?: string;
  tags: string[];
  isHelpful?: boolean;
}

export function FeedbackModal({
  isOpen,
  onClose,
  sessionId: _sessionId,
  feedbackType,
  onSubmit
}: FeedbackModalProps) {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [isHelpful, setIsHelpful] = useState<boolean | undefined>();
  const [submitting, setSubmitting] = useState(false);

  const tagOptions: Record<string, string[]> = {
    quality: ['清晰明确', '有深度', '易理解', '不够具体', '太简单'],
    accuracy: ['非常准确', '比较准确', '一般', '不太准', '完全不准'],
    helpfulness: ['很有帮助', '有一定帮助', '帮助不大', '没有帮助']
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      alert('请先评分');
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        rating,
        comment: comment.trim() || undefined,
        tags: selectedTags,
        isHelpful
      });
      // 重置表单
      setRating(0);
      setComment('');
      setSelectedTags([]);
      setIsHelpful(undefined);
      onClose();
    } catch (error) {
      console.error('提交反馈失败', error);
      alert('提交失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  if (!isOpen) return null;

  return (
    <div className="feedback-modal-overlay" onClick={onClose}>
      <div className="feedback-modal" onClick={(e) => e.stopPropagation()}>
        <div className="feedback-modal-header">
          <h3>反馈评价</h3>
          <button className="feedback-modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="feedback-modal-body">
          {/* 星级评分 */}
          <div className="feedback-rating">
            <label>整体评分</label>
            <div className="stars">
              {[1, 2, 3, 4, 5].map(star => (
                <span
                  key={star}
                  className={`star ${star <= rating ? 'active' : ''}`}
                  onClick={() => setRating(star)}
                >
                  ★
                </span>
              ))}
            </div>
          </div>

          {/* 标签选择 */}
          <div className="feedback-tags">
            <label>选择标签（可多选）</label>
            <div className="tag-list">
              {tagOptions[feedbackType].map(tag => (
                <button
                  key={tag}
                  className={`tag ${selectedTags.includes(tag) ? 'selected' : ''}`}
                  onClick={() => toggleTag(tag)}
                  type="button"
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* 是否有帮助 */}
          <div className="feedback-helpful">
            <label>这个结果对你有帮助吗？</label>
            <div className="helpful-buttons">
              <button
                type="button"
                className={isHelpful === true ? 'active' : ''}
                onClick={() => setIsHelpful(true)}
              >
                👍 有帮助
              </button>
              <button
                type="button"
                className={isHelpful === false ? 'active' : ''}
                onClick={() => setIsHelpful(false)}
              >
                👎 没帮助
              </button>
            </div>
          </div>

          {/* 文字反馈 */}
          <div className="feedback-comment">
            <label>补充说明（可选）</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="请告诉我们更多想法..."
              rows={4}
              maxLength={500}
            />
            <div className="char-count">{comment.length}/500</div>
          </div>
        </div>

        {/* 提交按钮 */}
        <div className="feedback-modal-footer">
          <Button variant="secondary" onClick={onClose}>
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={submitting || rating === 0}
          >
            {submitting ? '提交中...' : '提交反馈'}
          </Button>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MobilePage } from '../mobile';
import { Button } from '../mobile/Button';
import { Textarea } from '../mobile/Input';
import { Card, CardContent } from '../mobile/Card';
import DivinationResultCard from './DivinationResultCard';
import { DivinationLoading } from './DivinationLoading';
import { useAuth } from '../../lib/AuthContext';
import { useDivinationPolling } from '../../hooks/useDivinationPolling';
import { toast } from '../../hooks/useToast';
import axiosInstance from '../../lib/axios';
import type { DivinationResult } from '../../types/divination';
import './RitualFlow.css';

const STAGES = {
  QUESTION: 0,
  LOADING: 1,
  RESULT: 2
};

/**
 * 占卜流程主组件
 * 
 * 管理占卜的完整流程：问题输入 -> 占卜执行 -> 结果展示
 * 问题质量由后端智能判断，前端无需提醒
 */
export default function RitualFlow() {
  const { isAuthenticated, setShowLoginModal, user } = useAuth();
  const [stage, setStage] = useState(STAGES.QUESTION);
  const [question, setQuestion] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [result, setResult] = useState<DivinationResult | null>(null);

  // 始终调用 Hook（符合 React Hooks 规则），通过空 sessionId 来控制是否执行轮询
  const polling = useDivinationPolling({
    sessionId: sessionId,
    onSuccess: (data) => {
      setResult(data);
      setStage(STAGES.RESULT);
      setSessionId('');
    },
    onError: (error) => {
      console.error('Divination polling failed', error);
      setStage(STAGES.QUESTION);
      setSessionId('');
      toast.error(error.message || '占卜失败，请重试');
    },
    maxAttempts: 60,
    interval: 1000,
  });

  /**
   * 开始占卜
   * 简化流程：直接提交问题，后端智能处理
   */
  const startDivination = async () => {
    // 检查登录状态
    if (!isAuthenticated) {
      setShowLoginModal(true);
      return;
    }

    if (!question.trim()) {
      toast.warning('请输入您的问题');
      return;
    }
    
    setStage(STAGES.LOADING);

    try {
      const startRes = await axiosInstance.post('/divinations/start', {
        user_id: user?.id || 'unknown',
        question: question,
        version: 'CN',
        orientation: 'E'
      });

      const sessionIdFromResponse = startRes.data.session_id || startRes.data.id;
      
      if (!sessionIdFromResponse) {
        // 直接返回结果的情况（低质量问题）
        if (startRes.data.summary && startRes.data.detail) {
          setResult(startRes.data);
          setStage(STAGES.RESULT);
          return;
        }
        throw new Error('未获取到有效的会话ID');
      }
      
      setSessionId(sessionIdFromResponse);
      
    } catch (err: any) {
      console.error('Divination failed', err);
      setStage(STAGES.QUESTION);
      
      // 根据错误类型提供友好的错误提示
      const errorMessage = err.response?.data?.detail || err.response?.data?.message;
      if (err.response?.status === 500) {
        toast.error('服务器繁忙，请稍后重试');
      } else if (err.response?.status === 401) {
        toast.error('登录已过期，请重新登录');
        setShowLoginModal(true);
      } else if (errorMessage) {
        toast.error(errorMessage);
      } else {
        toast.error('占卜失败，请检查网络连接后重试');
      }
    }
  };

  /**
   * 重置占卜状态，返回问题输入页面
   */
  const resetDivination = () => {
    polling.cancel();
    setStage(STAGES.QUESTION);
    setQuestion('');
    setResult(null);
    setSessionId('');
  };

  /**
   * 取消正在进行的占卜
   */
  const handleCancelLoading = () => {
    polling.cancel();
    setStage(STAGES.QUESTION);
    setSessionId('');
    toast.info('已取消占卜');
  };

  return (
    <AnimatePresence mode="wait">
      {stage === STAGES.QUESTION && (
        <motion.div
          key="question"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <MobilePage>
            <div className="ritual-header">
              <h2 className="ritual-title">🌿 开始你的占卜之旅</h2>
              <p className="ritual-subtitle">诚心发问，静待答案</p>
            </div>

            <div className="ritual-section">
              <Textarea
                label="你的问题"
                placeholder="请输入你想要占卜的问题...&#10;&#10;例如：&#10;• 我应该和什么样的人谈恋爱？&#10;• 我该跳槽到新公司吗？&#10;• 今天适合表白吗？"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={6}
                maxLength={200}
                showCounter
                required
              />
            </div>

            <Card variant="gradient" size="sm">
              <CardContent>
                <div className="ritual-tip">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 16v-4"/>
                    <path d="M12 8h.01"/>
                  </svg>
                  <span>AI 会智能分析你的问题，给出最适合的回答</span>
                </div>
              </CardContent>
            </Card>

            {!isAuthenticated && (
              <Card variant="primary" size="sm">
                <CardContent>
                  <div className="ritual-login-prompt">
                    <span>⚠️ 请先登录后再进行占卜</span>
                  </div>
                </CardContent>
              </Card>
            )}

            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={startDivination}
              disabled={!question.trim()}
              icon={<span>🔮</span>}
            >
              {isAuthenticated ? '开始占卜' : '登录后占卜'}
            </Button>
          </MobilePage>
        </motion.div>
      )}

      {stage === STAGES.LOADING && (
        <DivinationLoading onCancel={handleCancelLoading} />
      )}

      {stage === STAGES.RESULT && result && (
        <motion.div
          key="result"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <MobilePage>
            <DivinationResultCard result={result} />
            <div className="ritual-actions">
              <Button variant="secondary" fullWidth onClick={resetDivination}>
                再占一次
              </Button>
            </div>
          </MobilePage>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

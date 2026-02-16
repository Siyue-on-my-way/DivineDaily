import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MobilePage } from '../mobile';
import { Button } from '../mobile/Button';
import { Textarea } from '../mobile/Input';
import { Card, CardContent } from '../mobile/Card';
import DivinationResultCard from './DivinationResultCard';
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
    maxAttempts: 30,
    interval: 1000,
  });

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

      // 修复：后端返回的是 session_id，不是 id
      const sessionIdFromResponse = startRes.data.session_id || startRes.data.id;
      
      if (!sessionIdFromResponse) {
        // 如果后端直接返回了完整结果（不需要轮询）
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
      toast.error(err.response?.data?.message || '占卜失败，请重试');
    }
  };

  const resetDivination = () => {
    // 取消正在进行的轮询
    polling.cancel();
    setStage(STAGES.QUESTION);
    setQuestion('');
    setResult(null);
    setSessionId('');
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
                placeholder="请输入你想要占卜的问题...&#10;&#10;例如：&#10;• 我应该和研究生学妹谈恋爱还是和大一学妹谈？&#10;• 我该跳槽到新公司吗？&#10;• 今天适合表白吗？"
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
                  <span>AI 会自动分析你的问题类型，无需手动选择</span>
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
        <motion.div
          key="loading"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <MobilePage centered>
            <div className="ritual-loading">
              <div className="ritual-loading-icon">🔮</div>
              <div className="ritual-loading-spinner" />
              <h3 className="ritual-loading-title">正在占卜中...</h3>
              <p className="ritual-loading-text">AI 正在分析问题并解读卦象</p>
            </div>
          </MobilePage>
        </motion.div>
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

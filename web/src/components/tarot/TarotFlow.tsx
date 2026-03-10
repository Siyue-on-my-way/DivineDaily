import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MobilePage } from '../mobile';
import { Button } from '../mobile/Button';
import { Textarea } from '../mobile/Input';
import { Card, CardContent } from '../mobile/Card';
import TarotResultCard from './TarotResultCard';
import { useAuth } from '../../lib/AuthContext';
import { useDivinationPolling } from '../../hooks/useDivinationPolling';
import { toast } from '../../hooks/useToast';
import axiosInstance from '../../lib/axios';
import type { DivinationResult } from '../../types/divination';
import './TarotFlow.css';

const STAGES = {
  SPREAD_SELECT: 0,
  QUESTION: 1,
  SHUFFLE: 2,
  LOADING: 3,
  RESULT: 4,
};

const SPREAD_OPTIONS = [
  {
    id: 'single',
    name: '单张牌',
    description: '快速获得简单明了的答案',
    icon: '🃏',
    cards: 1
  },
  {
    id: 'three',
    name: '三张牌阵',
    description: '了解过去、现在和未来',
    icon: '🎴',
    cards: 3
  },
  {
    id: 'cross',
    name: '十字牌阵',
    description: '深入分析复杂问题',
    icon: '✨',
    cards: 10
  }
];

export default function TarotFlow() {
  const { isAuthenticated, setShowLoginModal, user } = useAuth();
  const [stage, setStage] = useState(STAGES.SPREAD_SELECT);
  const [selectedSpread, setSelectedSpread] = useState<string>('');
  const [question, setQuestion] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [result, setResult] = useState<DivinationResult | null>(null);
  const [cutPosition, setCutPosition] = useState<number>(50);
  const [shuffleTrace, setShuffleTrace] = useState<number[]>([]);

  // 始终调用 Hook（符合 React Hooks 规则）
  const polling = useDivinationPolling({
    sessionId: sessionId,
    onSuccess: (data) => {
      setResult(data);
      setStage(STAGES.RESULT);
      setSessionId('');
    },
    onError: (error) => {
      console.error('Tarot polling failed', error);
      setStage(STAGES.QUESTION);
      setSessionId('');
      toast.error(error.message || '塔罗占卜失败，请重试');
    },
    maxAttempts: 30,
    interval: 1000,
  });

  const selectSpread = (spreadId: string) => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
      return;
    }
    setSelectedSpread(spreadId);
    setStage(STAGES.QUESTION);
  };

  const startTarotReading = async () => {
    if (!question.trim()) {
      toast.warning('请输入您的问题');
      return;
    }
    
    setStage(STAGES.LOADING);

    try {
      const startRes = await axiosInstance.post('/divinations/start', {
        user_id: user?.id || 'unknown',
        question: question,
        version: 'TAROT',
        spread: selectedSpread,
        orientation: 'E',
        context: {
          tarot_interaction: {
            spread: selectedSpread,
            cut_position: cutPosition,
            shuffle_trace: shuffleTrace.slice(-20),
          },
        },
      });

      setSessionId(startRes.data.session_id);
      
    } catch (err: any) {
      console.error('Tarot reading failed', err);
      setStage(STAGES.QUESTION);
      toast.error(err.response?.data?.message || '塔罗占卜失败，请重试');
    }
  };

  const resetTarotReading = () => {
    polling.cancel();
    setStage(STAGES.SPREAD_SELECT);
    setSelectedSpread('');
    setQuestion('');
    setResult(null);
    setSessionId('');
    setCutPosition(50);
    setShuffleTrace([]);
  };

  const goBackToSpreadSelect = () => {
    setStage(STAGES.SPREAD_SELECT);
    setSelectedSpread('');
    setQuestion('');
    setCutPosition(50);
    setShuffleTrace([]);
  };

  return (
    <AnimatePresence mode="wait">
      {stage === STAGES.SPREAD_SELECT && (
        <motion.div
          key="spread-select"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <MobilePage>
            <div className="tarot-header">
              <h2 className="tarot-title">🔮 选择塔罗牌阵</h2>
              <p className="tarot-subtitle">不同的牌阵适合不同类型的问题</p>
            </div>

            <div className="tarot-spread-grid">
              {SPREAD_OPTIONS.map((spread) => (
                <Card
                  key={spread.id}
                  variant="glass"
                  className="tarot-spread-card"
                  onClick={() => selectSpread(spread.id)}
                >
                  <CardContent>
                    <div className="tarot-spread-icon">{spread.icon}</div>
                    <h3 className="tarot-spread-name">{spread.name}</h3>
                    <p className="tarot-spread-description">{spread.description}</p>
                    <div className="tarot-spread-cards">
                      {spread.cards} 张牌
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {!isAuthenticated && (
              <Card variant="primary" size="sm">
                <CardContent>
                  <div className="tarot-login-prompt">
                    <span>⚠️ 请先登录后再进行塔罗占卜</span>
                  </div>
                </CardContent>
              </Card>
            )}
          </MobilePage>
        </motion.div>
      )}

      {stage === STAGES.QUESTION && (
        <motion.div
          key="question"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <MobilePage>
            <div className="tarot-header">
              <h2 className="tarot-title">
                {SPREAD_OPTIONS.find(s => s.id === selectedSpread)?.icon} {SPREAD_OPTIONS.find(s => s.id === selectedSpread)?.name}
              </h2>
              <p className="tarot-subtitle">诚心发问，静待塔罗的指引</p>
            </div>

            <div className="tarot-section">
              <Textarea
                label="你的问题"
                placeholder="请输入你想要占卜的问题...&#10;&#10;例如：&#10;• 我和TA的关系会如何发展？&#10;• 这次面试能成功吗？&#10;• 我应该接受这个工作机会吗？"
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
                <div className="tarot-tip">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 16v-4"/>
                    <path d="M12 8h.01"/>
                  </svg>
                  <span>塔罗牌会为你揭示问题的深层含义</span>
                </div>
              </CardContent>
            </Card>

            <div className="tarot-actions">
              <Button
                variant="secondary"
                size="lg"
                onClick={goBackToSpreadSelect}
              >
                返回选择牌阵
              </Button>
              <Button
                variant="primary"
                size="lg"
                onClick={() => setStage(STAGES.SHUFFLE)}
                disabled={!question.trim()}
                icon={<span>🃏</span>}
              >
                开始洗牌
              </Button>
            </div>
          </MobilePage>
        </motion.div>
      )}

      {stage === STAGES.SHUFFLE && (
        <motion.div
          key="shuffle"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <MobilePage>
            <div className="tarot-header">
              <h2 className="tarot-title">🃏 洗牌与切牌</h2>
              <p className="tarot-subtitle">滑动来感受洗牌的过程，选择一个直觉中的切牌位置</p>
            </div>

            <div className="tarot-section">
              <Card variant="glass">
                <CardContent>
                  <div className="tarot-shuffle-visual">
                    <div className="tarot-loading-cards">
                      <div className="tarot-loading-card">🃏</div>
                      <div className="tarot-loading-card">🃏</div>
                      <div className="tarot-loading-card">🃏</div>
                    </div>
                    <p className="tarot-shuffle-text">
                      缓缓滑动下面的滑块，就像你亲手在洗牌、切牌。
                    </p>
                  </div>

                  <div className="tarot-shuffle-control">
                    <label className="tarot-shuffle-label">
                      切牌位置（{cutPosition}%）
                    </label>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={cutPosition}
                      onChange={(e) => {
                        const value = Number(e.target.value);
                        setCutPosition(value);
                        setShuffleTrace((prev) =>
                          [...prev, value].slice(-100)
                        );
                      }}
                    />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="tarot-actions">
              <Button
                variant="secondary"
                size="lg"
                onClick={() => setStage(STAGES.QUESTION)}
              >
                返回修改问题
              </Button>
              <Button
                variant="primary"
                size="lg"
                onClick={startTarotReading}
                icon={<span>🔮</span>}
              >
                抽牌并解读
              </Button>
            </div>
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
            <div className="tarot-loading">
              <div className="tarot-loading-cards">
                <div className="tarot-loading-card">🃏</div>
                <div className="tarot-loading-card">🃏</div>
                <div className="tarot-loading-card">🃏</div>
              </div>
              <h3 className="tarot-loading-title">正在抽取塔罗牌...</h3>
              <p className="tarot-loading-text">AI 正在解读牌面含义</p>
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
            <TarotResultCard result={result} />
            <div className="tarot-actions">
              <Button variant="secondary" fullWidth onClick={resetTarotReading}>
                再占一次
              </Button>
            </div>
          </MobilePage>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

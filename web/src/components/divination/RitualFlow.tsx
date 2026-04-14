import { useEffect, useMemo, useRef, useState } from 'react';
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
import { formatApiErrorMessage } from '../../utils/apiError';
import './RitualFlow.css';

type Stage = 'QUESTION' | 'RITUAL' | 'CASTING' | 'LOADING' | 'REVEAL' | 'RESULT';

type RitualSplit = { left: number; right: number };

interface RitualContextPayload {
  ritual: {
    focus_duration_ms: number;
    press_duration_ms: number;
    tap_rhythm: number[];
    split_counts: RitualSplit[];
    client_timestamp: number;
    client_seed: string;
  };
}

const DURATION_HISTORY_KEY = 'divination_duration_history_buckets_v1';
const DURATION_HISTORY_LIMIT = 8;
const POLLING_MAX_ATTEMPTS = 60;

export default function RitualFlow() {
  const { isAuthenticated, setShowLoginModal, user } = useAuth();
  const [stage, setStage] = useState<Stage>('QUESTION');
  const [question, setQuestion] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [result, setResult] = useState<DivinationResult | null>(null);
  const [pollingElapsed, setPollingElapsed] = useState(0);
  const [pollingAttempts, setPollingAttempts] = useState(0);

  const [focusDone, setFocusDone] = useState(false);
  const [focusDurationMs, setFocusDurationMs] = useState(0);
  const focusStartRef = useRef<number>(0);

  const [pressDurationMs, setPressDurationMs] = useState(0);
  const pressStartRef = useRef<number>(0);
  const [holdDone, setHoldDone] = useState(false);
  const [tapRhythm, setTapRhythm] = useState<number[]>([]);
  const lastTapRef = useRef<number>(0);

  const [splitCounts, setSplitCounts] = useState<RitualSplit[]>([]);
  const [dragPosition, setDragPosition] = useState(0);
  const [revealIndex, setRevealIndex] = useState(0);

  const inferQuestionBucket = (text: string): string => {
    const q = text.toLowerCase();
    if (/恋爱|感情|婚姻|对象|分手|relationship/.test(q)) return 'relationship';
    if (/工作|事业|升职|跳槽|职场|career/.test(q)) return 'career';
    if (/运势|财运|今日|明天|fortune/.test(q)) return 'fortune';
    if (/知识|是什么|为什么|原理|knowledge/.test(q)) return 'knowledge';
    return 'general';
  };

  const activeQuestionBucket = useMemo(() => inferQuestionBucket(question), [question]);

  const estimatedRemainingSeconds = useMemo(() => {
    if (pollingElapsed <= 0) return undefined;
    try {
      const raw = localStorage.getItem(DURATION_HISTORY_KEY);
      if (!raw) return undefined;
      const bucketMap = JSON.parse(raw) as Record<string, number[]>;
      const bucketHistory = bucketMap?.[activeQuestionBucket] || [];
      const fallbackHistory = bucketMap?.general || [];
      const historySource = bucketHistory.length > 0 ? bucketHistory : fallbackHistory;
      const valid = historySource.filter((v) => Number.isFinite(v) && v > 0);
      if (valid.length === 0) return undefined;
      const averageMs = valid.reduce((sum, v) => sum + v, 0) / valid.length;
      return Math.ceil(Math.max(0, averageMs - pollingElapsed) / 1000);
    } catch {
      return undefined;
    }
  }, [pollingElapsed, activeQuestionBucket]);

  const changedHexagramInfo = useMemo(() => {
    const detail = result?.detail || '';
    if (!detail) return { number: undefined as number | undefined, name: undefined as string | undefined };

    const match = detail.match(/变卦：第(\d+)卦(?:（([^）]+)）)?/);
    if (!match) return { number: undefined, name: undefined };

    return {
      number: Number(match[1]),
      name: match[2],
    };
  }, [result?.detail]);

  const quickAdvice = useMemo(() => {
    const wuxing = result?.hexagram_info?.wuxing;
    const yi = result?.daily_fortune?.yi;
    const ji = result?.daily_fortune?.ji;
    const rec = result?.recommendations?.[0]?.content;

    return {
      wuxing,
      yi: yi || (rec ? `宜：${rec}` : undefined),
      ji,
    };
  }, [result]);

  const changingLineSummary = useMemo(() => {
    const lines = result?.yarrow_trace?.lines || [];
    const changingLines = lines
      .filter((line) => line.is_changing)
      .map((line) => line.line_index)
      .sort((a, b) => a - b);

    if (!changingLines.length) {
      return {
        text: '无变爻：主看本卦，整体趋势较稳定。',
        level: 'stable' as const,
      };
    }

    if (changingLines.length === 1) {
      return {
        text: `一变爻（第${changingLines[0]}爻）：局部有变，主看该爻提示。`,
        level: 'mild' as const,
      };
    }

    if (changingLines.length === 2) {
      return {
        text: `二变爻（第${changingLines.join('、')}爻）：趋势转折明显，需兼看本卦与变卦。`,
        level: 'medium' as const,
      };
    }

    return {
      text: `${changingLines.length}变爻（第${changingLines.join('、')}爻）：变化较大，建议以变卦为重并结合现实调整。`,
      level: 'strong' as const,
    };
  }, [result?.yarrow_trace?.lines]);

  const polling = useDivinationPolling({
    sessionId,
    onSuccess: (data) => {
      try {
        if (pollingElapsed > 0) {
          const raw = localStorage.getItem(DURATION_HISTORY_KEY);
          const bucketMap = raw ? (JSON.parse(raw) as Record<string, number[]>) : {};
          const currentBucketHistory = Array.isArray(bucketMap[activeQuestionBucket])
            ? bucketMap[activeQuestionBucket].filter((v) => Number.isFinite(v) && v > 0)
            : [];
          const nextBucketHistory = [...currentBucketHistory, pollingElapsed].slice(-DURATION_HISTORY_LIMIT);
          bucketMap[activeQuestionBucket] = nextBucketHistory;
          localStorage.setItem(DURATION_HISTORY_KEY, JSON.stringify(bucketMap));
        }
      } catch {
        // ignore storage failures
      }

      setResult(data);
      setSessionId('');
      setPollingElapsed(0);
      setPollingAttempts(0);

      if (data.yarrow_trace?.lines?.length) {
        setRevealIndex(0);
        setStage('REVEAL');
      } else {
        setStage('RESULT');
      }
    },
    onError: (error) => {
      setStage('QUESTION');
      setSessionId('');
      setPollingElapsed(0);
      setPollingAttempts(0);
      toast.error(error.message || '占卜失败，请重试');
    },
    onProgress: (elapsed, attempts) => {
      setPollingElapsed(elapsed);
      setPollingAttempts(attempts);
    },
    maxAttempts: POLLING_MAX_ATTEMPTS,
    interval: 1000,
  });

  const buildRitualContext = (): RitualContextPayload => ({
    ritual: {
      focus_duration_ms: Math.max(3000, focusDurationMs),
      press_duration_ms: pressDurationMs,
      tap_rhythm: tapRhythm.slice(-6),
      split_counts: splitCounts,
      client_timestamp: Date.now(),
      client_seed: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    },
  });

  const submitDivination = async (context?: RitualContextPayload) => {
    try {
      const startRes = await axiosInstance.post('/divinations/start', {
        user_id: user?.id || 'unknown',
        question,
        version: 'CN',
        orientation: 'E',
        context,
      });

      const sid = startRes.data.session_id;
      if (!sid) throw new Error('未获取到有效的会话ID');
      setSessionId(sid);
    } catch (err: any) {
      setStage('QUESTION');
      if (err.response?.status === 500) toast.error('服务器繁忙，请稍后重试');
      else if (err.response?.status === 401) {
        toast.error('登录已过期，请重新登录');
        setShowLoginModal(true);
      } else {
        toast.error(formatApiErrorMessage(err, '占卜失败，请检查网络连接后重试'));
      }
    }
  };

  const goRitual = () => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
      return;
    }
    if (!question.trim()) {
      toast.warning('请输入您的问题');
      return;
    }
    setFocusDone(false);
    setFocusDurationMs(0);
    setPressDurationMs(0);
    setHoldDone(false);
    setTapRhythm([]);
    setSplitCounts([]);
    setStage('RITUAL');
  };

  const skipRitual = async () => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
      return;
    }
    if (!question.trim()) {
      toast.warning('请输入您的问题');
      return;
    }
    setStage('LOADING');
    await submitDivination({
      ritual: {
        focus_duration_ms: 0,
        press_duration_ms: 0,
        tap_rhythm: [],
        split_counts: [],
        client_timestamp: Date.now(),
        client_seed: `${Date.now()}-skip`,
      },
    });
  };

  const beginFocus = () => {
    focusStartRef.current = Date.now();
    setFocusDone(false);
    window.setTimeout(() => {
      const duration = Date.now() - focusStartRef.current;
      setFocusDurationMs(duration);
      setFocusDone(true);
    }, 3000);
  };

  const holdStart = () => {
    pressStartRef.current = Date.now();
    const now = Date.now();
    if (lastTapRef.current > 0) {
      setTapRhythm((prev) => [...prev, now - lastTapRef.current].slice(-8));
    }
    lastTapRef.current = now;
  };

  const holdEnd = () => {
    if (!pressStartRef.current) return;
    const duration = Date.now() - pressStartRef.current;
    setPressDurationMs(duration);
    if (duration >= 800) setHoldDone(true);
    pressStartRef.current = 0;
  };

  const doSplit = () => {
    if (splitCounts.length >= 3) return;
    const normalized = Math.max(-1, Math.min(1, dragPosition / 120));
    const left = Math.max(16, Math.min(33, Math.round(24.5 + normalized * 8)));
    const right = 49 - left;
    setSplitCounts((prev) => [...prev, { left, right }]);
    setDragPosition(0);
  };

  const startCasting = () => {
    if (!focusDone || !holdDone || splitCounts.length < 3) {
      toast.warning('请先完成静心、触碰与三次分堆');
      return;
    }
    setStage('CASTING');
  };

  useEffect(() => {
    if (stage !== 'CASTING') return;
    const timer = window.setTimeout(async () => {
      setStage('LOADING');
      await submitDivination(buildRitualContext());
    }, 3200);
    return () => clearTimeout(timer);
  }, [stage]);

  useEffect(() => {
    if (stage !== 'REVEAL' || !result?.yarrow_trace?.lines?.length) return;
    if (revealIndex >= result.yarrow_trace.lines.length) {
      const doneTimer = window.setTimeout(() => setStage('RESULT'), 600);
      return () => clearTimeout(doneTimer);
    }
    const timer = window.setTimeout(() => setRevealIndex((prev) => prev + 1), 500);
    return () => clearTimeout(timer);
  }, [stage, revealIndex, result]);

  const resetDivination = () => {
    polling.cancel();
    setStage('QUESTION');
    setQuestion('');
    setResult(null);
    setSessionId('');
    setPollingElapsed(0);
    setPollingAttempts(0);
  };

  const handleCancelLoading = () => {
    polling.cancel();
    setStage('QUESTION');
    setSessionId('');
    setPollingElapsed(0);
    setPollingAttempts(0);
    toast.info('已取消占卜');
  };

  return (
    <AnimatePresence mode="wait">
      {stage === 'QUESTION' && (
        <motion.div key="question" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
          <MobilePage>
            <div className="ritual-header">
              <h2 className="ritual-title">🌿 开始你的占卜之旅</h2>
              <p className="ritual-subtitle">先输入问题，再参与起卦仪式</p>
            </div>

            <div className="ritual-section">
              <Textarea
                label="你的问题"
                placeholder="请输入你想要占卜的问题..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={6}
                maxLength={200}
                showCounter
                required
              />
            </div>

            <div className="ritual-actions">
              <Button variant="primary" size="lg" fullWidth onClick={goRitual} disabled={!question.trim()}>
                进入起卦仪式
              </Button>
              <Button variant="secondary" size="md" fullWidth onClick={skipRitual} disabled={!question.trim()}>
                跳过仪式，快速占卜
              </Button>
            </div>
          </MobilePage>
        </motion.div>
      )}

      {stage === 'RITUAL' && (
        <motion.div key="ritual" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <MobilePage>
            <div className="ritual-header">
              <h2 className="ritual-title">🕯️ 起卦仪式</h2>
              <p className="ritual-subtitle">参与过程，而非决定结果</p>
            </div>

            <Card size="sm"><CardContent>
              <div className="ritual-step-card">
                <h4>步骤 1：静心 3 秒</h4>
                <p>{focusDone ? `已完成（${Math.floor(focusDurationMs / 1000)}秒）` : '请开始静心'}</p>
                <Button variant="secondary" fullWidth onClick={beginFocus} disabled={focusDone}>开始静心</Button>
              </div>
            </CardContent></Card>

            <Card size="sm"><CardContent>
              <div className="ritual-step-card">
                <h4>步骤 2：长按混沌球</h4>
                <motion.button
                  className={`chaos-ball ${holdDone ? 'chaos-ball--done' : ''}`}
                  onMouseDown={holdStart}
                  onMouseUp={holdEnd}
                  onMouseLeave={holdEnd}
                  onTouchStart={holdStart}
                  onTouchEnd={holdEnd}
                  whileTap={{ scale: 0.95 }}
                >
                  {holdDone ? '已感应' : '按住 0.8 秒以上'}
                </motion.button>
                <p>{pressDurationMs > 0 ? `本次长按：${pressDurationMs}ms` : '尚未完成'}</p>
              </div>
            </CardContent></Card>

            <Card size="sm"><CardContent>
              <div className="ritual-step-card">
                <h4>步骤 3：三次分堆（左右拖动）</h4>
                <div className="split-drag-area">
                  <motion.div
                    className="split-drag-knob"
                    drag="x"
                    dragConstraints={{ left: -120, right: 120 }}
                    dragElastic={0.1}
                    onDrag={(_, info) => setDragPosition(info.offset.x)}
                    onDragEnd={(_, info) => setDragPosition(info.offset.x)}
                    animate={{ x: dragPosition }}
                  >
                    分
                  </motion.div>
                </div>
                <p className="split-preview">预估：左 {Math.max(16, Math.min(33, Math.round(24.5 + Math.max(-1, Math.min(1, dragPosition / 120)) * 8)))} / 右 {49 - Math.max(16, Math.min(33, Math.round(24.5 + Math.max(-1, Math.min(1, dragPosition / 120)) * 8)))}</p>
                <Button variant="secondary" fullWidth onClick={doSplit} disabled={splitCounts.length >= 3}>确认本次分堆</Button>
                <div className="split-list">
                  {splitCounts.map((s, idx) => (
                    <p key={`${idx}-${s.left}`}>第{idx + 1}次：左 {s.left} / 右 {s.right}</p>
                  ))}
                </div>
              </div>
            </CardContent></Card>

            <div className="ritual-actions">
              <Button variant="primary" fullWidth onClick={startCasting}>开始起卦</Button>
              <Button variant="secondary" fullWidth onClick={() => setStage('QUESTION')}>返回修改问题</Button>
            </div>
          </MobilePage>
        </motion.div>
      )}

      {stage === 'CASTING' && (
        <motion.div key="casting" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <MobilePage>
            <div className="ritual-header">
              <h2 className="ritual-title">☯️ 六爻生成中</h2>
              <p className="ritual-subtitle">本卦即将显现</p>
            </div>
            <div className="casting-lines">
              {[1, 2, 3, 4, 5, 6].map((line, index) => (
                <motion.div
                  key={line}
                  className="casting-line"
                  initial={{ opacity: 0, scaleX: 0.2 }}
                  animate={{ opacity: 1, scaleX: 1 }}
                  transition={{ delay: index * 0.35, duration: 0.25 }}
                />
              ))}
            </div>
          </MobilePage>
        </motion.div>
      )}

      {stage === 'LOADING' && (
        <DivinationLoading
          onCancel={handleCancelLoading}
          pollingElapsedMs={pollingElapsed}
          pollingAttempts={pollingAttempts}
          pollingMaxAttempts={POLLING_MAX_ATTEMPTS}
          estimatedRemainingSeconds={estimatedRemainingSeconds}
        />
      )}

      {stage === 'REVEAL' && result?.yarrow_trace?.lines && (
        <motion.div key="reveal" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <MobilePage>
            <div className="ritual-header">
              <h2 className="ritual-title">📜 卦象揭示</h2>
              <p className="ritual-subtitle">六爻逐步显现（自下而上）</p>
            </div>

            <Card size="sm">
              <CardContent>
                <div className="hexagram-transition">
                  <div className="hexagram-col">
                    <p className="hexagram-kicker">本卦</p>
                    <p className="hexagram-name">
                      {result.hexagram_info?.number ? `第${result.hexagram_info.number}卦` : '本卦'}
                      {result.hexagram_info?.name ? ` · ${result.hexagram_info.name}` : ''}
                    </p>
                  </div>
                  <div className="hexagram-arrow">→</div>
                  <div className="hexagram-col">
                    <p className="hexagram-kicker">变卦</p>
                    <p className="hexagram-name">
                      {changedHexagramInfo.number ? `第${changedHexagramInfo.number}卦` : '解析中'}
                      {changedHexagramInfo.name ? ` · ${changedHexagramInfo.name}` : ''}
                    </p>
                  </div>
                </div>

                <div className="reveal-quick-advice">
                  {quickAdvice.wuxing && <p>五行：<strong>{quickAdvice.wuxing}</strong></p>}
                  {quickAdvice.yi && <p>{quickAdvice.yi}</p>}
                  {quickAdvice.ji && <p>忌：{quickAdvice.ji}</p>}
                </div>
              </CardContent>
            </Card>

            <Card size="sm">
              <CardContent>
                <p className={`changing-summary changing-summary--${changingLineSummary.level}`}>
                  {changingLineSummary.text}
                </p>
              </CardContent>
            </Card>

            <div className="casting-lines reveal-lines">
              {result.yarrow_trace.lines.map((line, idx) => {
                const visible = idx < revealIndex;
                const isYang = line.line_value === 7 || line.line_value === 9;
                const isChanging = line.is_changing;
                return (
                  <motion.div
                    key={`reveal-${idx}-${line.line_value}`}
                    className={`reveal-line ${visible ? 'reveal-line--visible' : ''} ${isChanging ? 'reveal-line--changing' : ''}`}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: visible ? 1 : 0.15, y: 0 }}
                  >
                    {isYang ? (
                      <div className="line-yang" />
                    ) : (
                      <div className="line-yin-wrap">
                        <div className="line-yin" />
                        <div className="line-yin-gap" />
                        <div className="line-yin" />
                      </div>
                    )}
                    <span className="line-label">第{line.line_index}爻{isChanging ? '（变）' : ''}</span>
                  </motion.div>
                );
              })}
            </div>
          </MobilePage>
        </motion.div>
      )}

      {stage === 'RESULT' && result && (
        <motion.div key="result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <MobilePage>
            <DivinationResultCard result={result} />
            <div className="ritual-actions">
              <Button variant="secondary" fullWidth onClick={resetDivination}>再占一次</Button>
            </div>
          </MobilePage>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

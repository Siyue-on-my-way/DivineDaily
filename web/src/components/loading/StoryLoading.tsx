import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './StoryLoading.css';

interface LoadingStage {
  text: string;
  progress: number;
  duration: number;
}

const LOADING_STAGES: LoadingStage[] = [
  { text: "正在连接宇宙能量...", progress: 20, duration: 2000 },
  { text: "AI 正在解读卦象...", progress: 50, duration: 3000 },
  { text: "整理命运的启示...", progress: 80, duration: 2000 },
  { text: "即将揭晓答案...", progress: 95, duration: 1000 }
];

interface Props {
  type?: 'divination' | 'tarot' | 'fortune';
  onComplete?: () => void;
}

export default function StoryLoading({ type = 'divination', onComplete }: Props) {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; delay: number }>>([]);

  const stage = LOADING_STAGES[currentStage];

  useEffect(() => {
    // 生成粒子
    const newParticles = Array.from({ length: 30 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 2
    }));
    setParticles(newParticles);
  }, []);

  useEffect(() => {
    // 平滑进度条动画
    const targetProgress = stage.progress;
    const startProgress = progress;
    const diff = targetProgress - startProgress;
    const steps = 20;
    const stepDuration = stage.duration / steps;

    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      const newProgress = startProgress + (diff * currentStep) / steps;
      setProgress(newProgress);

      if (currentStep >= steps) {
        clearInterval(interval);
        // 进入下一阶段
        if (currentStage < LOADING_STAGES.length - 1) {
          setTimeout(() => {
            setCurrentStage(currentStage + 1);
          }, 200);
        } else if (onComplete) {
          setTimeout(onComplete, 500);
        }
      }
    }, stepDuration);

    return () => clearInterval(interval);
  }, [currentStage]);

  const getSymbols = () => {
    switch (type) {
      case 'tarot':
        return ['🎴', '✨', '🌙', '⭐'];
      case 'fortune':
        return ['🍀', '💫', '🌟', '✨'];
      default:
        return ['☰', '☱', '☲', '☳', '☴', '☵', '☶', '☷'];
    }
  };

  const symbols = getSymbols();

  return (
    <div className="story-loading">
      <div className="story-loading__background" />

      {/* 粒子效果 */}
      <div className="story-loading__particles">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="story-loading__particle"
            initial={{
              x: `${particle.x}vw`,
              y: `${particle.y}vh`,
              opacity: 0,
              scale: 0
            }}
            animate={{
              x: '50vw',
              y: '50vh',
              opacity: [0, 1, 0],
              scale: [0, 1, 0]
            }}
            transition={{
              duration: 3,
              delay: particle.delay,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          />
        ))}
      </div>

      {/* 中心内容 */}
      <div className="story-loading__content">
        {/* 旋转符号 */}
        <div className="story-loading__symbols">
          {symbols.map((symbol, index) => (
            <motion.div
              key={index}
              className="story-loading__symbol"
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: [0, 1, 1, 0],
                scale: [0, 1, 1, 0],
                rotate: 360
              }}
              transition={{
                duration: 4,
                delay: index * 0.5,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
              style={{
                position: 'absolute',
                left: '50%',
                top: '50%',
                transform: `rotate(${(360 / symbols.length) * index}deg) translateY(-80px)`
              }}
            >
              {symbol}
            </motion.div>
          ))}
        </div>

        {/* 中心图标 */}
        <motion.div
          className="story-loading__center"
          animate={{
            scale: [1, 1.1, 1],
            rotate: [0, 180, 360]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: 'linear'
          }}
        >
          <div className="story-loading__icon">
            {type === 'tarot' ? '🔮' : type === 'fortune' ? '🌿' : '☯'}
          </div>
        </motion.div>

        {/* 进度条 */}
        <div className="story-loading__progress-container">
          <div className="story-loading__progress-bar">
            <motion.div
              className="story-loading__progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            />
          </div>
          <div className="story-loading__progress-text">{Math.round(progress)}%</div>
        </div>

        {/* 动态文案 */}
        <motion.div
          className="story-loading__text"
          key={currentStage}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
        >
          {stage.text}
        </motion.div>

        {/* 脉冲效果 */}
        <div className="story-loading__pulse">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="story-loading__pulse-ring"
              animate={{
                scale: [1, 2, 2],
                opacity: [0.6, 0.3, 0]
              }}
              transition={{
                duration: 2,
                delay: i * 0.6,
                repeat: Infinity,
                ease: 'easeOut'
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

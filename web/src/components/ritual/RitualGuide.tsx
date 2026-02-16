import { useState, useEffect } from 'react';
import { motion, useAnimation } from 'framer-motion';
import './RitualGuide.css';

interface RitualStep {
  title: string;
  description: string;
  duration?: number;
  animation: 'breathing' | 'focus' | 'tap';
}

const RITUAL_STEPS: RitualStep[] = [
  {
    title: "静心",
    description: "请深呼吸三次，让心灵平静下来",
    duration: 9000, // 3次呼吸，每次3秒
    animation: "breathing"
  },
  {
    title: "凝神",
    description: "在心中默念你的问题三遍",
    duration: 5000,
    animation: "focus"
  },
  {
    title: "起卦",
    description: "点击屏幕，让命运为你揭示答案",
    animation: "tap"
  }
];

interface Props {
  onComplete: () => void;
  onSkip?: () => void;
  enableSound?: boolean;
  enableVibration?: boolean;
}

export default function RitualGuide({ 
  onComplete, 
  onSkip,
  enableSound = false,
  enableVibration = true 
}: Props) {
  const [currentStep, setCurrentStep] = useState(0);
  const [breathCount, setBreathCount] = useState(0);
  const [isBreathing, setIsBreathing] = useState<'inhale' | 'exhale' | null>(null);
  const controls = useAnimation();

  const step = RITUAL_STEPS[currentStep];

  useEffect(() => {
    // 检查用户是否选择跳过仪式
    const skipRitual = localStorage.getItem('skip_ritual') === 'true';
    if (skipRitual && onSkip) {
      onSkip();
      return;
    }

    if (step.animation === 'breathing') {
      startBreathingAnimation();
    } else if (step.animation === 'focus') {
      startFocusAnimation();
    }
  }, [currentStep]);

  const startBreathingAnimation = async () => {
    // 3次呼吸循环
    for (let i = 0; i < 3; i++) {
      // 吸气
      setIsBreathing('inhale');
      vibrate([100]);
      await controls.start({
        scale: 1.5,
        opacity: 1,
        background: 'linear-gradient(135deg, #10B981 0%, #F59E0B 100%)',
        transition: { duration: 3, ease: 'easeInOut' }
      });

      // 呼气
      setIsBreathing('exhale');
      vibrate([100]);
      await controls.start({
        scale: 1,
        opacity: 0.8,
        background: 'linear-gradient(135deg, #059669 0%, #10B981 100%)',
        transition: { duration: 3, ease: 'easeInOut' }
      });

      setBreathCount(i + 1);
    }

    // 完成后自动进入下一步
    setTimeout(() => nextStep(), 500);
  };

  const startFocusAnimation = async () => {
    // 聚焦动画：多个圆圈从外向内收缩
    await controls.start({
      scale: [1, 0.8, 1],
      opacity: [0.5, 1, 0.5],
      transition: { 
        duration: 5, 
        repeat: 0,
        ease: 'easeInOut'
      }
    });

    // 完成后等待用户点击
    setTimeout(() => nextStep(), 500);
  };

  const vibrate = (pattern: number[]) => {
    if (enableVibration && 'vibrate' in navigator) {
      navigator.vibrate(pattern);
    }
  };

  const playSound = (type: 'bell' | 'chime') => {
    if (enableSound) {
      // 这里可以集成音频播放
      // const audio = new Audio(`/sounds/${type}.mp3`);
      // audio.play();
    }
  };

  const nextStep = () => {
    if (currentStep < RITUAL_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
      vibrate([50]);
    }
  };

  const handleTap = () => {
    if (step.animation === 'tap') {
      vibrate([100, 50, 100]);
      playSound('chime');
      onComplete();
    }
  };

  const handleSkipForever = () => {
    localStorage.setItem('skip_ritual', 'true');
    if (onSkip) {
      onSkip();
    }
  };

  return (
    <div className="ritual-guide">
      <div className="ritual-guide__overlay" />
      
      <div className="ritual-guide__content">
        {/* 步骤指示器 */}
        <div className="ritual-guide__steps">
          {RITUAL_STEPS.map((_, index) => (
            <div
              key={index}
              className={`ritual-guide__step-dot ${
                index === currentStep ? 'active' : ''
              } ${index < currentStep ? 'completed' : ''}`}
            />
          ))}
        </div>

        {/* 动画区域 */}
        <div className="ritual-guide__animation">
          {step.animation === 'breathing' && (
            <div className="ritual-guide__breathing">
              <motion.div
                className="ritual-guide__circle"
                animate={controls}
                initial={{ scale: 1, opacity: 0.8 }}
              />
              <div className="ritual-guide__breath-text">
                {isBreathing === 'inhale' ? '吸气...' : '呼气...'}
              </div>
              <div className="ritual-guide__breath-count">
                {breathCount}/3
              </div>
            </div>
          )}

          {step.animation === 'focus' && (
            <div className="ritual-guide__focus">
              <motion.div
                className="ritual-guide__focus-circle ritual-guide__focus-circle--outer"
                animate={controls}
              />
              <motion.div
                className="ritual-guide__focus-circle ritual-guide__focus-circle--middle"
                animate={controls}
                transition={{ delay: 0.2 }}
              />
              <motion.div
                className="ritual-guide__focus-circle ritual-guide__focus-circle--inner"
                animate={controls}
                transition={{ delay: 0.4 }}
              />
              <div className="ritual-guide__focus-icon">🧘</div>
            </div>
          )}

          {step.animation === 'tap' && (
            <motion.div
              className="ritual-guide__tap"
              onClick={handleTap}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              animate={{
                boxShadow: [
                  '0 0 20px rgba(16, 185, 129, 0.4)',
                  '0 0 40px rgba(16, 185, 129, 0.6)',
                  '0 0 20px rgba(16, 185, 129, 0.4)'
                ]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
            >
              <div className="ritual-guide__tap-icon">🔮</div>
              <div className="ritual-guide__tap-text">点击开始</div>
            </motion.div>
          )}
        </div>

        {/* 文字说明 */}
        <motion.div
          className="ritual-guide__text"
          key={currentStep}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="ritual-guide__title">{step.title}</h2>
          <p className="ritual-guide__description">{step.description}</p>
        </motion.div>

        {/* 跳过按钮 */}
        <div className="ritual-guide__actions">
          <button
            className="ritual-guide__skip"
            onClick={() => onSkip && onSkip()}
          >
            跳过
          </button>
          <button
            className="ritual-guide__skip-forever"
            onClick={handleSkipForever}
          >
            不再显示
          </button>
        </div>
      </div>
    </div>
  );
}

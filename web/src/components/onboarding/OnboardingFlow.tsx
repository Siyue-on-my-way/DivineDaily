import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './OnboardingFlow.css';

interface Props {
  onComplete: () => void;
}

const SLIDES = [
  {
    id: 1,
    icon: '🌿',
    title: '欢迎来到 DivineDaily',
    description: '每日一卦，洞察人生',
    features: []
  },
  {
    id: 2,
    icon: '🔮',
    title: '三种占卜方式',
    description: '选择最适合你的占卜方法',
    features: [
      { icon: '☯', text: '周易六爻 - 古老智慧指引' },
      { icon: '🎴', text: '塔罗占卜 - 探索未知答案' },
      { icon: '⭐', text: '每日运势 - 把握当下机遇' }
    ]
  },
  {
    id: 3,
    icon: '✨',
    title: '开始你的第一次占卜',
    description: '诚心发问，静待答案',
    features: []
  }
];

export default function OnboardingFlow({ onComplete }: Props) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [direction, setDirection] = useState(0);

  const slide = SLIDES[currentSlide];

  const handleNext = () => {
    if (currentSlide < SLIDES.length - 1) {
      setDirection(1);
      setCurrentSlide(currentSlide + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrev = () => {
    if (currentSlide > 0) {
      setDirection(-1);
      setCurrentSlide(currentSlide - 1);
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    localStorage.setItem('onboarding_completed', 'true');
    onComplete();
  };

  const goToSlide = (index: number) => {
    setDirection(index > currentSlide ? 1 : -1);
    setCurrentSlide(index);
  };

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      x: 0,
      opacity: 1
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 1000 : -1000,
      opacity: 0
    })
  };

  return (
    <div className="onboarding-flow">
      <button className="onboarding-flow__skip" onClick={handleSkip}>
        跳过
      </button>

      <div className="onboarding-flow__container">
        <div className="onboarding-flow__swiper">
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div
              key={slide.id}
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{
                x: { type: 'spring', stiffness: 300, damping: 30 },
                opacity: { duration: 0.2 }
              }}
              className="onboarding-flow__slide"
            >
              {/* 动画图标 */}
              <div className="onboarding-flow__animation">
                <div className="onboarding-flow__circle onboarding-flow__circle--1" />
                <div className="onboarding-flow__circle onboarding-flow__circle--2" />
                <div className="onboarding-flow__circle onboarding-flow__circle--3" />
                <div className="onboarding-flow__icon">{slide.icon}</div>
              </div>

              {/* 文字内容 */}
              <div className="onboarding-flow__content">
                <h2 className="onboarding-flow__title">{slide.title}</h2>
                <p className="onboarding-flow__description">{slide.description}</p>
              </div>

              {/* 功能列表 */}
              {slide.features.length > 0 && (
                <div className="onboarding-flow__features">
                  {slide.features.map((feature, index) => (
                    <motion.div
                      key={index}
                      className="onboarding-flow__feature"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 + 0.3 }}
                    >
                      <div className="onboarding-flow__feature-icon">{feature.icon}</div>
                      <div className="onboarding-flow__feature-text">{feature.text}</div>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* 底部控制 */}
        <div className="onboarding-flow__controls">
          {/* 指示点 */}
          <div className="onboarding-flow__dots">
            {SLIDES.map((_, index) => (
              <div
                key={index}
                className={`onboarding-flow__dot ${
                  index === currentSlide ? 'onboarding-flow__dot--active' : ''
                }`}
                onClick={() => goToSlide(index)}
              />
            ))}
          </div>

          {/* 按钮 */}
          <div className="onboarding-flow__buttons">
            {currentSlide > 0 && (
              <button
                className="onboarding-flow__button onboarding-flow__button--secondary"
                onClick={handlePrev}
              >
                上一步
              </button>
            )}
            <button
              className="onboarding-flow__button onboarding-flow__button--primary"
              onClick={handleNext}
              style={{ flex: currentSlide === 0 ? 1 : undefined }}
            >
              {currentSlide === SLIDES.length - 1 ? '立即体验' : '下一步'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

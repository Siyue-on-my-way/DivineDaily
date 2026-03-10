import React, { useState, useEffect } from 'react';
import './DivinationLoading.css';

interface LoadingStage {
  duration: number;
  message: string;
  icon: string;
}

const stages: LoadingStage[] = [
  { duration: 3000, message: '正在起卦...', icon: '🎲' },
  { duration: 8000, message: 'AI大师正在解读卦象...', icon: '🔮' },
  { duration: 15000, message: '正在生成详细建议...', icon: '✨' },
  { duration: 60000, message: '即将完成...', icon: '🎯' }
];

interface DivinationLoadingProps {
  onCancel?: () => void;
}

export const DivinationLoading: React.FC<DivinationLoadingProps> = ({ onCancel }) => {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    const startTime = Date.now();
    
    // 更新阶段
    const stageInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      setElapsedTime(elapsed);
      
      // 根据时间确定当前阶段
      let stage = 0;
      for (let i = 0; i < stages.length; i++) {
        if (elapsed < stages[i].duration) {
          stage = i;
          break;
        }
      }
      setCurrentStage(stage);
    }, 100);

    // 更新进度条
    const progressInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const newProgress = getProgress(elapsed);
      setProgress(newProgress);
    }, 100);

    return () => {
      clearInterval(stageInterval);
      clearInterval(progressInterval);
    };
  }, []);

  // 根据时间计算进度
  const getProgress = (elapsed: number): number => {
    if (elapsed < 3000) return (elapsed / 3000) * 20;      // 0-20%
    if (elapsed < 8000) return 20 + ((elapsed - 3000) / 5000) * 50;  // 20-70%
    if (elapsed < 15000) return 70 + ((elapsed - 8000) / 7000) * 20; // 70-90%
    return Math.min(95, 90 + ((elapsed - 15000) / 10000) * 5);       // 90-95%
  };

  const formatTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    return `${seconds}秒`;
  };

  const stage = stages[currentStage];

  return (
    <div className="divination-loading-overlay">
      <div className="divination-loading-container">
        {/* 太极图动画 */}
        <div className="taiji-container">
          <div className="taiji-symbol">
            <svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
              {/* 外圆边框 */}
              <circle 
                cx="60" 
                cy="60" 
                r="58" 
                fill="none" 
                stroke="#FFD700" 
                strokeWidth="2"
              />
              
              {/* 白色阴鱼（左半部分 + 上半小圆） */}
              <path 
                d="M60,2 A58,58 0 0,1 60,118 A29,29 0 0,1 60,60 A29,29 0 0,0 60,2 Z" 
                fill="#FFFFFF"
              />
              
              {/* 黑色阳鱼（右半部分 + 下半小圆） */}
              <path 
                d="M60,2 A58,58 0 0,0 60,118 A29,29 0 0,0 60,60 A29,29 0 0,1 60,2 Z" 
                fill="#000000"
              />
              
              {/* 白鱼中的黑眼 */}
              <circle 
                cx="60" 
                cy="31" 
                r="8" 
                fill="#000000"
              />
              
              {/* 黑鱼中的白眼 */}
              <circle 
                cx="60" 
                cy="89" 
                r="8" 
                fill="#FFFFFF"
              />
            </svg>
          </div>
        </div>

        {/* 阶段提示 */}
        <div className="loading-stage">
          <span className="stage-icon">{stage.icon}</span>
          <h3 className="stage-message">{stage.message}</h3>
        </div>

        {/* 进度条 */}
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="progress-text">{Math.floor(progress)}%</div>
        </div>

        {/* 时间提示 */}
        <div className="time-info">
          <p className="time-elapsed">已用时: {formatTime(elapsedTime)}</p>
          <p className="time-hint">预计还需 {Math.max(0, 15 - Math.floor(elapsedTime / 1000))} 秒</p>
        </div>

        {/* 提示文字 */}
        <div className="loading-tips">
          <p>💡 AI正在结合易经智慧为您分析</p>
          <p>🌟 好的建议值得等待</p>
        </div>

        {/* 取消按钮 */}
        {onCancel && (
          <button className="cancel-button" onClick={onCancel}>
            取消占卜
          </button>
        )}
      </div>
    </div>
  );
};

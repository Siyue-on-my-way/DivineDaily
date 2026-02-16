import { motion } from 'framer-motion';
import './TarotDrawAnimation.css';

interface TarotCard {
  id: string;
  name: string;
  position?: string;
  is_reversed?: boolean;
}

interface Props {
  spread: 'single' | 'three' | 'cross';
  cards: TarotCard[];
  onComplete?: () => void;
}

export default function TarotDrawAnimation({ spread, cards, onComplete }: Props) {
  const totalCards = spread === 'single' ? 1 : spread === 'three' ? 3 : 10;
  const deckSize = 78;

  // 生成牌堆
  const deckCards = Array.from({ length: deckSize }, (_, i) => ({
    id: `deck-${i}`,
    x: Math.random() * 300 - 150,
    y: Math.random() * 300 - 150,
    rotation: Math.random() * 360
  }));

  return (
    <div className="tarot-draw-animation">
      {/* 阶段1: 洗牌 */}
      <div className="tarot-draw-animation__stage">
        <div className="tarot-draw-animation__shuffle">
          {deckCards.slice(0, 20).map((card, i) => (
            <motion.div
              key={card.id}
              className="tarot-draw-animation__deck-card"
              initial={{ 
                x: 0, 
                y: 0, 
                rotate: 0,
                scale: 1
              }}
              animate={{
                x: [0, card.x, card.x, 0],
                y: [0, card.y, card.y, 0],
                rotate: [0, card.rotation, card.rotation, 0],
                scale: [1, 0.8, 0.8, 1]
              }}
              transition={{
                duration: 2,
                times: [0, 0.3, 0.7, 1],
                repeat: 2,
                delay: i * 0.05,
                ease: 'easeInOut'
              }}
            >
              🎴
            </motion.div>
          ))}
        </div>

        <motion.div
          className="tarot-draw-animation__text"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 1, 0] }}
          transition={{ duration: 6, times: [0, 0.1, 0.9, 1] }}
        >
          正在洗牌...
        </motion.div>
      </div>

      {/* 阶段2: 抽牌 */}
      <div className="tarot-draw-animation__stage">
        {cards.map((card, i) => (
          <motion.div
            key={card.id}
            className="tarot-draw-animation__selected-card"
            initial={{ 
              x: 0,
              y: 0,
              scale: 0,
              rotateY: 180,
              opacity: 0
            }}
            animate={{
              x: getCardPosition(i, totalCards).x,
              y: getCardPosition(i, totalCards).y,
              scale: 1,
              rotateY: 180,
              opacity: 1
            }}
            transition={{
              delay: 6 + i * 0.5,
              duration: 0.8,
              type: 'spring',
              stiffness: 200,
              damping: 20
            }}
          >
            <div className="tarot-draw-animation__card-back">
              <div className="tarot-draw-animation__card-pattern">✨</div>
            </div>
          </motion.div>
        ))}

        <motion.div
          className="tarot-draw-animation__text"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 1, 0] }}
          transition={{ 
            duration: totalCards * 0.5 + 1,
            delay: 6,
            times: [0, 0.1, 0.9, 1]
          }}
        >
          正在抽取塔罗牌...
        </motion.div>
      </div>

      {/* 阶段3: 翻牌 */}
      <div className="tarot-draw-animation__stage">
        {cards.map((card, i) => (
          <motion.div
            key={`flip-${card.id}`}
            className="tarot-draw-animation__flip-card"
            style={{
              position: 'absolute',
              left: `calc(50% + ${getCardPosition(i, totalCards).x}px)`,
              top: `calc(50% + ${getCardPosition(i, totalCards).y}px)`,
              transform: 'translate(-50%, -50%)'
            }}
            initial={{ rotateY: 180 }}
            animate={{ rotateY: card.is_reversed ? 180 : 0 }}
            transition={{
              delay: 6 + totalCards * 0.5 + i * 0.3,
              duration: 0.6,
              ease: 'easeInOut'
            }}
            onAnimationComplete={() => {
              if (i === cards.length - 1 && onComplete) {
                setTimeout(onComplete, 500);
              }
            }}
          >
            <div className="tarot-draw-animation__card-front">
              <div className="tarot-draw-animation__card-name">{card.name}</div>
              {card.position && (
                <div className="tarot-draw-animation__card-position">
                  {card.position}
                </div>
              )}
            </div>
          </motion.div>
        ))}

        <motion.div
          className="tarot-draw-animation__text"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 1] }}
          transition={{ 
            delay: 6 + totalCards * 0.5,
            duration: 1
          }}
        >
          揭示命运的答案...
        </motion.div>
      </div>
    </div>
  );
}

// 计算卡片位置
function getCardPosition(index: number, total: number): { x: number; y: number } {
  if (total === 1) {
    return { x: 0, y: 0 };
  }

  if (total === 3) {
    // 三张牌横向排列
    return {
      x: (index - 1) * 140,
      y: 0
    };
  }

  if (total === 10) {
    // 十字牌阵
    const positions = [
      { x: 0, y: 0 },      // 中心
      { x: 0, y: -120 },   // 上
      { x: 120, y: 0 },    // 右
      { x: 0, y: 120 },    // 下
      { x: -120, y: 0 },   // 左
      { x: 0, y: -240 },   // 最上
      { x: 240, y: 0 },    // 最右
      { x: 0, y: 240 },    // 最下
      { x: -240, y: 0 },   // 最左
      { x: 0, y: -360 }    // 顶部
    ];
    return positions[index] || { x: 0, y: 0 };
  }

  return { x: 0, y: 0 };
}

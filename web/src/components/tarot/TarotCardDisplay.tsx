import { useState, useEffect } from 'react'
import type { TarotCardDraw } from '../../types/divination'
import TarotCardInfo from './TarotCardInfo'
// import './TarotCardDisplay.css' // Removed

interface TarotCardDisplayProps {
  cards: TarotCardDraw[]
  spread: string
}

export default function TarotCardDisplay({ cards, spread }: TarotCardDisplayProps) {
  const [flippedCards, setFlippedCards] = useState<Set<number>>(new Set())
  const [revealedCards, setRevealedCards] = useState<Set<number>>(new Set())
  const [isAnimating, setIsAnimating] = useState(true)

  if (!cards || cards.length === 0) {
    return null
  }

  // 抽牌动画：依次显示牌面
  useEffect(() => {
    if (cards.length === 0) return
    
    setIsAnimating(true)
    setRevealedCards(new Set())
    const revealOrder: number[] = []
    const timeouts: ReturnType<typeof setTimeout>[] = []
    
    if (spread === 'single') {
      revealOrder.push(0)
    } else if (spread === 'three') {
      revealOrder.push(0, 1, 2)
    } else if (spread === 'cross') {
      revealOrder.push(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    }
    
    revealOrder.forEach((idx, order) => {
      const timeout = setTimeout(() => {
        setRevealedCards((prev) => {
          const newSet = new Set(prev)
          newSet.add(idx)
          return newSet
        })
        if (order === revealOrder.length - 1) {
          const finalTimeout = setTimeout(() => setIsAnimating(false), 300)
          timeouts.push(finalTimeout)
        }
      }, order * 300 + 200)
      timeouts.push(timeout)
    })
    
    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout))
    }
  }, [cards, spread])

  const handleCardClick = (index: number) => {
    setFlippedCards((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  // Helper for Card Rendering
  const Card = ({ 
    card, 
    index, 
    className = "", 
    style = {} 
  }: { 
    card: TarotCardDraw, 
    index: number, 
    className?: string,
    style?: React.CSSProperties
  }) => {
    const isFlipped = flippedCards.has(index)
    const isRevealed = revealedCards.has(index)
    
    return (
      <div 
        className={`relative w-[100px] h-[150px] md:w-[120px] md:h-[180px] perspective-[1000px] cursor-pointer transition-all duration-500 ease-out ${className} ${!isRevealed ? 'opacity-0 translate-y-4 scale-90' : 'opacity-100 translate-y-0 scale-100'}`}
        onClick={() => handleCardClick(index)}
        style={{ 
          ...style,
          transitionDelay: `${index * 100}ms`
        }}
      >
        <div className={`relative w-full h-full transition-transform duration-700 transform-style-3d ${isFlipped ? 'rotate-y-180' : ''}`}>
          {/* Back */}
          <div className="absolute inset-0 backface-hidden rounded-xl bg-gradient-to-br from-[var(--color-nebula-purple)] to-indigo-900 border border-[var(--glass-border)] flex items-center justify-center text-4xl shadow-xl">
            <span className="opacity-50">🃏</span>
          </div>
          
          {/* Front */}
          <div className="absolute inset-0 backface-hidden rounded-xl bg-[#fdfbf7] border-2 border-[var(--color-ethereal-gold)] rotate-y-180 flex flex-col items-center justify-between p-2 shadow-xl overflow-hidden">
            <div className="text-[10px] text-[var(--color-starlight-dim)] uppercase tracking-widest text-center w-full border-b border-[var(--color-ethereal-gold)]/20 pb-1">
              {card.position}
            </div>
            
            <div className="flex-1 flex flex-col items-center justify-center text-center">
              <div className="text-sm font-serif font-bold text-gray-800 leading-tight px-1">
                {card.name}
              </div>
              {card.is_reversed && (
                <span className="text-[10px] text-red-500 font-bold mt-1 border border-red-200 px-1 rounded">
                  逆位
                </span>
              )}
            </div>
            
            <div className="w-full h-1 bg-[var(--color-ethereal-gold)]/20 rounded-full mt-1"></div>
          </div>
        </div>
      </div>
    )
  }

  const renderSingleCard = () => {
    if (cards.length === 0) return null
    return (
      <div className="flex justify-center mb-8">
        <Card card={cards[0]} index={0} />
      </div>
    )
  }

  const renderThreeCards = () => {
    if (cards.length < 3) return null
    return (
      <div className="flex justify-center gap-4 flex-wrap mb-8">
        {cards.slice(0, 3).map((card, idx) => (
          <Card key={idx} card={card} index={idx} />
        ))}
      </div>
    )
  }

  const renderCrossSpread = () => {
    if (cards.length < 10) return null
    // Positions mapping
    const posMap = [
      'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20', // Center
      'top-0 left-1/2 -translate-x-1/2', // Top
      'bottom-0 left-1/2 -translate-x-1/2', // Bottom
      'top-1/2 left-0 -translate-y-1/2', // Left
      'top-1/2 right-0 -translate-y-1/2', // Right
      'top-[10%] left-[10%]', // TopLeft
      'top-[10%] right-[10%]', // TopRight
      'bottom-[10%] left-[10%]', // BottomLeft
      'bottom-[10%] right-[10%]', // BottomRight
      'bottom-[-190px] left-1/2 -translate-x-1/2', // Future (below)
    ]

    return (
      <div className="relative w-full max-w-[500px] mx-auto aspect-square min-h-[400px] mb-24">
        {cards.slice(0, 10).map((card, idx) => (
          <Card 
            key={idx} 
            card={card} 
            index={idx} 
            className={`absolute ${posMap[idx]}`} 
          />
        ))}
      </div>
    )
  }

  const renderCards = () => {
    switch (spread) {
      case 'single': return renderSingleCard()
      case 'three': return renderThreeCards()
      case 'cross': return renderCrossSpread()
      default: return renderSingleCard()
    }
  }

  return (
    <div className="my-6">
      <div className="text-center mb-8">
        <h4 className="text-lg font-serif font-bold text-[var(--color-ethereal-gold)]">
          {spread === 'single' && '单张牌'}
          {spread === 'three' && '三张牌阵（过去/现在/未来）'}
          {spread === 'cross' && '十字牌阵'}
        </h4>
      </div>

      {isAnimating && (
        <div className="flex items-center justify-center gap-2 mb-8 p-4 rounded-lg bg-[var(--glass-bg)] border border-[var(--glass-border)]">
          <span className="text-sm text-[var(--color-starlight-dim)] animate-pulse">正在抽牌...</span>
          <div className="flex gap-1">
            <span className="w-1.5 h-1.5 bg-[var(--color-nebula-purple)] rounded-full animate-bounce [animation-delay:-0.3s]"></span>
            <span className="w-1.5 h-1.5 bg-[var(--color-nebula-purple)] rounded-full animate-bounce [animation-delay:-0.15s]"></span>
            <span className="w-1.5 h-1.5 bg-[var(--color-nebula-purple)] rounded-full animate-bounce"></span>
          </div>
        </div>
      )}

      {renderCards()}

      {!isAnimating && (
        <div className="bg-[var(--glass-bg)] rounded-xl overflow-hidden border border-[var(--glass-border)]">
          <div className="p-3 text-center border-b border-[var(--glass-border)] bg-black/20">
            <span className="text-xs text-[var(--color-starlight-dim)]">💡 点击牌面翻转查看 | 点击下方列表查看详情</span>
          </div>
          <div className="divide-y divide-[var(--glass-border)]">
            {cards.map((card, idx) => (
              <TarotCardInfo key={idx} card={card} index={idx} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

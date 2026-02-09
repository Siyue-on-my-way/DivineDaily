import { useState } from 'react'
import type { TarotCardDraw } from '../../types/divination'
// import './TarotCardInfo.css' // Removed

interface TarotCardInfoProps {
  card: TarotCardDraw
  index: number
}

export default function TarotCardInfo({ card, index }: TarotCardInfoProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const isReversed = card.is_reversed
  const cardNameWithoutReversed = card.name

  return (
    <div className="border-b border-[var(--glass-border)] last:border-0">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-[rgba(255,255,255,0.05)] transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[var(--color-nebula-purple)] text-white text-xs font-bold shadow-[0_0_8px_var(--color-nebula-purple-glow)]">
            {index + 1}
          </span>
          <span className="font-medium text-[var(--color-starlight)] flex items-center gap-2">
            {cardNameWithoutReversed}
            {isReversed && (
              <span className="text-red-400 text-xs font-bold border border-red-400/30 px-1 rounded" title="逆位">逆</span>
            )}
          </span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-ethereal-gold-glow)]/20 text-[var(--color-ethereal-gold)] border border-[var(--color-ethereal-gold)]/20">
            {card.position}
          </span>
        </div>
        <span className="text-[var(--color-starlight-dim)] text-xs transition-transform duration-300" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
          ▼
        </span>
      </div>
      
      {isExpanded && (
        <div className="px-4 pb-4 pl-12 space-y-3 animate-[slideDown_0.3s_ease]">
          <div className="p-4 rounded-lg bg-black/20 border border-[var(--glass-border)] space-y-3">
            <h4 className="text-sm font-serif font-bold text-[var(--color-ethereal-gold)] border-b border-[var(--glass-border)] pb-2">
              牌面信息
            </h4>
            
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex flex-col">
                <span className="text-[var(--color-starlight-dim)] text-xs">位置</span>
                <span className="text-[var(--color-starlight)]">{card.position}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[var(--color-starlight-dim)] text-xs">牌名</span>
                <span className="text-[var(--color-starlight)]">{cardNameWithoutReversed}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[var(--color-starlight-dim)] text-xs">状态</span>
                <span className={`${isReversed ? 'text-red-400' : 'text-green-400'}`}>
                  {isReversed ? '逆位' : '正位'}
                </span>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <h4 className="text-sm font-serif font-bold text-[var(--color-ethereal-gold)] border-b border-[var(--glass-border)] pb-2">
                位置含义
              </h4>
              <p className="text-sm text-[var(--color-starlight-dim)] leading-relaxed">
                {card.position === '过去' && '这张牌代表您过去的情况和经历，影响您当前的状态。'}
                {card.position === '现在' && '这张牌代表您当前的情况和状态，是问题的核心所在。'}
                {card.position === '未来' && '这张牌代表未来可能的发展趋势和结果。'}
                {card.position === '中心' && '这张牌是问题的核心，代表当前最重要的因素。'}
                {!['过去', '现在', '未来', '中心'].includes(card.position) && 
                  `这张牌在${card.position}位置，代表相关的方面和影响因素。`}
              </p>
              {isReversed && (
                <div className="mt-2 p-2 rounded bg-red-900/10 border border-red-500/20">
                  <strong className="text-red-400 text-xs block mb-1">逆位提示</strong>
                  <p className="text-xs text-[var(--color-starlight-dim)]">
                    逆位通常表示该能量的阻碍、延迟或需要反思的方面。需要特别注意这个位置的指引。
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

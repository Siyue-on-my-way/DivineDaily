import type { HexagramInfo } from '../../types/divination';
// import './HexagramDisplay.css'; // Removed

interface Props {
  hexagram: HexagramInfo;
}

// 八卦符号映射
const trigramSymbols: Record<string, string> = {
  乾: '☰',
  坤: '☷',
  震: '☳',
  巽: '☴',
  坎: '☵',
  离: '☲',
  艮: '☶',
  兑: '☱',
};

export default function HexagramDisplay({ hexagram }: Props) {
  const upperSymbol = trigramSymbols[hexagram.upper_trigram] || hexagram.upper_trigram;
  const lowerSymbol = trigramSymbols[hexagram.lower_trigram] || hexagram.lower_trigram;

  const getOutcomeColor = (outcome: string) => {
    if (outcome.includes('吉')) return 'text-green-400 bg-green-400/10 border-green-400/20';
    if (outcome.includes('凶')) return 'text-red-400 bg-red-400/10 border-red-400/20';
    return 'text-[var(--color-starlight-dim)] bg-[var(--glass-bg)] border-[var(--glass-border)]';
  };

  return (
    <div className="p-6 rounded-xl bg-[var(--glass-bg)] border border-[var(--glass-border)]">
      
      <div className="text-center mb-8">
        <div className="mb-4 space-x-2">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-mono text-[var(--color-nebula-purple)] bg-[var(--color-nebula-purple-glow)] border border-[var(--color-nebula-purple)]/30">
            第{hexagram.number}卦
          </span>
          <span className="text-3xl font-serif font-bold text-[var(--color-ethereal-gold)] tracking-wide">
            {hexagram.name}
          </span>
        </div>
        
        <div className="flex flex-col items-center gap-6 my-6">
          <div className="flex flex-col gap-2">
            <div className="flex flex-col items-center gap-1 order-2">
              <div className="text-xs text-[var(--color-starlight-dim)] uppercase tracking-wider">上卦 · {hexagram.upper_trigram}</div>
              <div className="text-5xl leading-none text-[var(--color-starlight)] font-light opacity-90">{upperSymbol}</div>
            </div>
            
            <div className="flex flex-col items-center gap-1 order-1">
              <div className="text-xs text-[var(--color-starlight-dim)] uppercase tracking-wider">下卦 · {hexagram.lower_trigram}</div>
              <div className="text-5xl leading-none text-[var(--color-starlight)] font-light opacity-90">{lowerSymbol}</div>
            </div>
          </div>
        </div>
        
        {hexagram.changing_lines && hexagram.changing_lines.length > 0 && (
          <div className="inline-block px-4 py-2 rounded-lg bg-[var(--color-ethereal-gold-glow)]/30 border border-[var(--color-ethereal-gold)]/30 text-[var(--color-ethereal-gold)] text-sm">
            变爻：第{hexagram.changing_lines.map(l => l + 1).join('、')}爻
          </div>
        )}
      </div>

      <div className="space-y-3 pt-4 border-t border-[var(--glass-border)]">
        <div className="flex items-baseline gap-3">
          <span className="w-12 text-sm font-medium text-[var(--color-starlight-dim)] text-right flex-shrink-0">吉凶</span>
          <span className={`px-2 py-0.5 rounded text-sm font-medium border ${getOutcomeColor(hexagram.outcome)}`}>
            {hexagram.outcome}
          </span>
        </div>
        
        {hexagram.wuxing && (
          <div className="flex items-baseline gap-3">
            <span className="w-12 text-sm font-medium text-[var(--color-starlight-dim)] text-right flex-shrink-0">五行</span>
            <span className="text-[var(--color-starlight)]">{hexagram.wuxing}</span>
          </div>
        )}
        
        {hexagram.summary && (
          <div className="flex items-baseline gap-3">
            <span className="w-12 text-sm font-medium text-[var(--color-starlight-dim)] text-right flex-shrink-0">卦辞</span>
            <span className="text-[var(--color-starlight)] leading-relaxed">{hexagram.summary}</span>
          </div>
        )}
      </div>
    </div>
  );
}

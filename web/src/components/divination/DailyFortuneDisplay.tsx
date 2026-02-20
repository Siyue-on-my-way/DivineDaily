import type { DailyFortuneInfo } from '../../types/divination';
// import './DailyFortuneDisplay.css'; // Removed

interface Props {
  info: DailyFortuneInfo;
}

export default function DailyFortuneDisplay({ info }: Props) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-6 rounded-xl bg-gradient-to-br from-[var(--color-nebula-purple)]/20 to-[var(--color-ethereal-gold)]/10 border border-[var(--glass-border)]">
        <div className="flex flex-col items-center md:items-start">
          <div className="text-4xl font-serif font-bold text-[var(--color-ethereal-gold)] drop-shadow-[0_0_10px_rgba(251,191,36,0.5)]">
            {info.score}
          </div>
          <div className="text-xs text-[var(--color-starlight-dim)] uppercase tracking-wider mt-1">运势评分</div>
        </div>
        
        <div className="flex flex-wrap justify-center gap-3">
          <div className="px-4 py-2 rounded-lg bg-[var(--glass-bg)] border border-[var(--glass-border)] text-[var(--color-starlight)] font-mono">
            {new Date(info.date).toLocaleDateString()}
          </div>
          {info.solar_term && (
            <div className="px-3 py-2 rounded-lg bg-[var(--color-ethereal-gold-glow)]/20 border border-[var(--color-ethereal-gold)]/30 text-[var(--color-ethereal-gold)]">
              {info.solar_term}
            </div>
          )}
          {info.festival && (
            <div className="px-3 py-2 rounded-lg bg-[var(--color-nebula-purple-glow)]/20 border border-[var(--color-nebula-purple)]/30 text-[var(--color-nebula-purple)]">
              {info.festival}
            </div>
          )}
        </div>
      </div>

      {/* Lucky Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '幸运色', value: info.lucky_color, color: 'text-pink-400' },
          { label: '幸运数字', value: info.lucky_number, color: 'text-blue-400' },
          { label: '幸运方位', value: info.lucky_direction, color: 'text-purple-400' },
          { label: '吉时', value: info.lucky_time, color: 'text-amber-400' },
        ].map((item, idx) => (
          <div key={idx} className="flex flex-col items-center justify-center p-4 rounded-xl bg-[var(--glass-bg)] border border-[var(--glass-border)]">
            <span className="text-xs text-[var(--color-starlight-dim)] mb-1">{item.label}</span>
            <span className={`text-lg font-bold ${item.color}`}>{item.value}</span>
          </div>
        ))}
      </div>

      {/* Yi / Ji Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-green-900/10 border border-green-500/20">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 font-serif font-bold">
              宜
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {info.yi.map((item, idx) => (
              <span key={idx} className="px-2 py-1 rounded bg-green-500/10 text-green-300 text-sm border border-green-500/20">
                {item}
              </span>
            ))}
          </div>
        </div>
        
        <div className="p-5 rounded-xl bg-red-900/10 border border-red-500/20">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-400 font-serif font-bold">
              忌
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {info.ji.map((item, idx) => (
              <span key={idx} className="px-2 py-1 rounded bg-red-500/10 text-red-300 text-sm border border-red-500/20">
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Advice Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { title: '财运', content: info.wealth, icon: '💰', color: 'border-yellow-500/20 bg-yellow-900/5' },
          { title: '事业', content: info.career, icon: '💼', color: 'border-blue-500/20 bg-blue-900/5' },
          { title: '感情', content: info.love, icon: '❤️', color: 'border-pink-500/20 bg-pink-900/5' },
          { title: '健康', content: info.health, icon: '🧘', color: 'border-green-500/20 bg-green-900/5' },
        ].map((item, idx) => (
          <div key={idx} className={`p-4 rounded-xl border ${item.color} transition-all duration-300 hover:bg-opacity-20`}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium text-[var(--color-starlight)]">{item.title}</span>
            </div>
            <p className="text-sm text-[var(--color-starlight-dim)] leading-relaxed">
              {item.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* 桌面端响应式适配已内置 */

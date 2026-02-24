import type { DailyFortuneInfo } from '../../types/divination';

interface Props {
  info: DailyFortuneInfo;
}

export default function DailyFortuneDisplay({ info }: Props) {
  // 将逗号分隔的字符串转换为数组
  const yiList = info.yi ? info.yi.split(',').filter(item => item.trim()) : [];
  const jiList = info.ji ? info.ji.split(',').filter(item => item.trim()) : [];
  
  // 从 content 中提取各部分内容
  const parseContent = (content: string) => {
    const sections = {
      summary: '',
      wealth: '',
      career: '',
      love: '',
      health: ''
    };
    
    // 简单解析：按照【】标记分割
    const lines = content.split('\n');
    let currentSection = 'summary';
    
    for (const line of lines) {
      if (line.includes('【财运')) {
        currentSection = 'wealth';
      } else if (line.includes('【事业')) {
        currentSection = 'career';
      } else if (line.includes('【感情')) {
        currentSection = 'love';
      } else if (line.includes('【健康')) {
        currentSection = 'health';
      } else if (line.trim() && !line.includes('【')) {
        sections[currentSection as keyof typeof sections] += line + ' ';
      }
    }
    
    return sections;
  };
  
  const sections = parseContent(info.content);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-6 rounded-xl bg-gradient-to-br from-[var(--color-nebula-purple)]/20 to-[var(--color-ethereal-gold)]/10 border border-[var(--glass-border)]">
        <div className="flex flex-col items-center md:items-start">
          <div className="text-4xl font-serif font-bold text-[var(--color-ethereal-gold)] drop-shadow-[0_0_10px_rgba(251,191,36,0.5)]">
            {info.overall_score}
          </div>
          <div className="text-xs text-[var(--color-starlight-dim)] uppercase tracking-wider mt-1">综合运势</div>
        </div>
        
        <div className="flex flex-wrap justify-center gap-3">
          <div className="px-4 py-2 rounded-lg bg-[var(--glass-bg)] border border-[var(--glass-border)] text-[var(--color-starlight)] font-mono">
            {new Date().toLocaleDateString()}
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

      {/* Score Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '财运', value: info.wealth_score, color: 'text-yellow-400' },
          { label: '事业', value: info.career_score, color: 'text-blue-400' },
          { label: '感情', value: info.love_score, color: 'text-pink-400' },
          { label: '健康', value: info.health_score, color: 'text-green-400' },
        ].map((item, idx) => (
          <div key={idx} className="flex flex-col items-center justify-center p-4 rounded-xl bg-[var(--glass-bg)] border border-[var(--glass-border)]">
            <span className="text-xs text-[var(--color-starlight-dim)] mb-1">{item.label}</span>
            <span className={`text-2xl font-bold ${item.color}`}>{item.value}</span>
          </div>
        ))}
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
            {yiList.length > 0 ? yiList.map((item, idx) => (
              <span key={idx} className="px-2 py-1 rounded bg-green-500/10 text-green-300 text-sm border border-green-500/20">
                {item}
              </span>
            )) : (
              <span className="text-green-300/50 text-sm">暂无</span>
            )}
          </div>
        </div>
        
        <div className="p-5 rounded-xl bg-red-900/10 border border-red-500/20">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-400 font-serif font-bold">
              忌
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {jiList.length > 0 ? jiList.map((item, idx) => (
              <span key={idx} className="px-2 py-1 rounded bg-red-500/10 text-red-300 text-sm border border-red-500/20">
                {item}
              </span>
            )) : (
              <span className="text-red-300/50 text-sm">暂无</span>
            )}
          </div>
        </div>
      </div>

      {/* Advice Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { title: '财运', content: sections.wealth, icon: '💰', score: info.wealth_score, color: 'border-yellow-500/20 bg-yellow-900/5' },
          { title: '事业', content: sections.career, icon: '💼', score: info.career_score, color: 'border-blue-500/20 bg-blue-900/5' },
          { title: '感情', content: sections.love, icon: '❤️', score: info.love_score, color: 'border-pink-500/20 bg-pink-900/5' },
          { title: '健康', content: sections.health, icon: '🧘', score: info.health_score, color: 'border-green-500/20 bg-green-900/5' },
        ].map((item, idx) => (
          <div key={idx} className={`p-4 rounded-xl border ${item.color} transition-all duration-300 hover:bg-opacity-20`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium text-[var(--color-starlight)]">{item.title}</span>
              </div>
              <span className="text-sm font-bold text-[var(--color-ethereal-gold)]">{item.score}分</span>
            </div>
            <p className="text-sm text-[var(--color-starlight-dim)] leading-relaxed">
              {item.content || '运势平稳，保持积极心态。'}
            </p>
          </div>
        ))}
      </div>

      {/* Summary Section */}
      {sections.summary && (
        <div className="p-5 rounded-xl bg-[var(--glass-bg)] border border-[var(--glass-border)]">
          <h3 className="text-lg font-medium text-[var(--color-starlight)] mb-3">今日运势概述</h3>
          <p className="text-[var(--color-starlight-dim)] leading-relaxed">
            {sections.summary}
          </p>
        </div>
      )}
    </div>
  );
}

/* 桌面端响应式适配已内置 */

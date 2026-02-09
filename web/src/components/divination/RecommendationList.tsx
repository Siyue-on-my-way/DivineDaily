import type { RecommendationItem } from '../../types/divination';
// import './RecommendationList.css'; // Removed

interface Props {
  recommendations: RecommendationItem[];
}

export default function RecommendationList({ recommendations }: Props) {
  return (
    <div className="space-y-4">
      {recommendations.map((rec, index) => (
        <div 
          key={index} 
          className="flex gap-4 p-4 rounded-xl bg-[var(--glass-bg)] border border-[var(--glass-border)] hover:bg-[rgba(255,255,255,0.05)] transition-colors duration-300"
        >
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-[var(--color-nebula-purple)] text-white font-bold text-sm flex-shrink-0 shadow-[0_0_10px_var(--color-nebula-purple-glow)]">
            {index + 1}
          </div>
          <div className="flex-1 space-y-2">
            <div className="text-[var(--color-starlight)] text-base font-medium">
              <strong className="text-[var(--color-nebula-purple)] mr-2">推荐：</strong>
              {rec.content}
            </div>
            {rec.reason && (
              <div className="text-sm text-[var(--color-starlight-dim)] leading-relaxed bg-black/20 p-3 rounded-lg">
                <strong className="text-[var(--color-starlight-dim)] opacity-70 block mb-1 text-xs uppercase tracking-wide">理由</strong>
                {rec.reason}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

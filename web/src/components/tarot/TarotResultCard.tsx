import { useState } from 'react';
import { Card, CardContent } from '../mobile/Card';
import { Button } from '../mobile/Button';
import TarotCardDisplay from './TarotCardDisplay';
import type { DivinationResult } from '../../types/divination';

interface TarotResultCardProps {
  result: DivinationResult;
}

export default function TarotResultCard({ result }: TarotResultCardProps) {
  const [showDetail, setShowDetail] = useState(false);

  return (
    <div className="space-y-4">
      {/* 标题卡片 */}
      <Card variant="gradient">
        <CardContent>
          <div className="text-center py-4">
            <h2 className="text-2xl font-bold mb-2">🔮 塔罗解读</h2>
            {result.title && (
              <p className="text-lg opacity-90">{result.title}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 塔罗牌展示 */}
      {result.cards && result.cards.length > 0 && (
        <Card variant="elevated">
          <CardContent>
            <TarotCardDisplay 
              cards={result.cards} 
              spread={result.spread || 'single'} 
            />
          </CardContent>
        </Card>
      )}

      {/* 简要解读 */}
      <Card variant="primary">
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">✨</span>
              <h3 className="text-lg font-bold">牌面解读</h3>
            </div>
            <p className="text-base leading-relaxed whitespace-pre-wrap">
              {result.summary}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 详细解读（可展开） */}
      {result.detail && (
        <Card variant="elevated">
          <CardContent>
            <div className="space-y-3">
              <Button
                variant="text"
                fullWidth
                onClick={() => setShowDetail(!showDetail)}
                icon={
                  <span style={{ 
                    display: 'inline-block',
                    transform: showDetail ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.3s'
                  }}>
                    ▼
                  </span>
                }
              >
                {showDetail ? '收起详细解读' : '查看详细解读'}
              </Button>

              {showDetail && (
                <div className="pt-3 border-t border-white/10">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">📖</span>
                      <h4 className="font-bold">详细分析</h4>
                    </div>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap opacity-90">
                      {result.detail}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 场景建议 */}
      {result.scene_advice && result.scene_advice.length > 0 && (
        <Card variant="elevated">
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-xl">💡</span>
                <h3 className="font-bold">建议指引</h3>
              </div>
              <div className="space-y-2">
                {result.scene_advice.map((advice, index) => (
                  <div 
                    key={index}
                    className="p-3 rounded-lg bg-white/5 border border-white/10"
                  >
                    <h4 className="font-semibold text-sm mb-1">{advice.title}</h4>
                    <p className="text-sm opacity-80">{advice.content}</p>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 时间戳 */}
      <div className="text-center text-xs opacity-50">
        占卜时间：{new Date(result.created_at).toLocaleString('zh-CN')}
      </div>
    </div>
  );
}

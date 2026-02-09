import { useParams, useNavigate } from 'react-router-dom';
import { MobilePage } from '../components/mobile';
import { Button } from '../components/mobile/Button';
import DivinationResultCard from '../components/divination/DivinationResultCard';
import type { DivinationResult } from '../types/divination';

export default function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // TODO: 从 API 获取真实数据
  const mockResult: DivinationResult = {
    session_id: id || '1',
    outcome: '吉',
    title: '转介绍会成功吗？',
    summary: '根据卦象显示，此事有较大成功可能...',
    detail: '详细解读内容...',
    needs_follow_up: false,
    created_at: new Date().toISOString(),
  };

  return (
    <MobilePage>
      <div style={{ padding: 'var(--spacing-md)' }}>
        <Button 
          variant="text" 
          size="sm" 
          onClick={() => navigate('/history')}
          icon={
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          }
        >
          返回历史
        </Button>
        
        <DivinationResultCard result={mockResult} />
      </div>
    </MobilePage>
  );
}

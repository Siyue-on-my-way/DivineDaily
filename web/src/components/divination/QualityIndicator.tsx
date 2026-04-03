import './QualityIndicator.css';

interface QualityIndicatorProps {
  score: number;
  breakdown: {
    specificity: number;
    personalRelevance: number;
    decisionValue: number;
    temporalRelevance: number;
  };
  suggestions: Array<{
    type: string;
    message: string;
    priority: string;
  }>;
  loading?: boolean;
}

/**
 * 问题质量指示器组件
 * 
 * 显示问题质量评分和详细的改进建议，帮助用户提出更好的问题
 * 
 * @param score - 总体质量评分 (0-100)
 * @param breakdown - 各维度评分详情
 * @param suggestions - 改进建议列表
 * @param loading - 是否正在评估中
 */
export function QualityIndicator({
  score,
  breakdown,
  suggestions,
  loading = false
}: QualityIndicatorProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return '优秀';
    if (score >= 60) return '良好';
    if (score >= 40) return '一般';
    return '需改进';
  };

  const getScoreDescription = (score: number) => {
    if (score >= 80) return '问题表述清晰，占卜结果会更准确';
    if (score >= 60) return '问题质量不错，可以进一步优化';
    if (score >= 40) return '问题较为模糊，建议补充更多细节';
    return '问题过于简单，强烈建议改进后再占卜';
  };

  // 维度说明
  const dimensionHelp: Record<string, string> = {
    specificity: '问题是否具体明确，包含足够的细节和背景信息',
    personalRelevance: '问题是否与个人情况相关，使用第一人称表述',
    decisionValue: '问题是否有助于做出决策，而非简单的是非判断',
    temporalRelevance: '问题是否包含时间信息，如"近期"、"今年"等'
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '💡';
    }
  };

  if (loading) {
    return (
      <div className="quality-indicator loading">
        <div className="loading-spinner"></div>
        <span>正在评估问题质量...</span>
      </div>
    );
  }

  return (
    <div className="quality-indicator">
      {/* 总分显示 */}
      <div className="quality-score" style={{ color: getScoreColor(score) }}>
        <div className="score-value">{score}</div>
        <div className="score-label">{getScoreLabel(score)}</div>
      </div>
      
      {/* 评分说明 */}
      <div className="quality-description">
        {getScoreDescription(score)}
      </div>

      {/* 详细评分 */}
      <div className="quality-breakdown">
        <div className="breakdown-item" title={dimensionHelp.specificity}>
          <span className="breakdown-label">具体性</span>
          <div className="breakdown-bar">
            <div
              className="breakdown-fill"
              style={{ 
                width: `${breakdown.specificity}%`,
                backgroundColor: getScoreColor(breakdown.specificity)
              }}
            />
          </div>
          <span className="breakdown-value">{breakdown.specificity}</span>
        </div>
        <div className="breakdown-item" title={dimensionHelp.personalRelevance}>
          <span className="breakdown-label">相关性</span>
          <div className="breakdown-bar">
            <div
              className="breakdown-fill"
              style={{ 
                width: `${breakdown.personalRelevance}%`,
                backgroundColor: getScoreColor(breakdown.personalRelevance)
              }}
            />
          </div>
          <span className="breakdown-value">{breakdown.personalRelevance}</span>
        </div>
        <div className="breakdown-item" title={dimensionHelp.decisionValue}>
          <span className="breakdown-label">决策价值</span>
          <div className="breakdown-bar">
            <div
              className="breakdown-fill"
              style={{ 
                width: `${breakdown.decisionValue}%`,
                backgroundColor: getScoreColor(breakdown.decisionValue)
              }}
            />
          </div>
          <span className="breakdown-value">{breakdown.decisionValue}</span>
        </div>
        <div className="breakdown-item" title={dimensionHelp.temporalRelevance}>
          <span className="breakdown-label">时效性</span>
          <div className="breakdown-bar">
            <div
              className="breakdown-fill"
              style={{ 
                width: `${breakdown.temporalRelevance}%`,
                backgroundColor: getScoreColor(breakdown.temporalRelevance)
              }}
            />
          </div>
          <span className="breakdown-value">{breakdown.temporalRelevance}</span>
        </div>
      </div>

      {/* 改进建议 */}
      {suggestions.length > 0 && (
        <div className="quality-suggestions">
          <div className="suggestions-title">💡 如何改进你的问题</div>
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              className={`suggestion-item priority-${suggestion.priority}`}
            >
              <span className="suggestion-icon">{getPriorityIcon(suggestion.priority)}</span>
              <span className="suggestion-text">{suggestion.message}</span>
            </div>
          ))}
          
          {/* 示例提示 */}
          {score < 60 && (
            <div className="quality-example-tip">
              <strong>示例：</strong>将"好不好"改为"我最近在考虑跳槽到新公司，这个决定对我的职业发展是否有利？"
            </div>
          )}
        </div>
      )}
    </div>
  );
}

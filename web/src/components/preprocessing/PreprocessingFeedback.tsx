import React from 'react';
import type { PreprocessResponse } from '../../types/preprocessing';
import './PreprocessingFeedback.css';

interface PreprocessingFeedbackProps {
  result: PreprocessResponse;
  onAccept: () => void;
  onReject: () => void;
}

const PreprocessingFeedback: React.FC<PreprocessingFeedbackProps> = ({ result, onAccept, onReject }) => {
  return (
    <div className="preprocessing-feedback">
      <div className="quality-score">
        <span>问题质量评分: {(result.quality_score * 10).toFixed(1)}/10.0</span>
        <div className="quality-bar">
          <div 
            className="quality-fill" 
            style={{ width: `${result.quality_score * 100}%` }}
          />
        </div>
      </div>
      
      {result.suggestions.length > 0 && (
        <div className="suggestions">
          <h4>优化建议:</h4>
          {result.suggestions.map((suggestion, index) => (
            <div key={index} className="suggestion-item">
              <span className="suggestion-type">{suggestion.type}</span>
              <span className="suggestion-message">{suggestion.message}</span>
            </div>
          ))}
        </div>
      )}
      
      {result.use_enhanced && (
        <div className="enhancement-comparison">
          <div className="original-question">
            <h4>原问题:</h4>
            <p>{result.original_question}</p>
          </div>
          <div className="enhanced-question">
            <h4>优化后:</h4>
            <p>{result.enhanced_question}</p>
          </div>
        </div>
      )}
      
      <div className="action-buttons">
        {result.use_enhanced ? (
          <>
            <button onClick={onAccept} className="accept-btn">
              使用优化后的问题
            </button>
            <button onClick={onReject} className="reject-btn">
              坚持使用原问题
            </button>
          </>
        ) : (
          <button onClick={onAccept} className="continue-btn">
            继续占卜
          </button>
        )}
      </div>
    </div>
  );
};

export default PreprocessingFeedback;

import { motion } from 'framer-motion';
import { RecommendationService } from '../../services/recommendation';
import type { DivinationResult } from '../../types/divination';
import './SmartRecommendations.css';

interface Props {
  history: DivinationResult[];
  onSelectQuestion: (question: string) => void;
}

export default function SmartRecommendations({ history, onSelectQuestion }: Props) {
  const recommendations = RecommendationService.analyzeHistory(history);

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="smart-recommendations">
      <h3 className="smart-recommendations__title">
        <span>💡</span>
        为你推荐
      </h3>

      <div className="smart-recommendations__list">
        {recommendations.map((rec, index) => (
          <motion.div
            key={rec.id}
            className="recommendation-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => onSelectQuestion(rec.question)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div
              className={`recommendation-card__category recommendation-card__category--${rec.category}`}
            >
              {rec.category}
            </div>

            <div className="recommendation-card__header">
              <div className="recommendation-card__icon">{rec.icon}</div>
              <div className="recommendation-card__content">
                <h4 className="recommendation-card__question">{rec.question}</h4>
                <p className="recommendation-card__reason">
                  <span className="recommendation-card__reason-icon">✨</span>
                  {rec.reason}
                </p>
              </div>
            </div>

            <div className="recommendation-card__action">
              <button className="recommendation-card__button">
                一键占卜
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

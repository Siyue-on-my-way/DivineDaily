import type { DivinationResult } from '../types/divination';

interface RecommendationItem {
  id: string;
  question: string;
  category: 'career' | 'love' | 'wealth' | 'health';
  icon: string;
  reason: string;
}

export class RecommendationService {
  private static readonly QUESTION_TEMPLATES = {
    career: [
      '这次工作机会适合我吗？',
      '我应该跳槽吗？',
      '项目能顺利完成吗？',
      '升职的机会大吗？'
    ],
    love: [
      '我和TA的关系会如何发展？',
      '今天适合表白吗？',
      '这段感情有未来吗？',
      '如何改善我们的关系？'
    ],
    wealth: [
      '这笔投资值得吗？',
      '最近财运如何？',
      '能谈成这笔生意吗？',
      '如何提升财运？'
    ],
    health: [
      '最近需要注意健康吗？',
      '这个养生方法适合我吗？',
      '如何改善睡眠质量？',
      '运动计划能坚持吗？'
    ]
  };

  /**
   * 分析用户历史占卜，生成个性化推荐
   */
  static analyzeHistory(history: DivinationResult[]): RecommendationItem[] {
    if (history.length === 0) {
      return this.getDefaultRecommendations();
    }

    // 分析最近10次占卜
    const recentHistory = history.slice(0, 10);
    const categories = this.extractCategories(recentHistory);
    const daysSinceLastDivination = this.getDaysSinceLastDivination(history[0]);

    const recommendations: RecommendationItem[] = [];

    // 如果距离上次占卜超过7天，推荐"好久不见"
    if (daysSinceLastDivination > 7) {
      recommendations.push({
        id: 'comeback',
        question: '好久不见，最近运势如何？',
        category: 'health',
        icon: '🌟',
        reason: `距离上次占卜已经${daysSinceLastDivination}天了`
      });
    }

    // 根据高频主题推荐
    const topCategory = this.getTopCategory(categories);
    if (topCategory) {
      const template = this.getRandomTemplate(topCategory);
      recommendations.push({
        id: `category-${topCategory}`,
        question: template,
        category: topCategory,
        icon: this.getCategoryIcon(topCategory),
        reason: `你最近经常关注${this.getCategoryName(topCategory)}问题`
      });
    }

    // 节气/节日推荐
    const seasonalRecommendation = this.getSeasonalRecommendation();
    if (seasonalRecommendation) {
      recommendations.push(seasonalRecommendation);
    }

    // 补充其他类别的推荐
    const otherCategories = (['career', 'love', 'wealth', 'health'] as const).filter(
      cat => cat !== topCategory
    );
    
    otherCategories.slice(0, 2).forEach(category => {
      const template = this.getRandomTemplate(category);
      recommendations.push({
        id: `other-${category}`,
        question: template,
        category,
        icon: this.getCategoryIcon(category),
        reason: '也许你也想了解一下'
      });
    });

    return recommendations.slice(0, 4);
  }

  /**
   * 提取问题类别
   */
  private static extractCategories(history: DivinationResult[]): Record<string, number> {
    const categories: Record<string, number> = {
      career: 0,
      love: 0,
      wealth: 0,
      health: 0
    };

    history.forEach(item => {
      const question = (item.title || '').toLowerCase();
      
      if (question.includes('工作') || question.includes('事业') || question.includes('职') || question.includes('升')) {
        categories.career++;
      }
      if (question.includes('感情') || question.includes('爱') || question.includes('恋') || question.includes('表白')) {
        categories.love++;
      }
      if (question.includes('财') || question.includes('钱') || question.includes('投资') || question.includes('生意')) {
        categories.wealth++;
      }
      if (question.includes('健康') || question.includes('身体') || question.includes('运动') || question.includes('睡眠')) {
        categories.health++;
      }
    });

    return categories;
  }

  /**
   * 获取最高频类别
   */
  private static getTopCategory(categories: Record<string, number>): 'career' | 'love' | 'wealth' | 'health' | null {
    const entries = Object.entries(categories);
    if (entries.every(([_, count]) => count === 0)) return null;

    const sorted = entries.sort((a, b) => b[1] - a[1]);
    return sorted[0][0] as 'career' | 'love' | 'wealth' | 'health';
  }

  /**
   * 计算距离上次占卜的天数
   */
  private static getDaysSinceLastDivination(lastDivination: DivinationResult): number {
    const lastDate = new Date(lastDivination.created_at);
    const now = new Date();
    const diff = now.getTime() - lastDate.getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  }

  /**
   * 获取随机问题模板
   */
  private static getRandomTemplate(category: 'career' | 'love' | 'wealth' | 'health'): string {
    const templates = this.QUESTION_TEMPLATES[category];
    return templates[Math.floor(Math.random() * templates.length)];
  }

  /**
   * 获取类别图标
   */
  private static getCategoryIcon(category: string): string {
    const icons: Record<string, string> = {
      career: '💼',
      love: '❤️',
      wealth: '💰',
      health: '🧘'
    };
    return icons[category] || '🔮';
  }

  /**
   * 获取类别名称
   */
  private static getCategoryName(category: string): string {
    const names: Record<string, string> = {
      career: '事业',
      love: '感情',
      wealth: '财运',
      health: '健康'
    };
    return names[category] || '占卜';
  }

  /**
   * 获取节气/节日推荐
   */
  private static getSeasonalRecommendation(): RecommendationItem | null {
    const now = new Date();
    const month = now.getMonth() + 1;
    const day = now.getDate();

    // 春节前后
    if ((month === 1 && day > 20) || (month === 2 && day < 15)) {
      return {
        id: 'spring-festival',
        question: '新年运势如何？',
        category: 'health',
        icon: '🧧',
        reason: '新春佳节，了解一下新年运势'
      };
    }

    // 情人节
    if (month === 2 && day === 14) {
      return {
        id: 'valentines',
        question: '今天表白会成功吗？',
        category: 'love',
        icon: '💝',
        reason: '情人节特别推荐'
      };
    }

    // 中秋节
    if (month === 9 && day > 10 && day < 20) {
      return {
        id: 'mid-autumn',
        question: '中秋团圆，家人关系如何？',
        category: 'love',
        icon: '🥮',
        reason: '中秋佳节，关心家人'
      };
    }

    return null;
  }

  /**
   * 获取默认推荐（新用户）
   */
  private static getDefaultRecommendations(): RecommendationItem[] {
    return [
      {
        id: 'first-divination',
        question: '今天运势如何？',
        category: 'health',
        icon: '🌟',
        reason: '开始你的第一次占卜'
      },
      {
        id: 'career-start',
        question: '最近工作顺利吗？',
        category: 'career',
        icon: '💼',
        reason: '了解事业运势'
      },
      {
        id: 'love-start',
        question: '感情方面有什么建议？',
        category: 'love',
        icon: '❤️',
        reason: '探索感情走向'
      },
      {
        id: 'wealth-start',
        question: '财运如何提升？',
        category: 'wealth',
        icon: '💰',
        reason: '把握财富机会'
      }
    ];
  }
}

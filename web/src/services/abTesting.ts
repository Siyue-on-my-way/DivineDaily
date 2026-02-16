/**
 * A/B 测试框架
 */

interface Variant {
  id: string;
  name: string;
  weight: number;
}

interface Experiment {
  id: string;
  name: string;
  variants: Variant[];
  enabled: boolean;
}

interface ExperimentAssignment {
  experimentId: string;
  variantId: string;
  timestamp: number;
}

export class ABTestingService {
  private static readonly STORAGE_KEY = 'ab_experiments';
  private experiments: Map<string, Experiment> = new Map();
  private assignments: Map<string, ExperimentAssignment> = new Map();

  constructor() {
    this.loadAssignments();
  }

  /**
   * 注册实验
   */
  registerExperiment(experiment: Experiment) {
    this.experiments.set(experiment.id, experiment);
  }

  /**
   * 获取用户的变体
   */
  getVariant(experimentId: string, userId?: string): string | null {
    const experiment = this.experiments.get(experimentId);
    
    if (!experiment || !experiment.enabled) {
      return null;
    }

    // 检查是否已有分配
    const existing = this.assignments.get(experimentId);
    if (existing) {
      return existing.variantId;
    }

    // 分配新变体
    const variantId = this.assignVariant(experiment, userId);
    
    // 保存分配
    this.assignments.set(experimentId, {
      experimentId,
      variantId,
      timestamp: Date.now()
    });
    
    this.saveAssignments();
    
    return variantId;
  }

  /**
   * 分配变体（基于权重）
   */
  private assignVariant(experiment: Experiment, userId?: string): string {
    const { variants } = experiment;
    
    // 计算总权重
    const totalWeight = variants.reduce((sum, v) => sum + v.weight, 0);
    
    // 生成随机数（如果有 userId，使用确定性哈希）
    let random: number;
    if (userId) {
      random = this.hashUserId(userId) % totalWeight;
    } else {
      random = Math.random() * totalWeight;
    }

    // 选择变体
    let cumulative = 0;
    for (const variant of variants) {
      cumulative += variant.weight;
      if (random < cumulative) {
        return variant.id;
      }
    }

    // 降级返回第一个变体
    return variants[0].id;
  }

  /**
   * 用户 ID 哈希（简单实现）
   */
  private hashUserId(userId: string): number {
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {
      const char = userId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash);
  }

  /**
   * 追踪事件
   */
  track(experimentId: string, eventName: string, properties?: Record<string, any>) {
    const assignment = this.assignments.get(experimentId);
    
    if (!assignment) {
      return;
    }

    const event = {
      experimentId,
      variantId: assignment.variantId,
      eventName,
      properties,
      timestamp: Date.now()
    };

    console.log('[A/B Testing] Event:', event);
    
    // 这里可以上报到分析服务
    // analytics.track('ab_test_event', event);
  }

  /**
   * 加载分配记录
   */
  private loadAssignments() {
    try {
      const stored = localStorage.getItem(ABTestingService.STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        this.assignments = new Map(Object.entries(data));
      }
    } catch (error) {
      console.error('[A/B Testing] Failed to load assignments:', error);
    }
  }

  /**
   * 保存分配记录
   */
  private saveAssignments() {
    try {
      const data = Object.fromEntries(this.assignments);
      localStorage.setItem(ABTestingService.STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('[A/B Testing] Failed to save assignments:', error);
    }
  }

  /**
   * 清除所有分配
   */
  clearAssignments() {
    this.assignments.clear();
    localStorage.removeItem(ABTestingService.STORAGE_KEY);
  }

  /**
   * 强制分配变体（用于测试）
   */
  forceVariant(experimentId: string, variantId: string) {
    this.assignments.set(experimentId, {
      experimentId,
      variantId,
      timestamp: Date.now()
    });
    this.saveAssignments();
  }
}

// 创建全局实例
export const abTesting = new ABTestingService();

// 注册实验示例
abTesting.registerExperiment({
  id: 'homepage_hero_design',
  name: '首页 Hero 区域设计',
  enabled: true,
  variants: [
    { id: 'control', name: '原始版本', weight: 50 },
    { id: 'variant_a', name: '大号评分', weight: 50 }
  ]
});

abTesting.registerExperiment({
  id: 'result_display_format',
  name: '结果展示格式',
  enabled: true,
  variants: [
    { id: 'control', name: '标准格式', weight: 50 },
    { id: 'variant_a', name: '交互式格式', weight: 50 }
  ]
});

abTesting.registerExperiment({
  id: 'onboarding_flow',
  name: '引导流程',
  enabled: true,
  variants: [
    { id: 'control', name: '无引导', weight: 30 },
    { id: 'variant_a', name: '3步引导', weight: 40 },
    { id: 'variant_b', name: '5步引导', weight: 30 }
  ]
});

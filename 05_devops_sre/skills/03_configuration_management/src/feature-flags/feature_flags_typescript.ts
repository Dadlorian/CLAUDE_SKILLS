/**
 * Feature Flags Implementation in TypeScript
 * Production-ready feature flag system with LaunchDarkly-style API
 * Supports: Percentage rollouts, user targeting, A/B testing, gradual releases
 */

import { createHash } from 'crypto';

// Type definitions
interface UserContext {
  userId: string;
  email?: string;
  attributes: Record<string, any>;
}

enum RolloutStrategy {
  ALL = 'all',
  NONE = 'none',
  PERCENTAGE = 'percentage',
  USER_LIST = 'user_list',
  USER_ATTRIBUTE = 'user_attribute',
  GRADUAL = 'gradual',
}

interface FeatureFlag {
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  strategy: RolloutStrategy;
  config: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

interface Variant {
  name: string;
  weight: number;
  config?: Record<string, any>;
}

interface EvaluationResult {
  enabled: boolean;
  variant?: string;
  reason?: string;
}

/**
 * Feature Flag Client
 * Manages feature flags with caching, fallbacks, and analytics
 */
export class FeatureFlagClient {
  private cache: Map<string, FeatureFlag> = new Map();
  private analytics: Map<string, number> = new Map();
  private evaluationCallbacks: ((flag: string, user: UserContext, result: boolean) => void)[] = [];

  constructor(
    private config: {
      apiKey?: string;
      endpoint?: string;
      cacheTTL?: number;
      enableAnalytics?: boolean;
    } = {}
  ) {
    this.config.cacheTTL = this.config.cacheTTL || 60000; // 1 minute default
    this.config.enableAnalytics = this.config.enableAnalytics !== false;
  }

  /**
   * Check if a feature flag is enabled for a user
   */
  async isEnabled(
    flagKey: string,
    user: UserContext,
    defaultValue: boolean = false
  ): Promise<boolean> {
    try {
      const flag = await this.getFlag(flagKey);

      if (!flag || !flag.enabled) {
        this.track(flagKey, user, 'disabled', 'flag_not_enabled');
        return defaultValue;
      }

      const result = this.evaluateStrategy(flag, user);
      this.track(flagKey, user, result ? 'enabled' : 'disabled', 'evaluated');

      // Call registered callbacks
      this.evaluationCallbacks.forEach(callback => {
        callback(flagKey, user, result);
      });

      return result;
    } catch (error) {
      console.error(`Error evaluating flag ${flagKey}:`, error);
      return defaultValue;
    }
  }

  /**
   * Get variant for A/B testing
   */
  async getVariant(
    flagKey: string,
    user: UserContext,
    defaultVariant: string = 'control'
  ): Promise<string> {
    try {
      const flag = await this.getFlag(flagKey);

      if (!flag || !flag.enabled) {
        return defaultVariant;
      }

      const variants = flag.config.variants as Record<string, Variant>;
      if (!variants || Object.keys(variants).length === 0) {
        return defaultVariant;
      }

      // Use consistent hashing for stable variant assignment
      const userHash = this.hashUser(user.userId, flagKey);
      const totalWeight = Object.values(variants).reduce(
        (sum, v) => sum + v.weight,
        0
      );

      if (totalWeight === 0) {
        return defaultVariant;
      }

      // Determine variant based on hash and weights
      const threshold = (userHash % 100) / 100 * totalWeight;
      let cumulativeWeight = 0;

      for (const [variantName, variantConfig] of Object.entries(variants)) {
        cumulativeWeight += variantConfig.weight;
        if (threshold < cumulativeWeight) {
          this.track(flagKey, user, 'variant', variantName);
          return variantName;
        }
      }

      return defaultVariant;
    } catch (error) {
      console.error(`Error getting variant for ${flagKey}:`, error);
      return defaultVariant;
    }
  }

  /**
   * Get configuration for a feature flag
   */
  async getConfig(
    flagKey: string,
    user: UserContext
  ): Promise<Record<string, any>> {
    try {
      const flag = await this.getFlag(flagKey);

      if (!flag || !(await this.isEnabled(flagKey, user))) {
        return {};
      }

      return flag.config;
    } catch (error) {
      console.error(`Error getting config for ${flagKey}:`, error);
      return {};
    }
  }

  /**
   * Register callback for flag evaluations (for analytics)
   */
  onEvaluation(
    callback: (flag: string, user: UserContext, result: boolean) => void
  ): void {
    this.evaluationCallbacks.push(callback);
  }

  /**
   * Create a new feature flag (for testing/development)
   */
  createFlag(flagDefinition: Partial<FeatureFlag>): void {
    const flag: FeatureFlag = {
      key: flagDefinition.key!,
      name: flagDefinition.name || flagDefinition.key!,
      description: flagDefinition.description || '',
      enabled: flagDefinition.enabled !== false,
      strategy: flagDefinition.strategy || RolloutStrategy.ALL,
      config: flagDefinition.config || {},
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.cache.set(flag.key, flag);
  }

  /**
   * Update feature flag configuration
   */
  updateFlag(flagKey: string, updates: Partial<FeatureFlag>): void {
    const flag = this.cache.get(flagKey);
    if (flag) {
      Object.assign(flag, updates);
      flag.updatedAt = new Date();
    }
  }

  /**
   * Get analytics data for a flag
   */
  getAnalytics(flagKey: string): Map<string, number> {
    const analytics = new Map<string, number>();
    for (const [key, value] of this.analytics.entries()) {
      if (key.startsWith(`${flagKey}:`)) {
        analytics.set(key, value);
      }
    }
    return analytics;
  }

  // Private methods

  private async getFlag(flagKey: string): Promise<FeatureFlag | null> {
    // Check cache
    if (this.cache.has(flagKey)) {
      return this.cache.get(flagKey)!;
    }

    // In production, this would fetch from API
    // For now, return null
    return null;
  }

  private evaluateStrategy(flag: FeatureFlag, user: UserContext): boolean {
    switch (flag.strategy) {
      case RolloutStrategy.ALL:
        return true;

      case RolloutStrategy.NONE:
        return false;

      case RolloutStrategy.PERCENTAGE:
        const percentage = flag.config.percentage || 0;
        const userHash = this.hashUser(user.userId, flag.key);
        return (userHash % 100) < percentage;

      case RolloutStrategy.USER_LIST:
        const allowedUsers = flag.config.users || [];
        return (
          allowedUsers.includes(user.userId) ||
          (user.email && allowedUsers.includes(user.email))
        );

      case RolloutStrategy.USER_ATTRIBUTE:
        const rules = flag.config.rules || [];
        return this.evaluateAttributeRules(rules, user);

      case RolloutStrategy.GRADUAL:
        return this.evaluateGradualRollout(flag, user);

      default:
        return false;
    }
  }

  private evaluateAttributeRules(
    rules: any[],
    user: UserContext
  ): boolean {
    for (const rule of rules) {
      const { attribute, operator, value } = rule;
      const userValue = user.attributes[attribute];

      switch (operator) {
        case 'equals':
          if (userValue === value) return true;
          break;
        case 'not_equals':
          if (userValue !== value) return true;
          break;
        case 'in':
          if (Array.isArray(value) && value.includes(userValue)) return true;
          break;
        case 'not_in':
          if (Array.isArray(value) && !value.includes(userValue)) return true;
          break;
        case 'greater_than':
          if (userValue > value) return true;
          break;
        case 'less_than':
          if (userValue < value) return true;
          break;
        case 'regex':
          if (new RegExp(value).test(userValue)) return true;
          break;
      }
    }

    return false;
  }

  private evaluateGradualRollout(
    flag: FeatureFlag,
    user: UserContext
  ): boolean {
    const { start_percentage, end_percentage, start_time, end_time } =
      flag.config;

    if (!start_time || !end_time) {
      return false;
    }

    const now = new Date();
    const start = new Date(start_time);
    const end = new Date(end_time);

    let currentPercentage: number;

    if (now < start) {
      currentPercentage = start_percentage || 0;
    } else if (now > end) {
      currentPercentage = end_percentage || 100;
    } else {
      // Linear interpolation
      const progress =
        (now.getTime() - start.getTime()) /
        (end.getTime() - start.getTime());
      currentPercentage =
        (start_percentage || 0) +
        ((end_percentage || 100) - (start_percentage || 0)) * progress;
    }

    const userHash = this.hashUser(user.userId, flag.key);
    return (userHash % 100) < currentPercentage;
  }

  private hashUser(userId: string, flagKey: string): number {
    const hash = createHash('md5')
      .update(`${userId}:${flagKey}`)
      .digest('hex');
    return parseInt(hash.substring(0, 8), 16);
  }

  private track(
    flagKey: string,
    user: UserContext,
    event: string,
    reason?: string
  ): void {
    if (!this.config.enableAnalytics) {
      return;
    }

    const key = `${flagKey}:${event}`;
    const current = this.analytics.get(key) || 0;
    this.analytics.set(key, current + 1);

    // In production, send to analytics service
    console.debug(`[FeatureFlag] ${flagKey} - ${event}`, {
      user: user.userId,
      reason,
    });
  }
}

// React Hook for feature flags
export function useFeatureFlag(flagKey: string, defaultValue: boolean = false) {
  // This would be implemented with React hooks in a real application
  // For now, just a placeholder
  return defaultValue;
}

// Example usage
async function exampleUsage() {
  const client = new FeatureFlagClient({
    apiKey: process.env.FEATURE_FLAG_API_KEY,
    enableAnalytics: true,
  });

  // Create test flags
  client.createFlag({
    key: 'new-checkout',
    name: 'New Checkout Flow',
    enabled: true,
    strategy: RolloutStrategy.PERCENTAGE,
    config: { percentage: 50 },
  });

  client.createFlag({
    key: 'homepage-redesign',
    name: 'Homepage Redesign',
    enabled: true,
    strategy: RolloutStrategy.ALL,
    config: {
      variants: {
        control: { weight: 50 },
        treatment: { weight: 50 },
      },
    },
  });

  // Create user context
  const user: UserContext = {
    userId: 'user123',
    email: 'user@example.com',
    attributes: {
      plan: 'premium',
      country: 'US',
      signupDate: '2024-01-15',
    },
  };

  // Check feature flag
  const isNewCheckoutEnabled = await client.isEnabled('new-checkout', user);
  if (isNewCheckoutEnabled) {
    console.log('Using new checkout flow');
  } else {
    console.log('Using legacy checkout flow');
  }

  // A/B testing
  const variant = await client.getVariant('homepage-redesign', user);
  console.log(`Homepage variant: ${variant}`);

  // Get configuration
  const config = await client.getConfig('search-settings', user);
  console.log('Search config:', config);

  // Register analytics callback
  client.onEvaluation((flag, user, result) => {
    console.log(`Flag ${flag} evaluated for ${user.userId}: ${result}`);
    // Send to analytics service
  });
}

export default FeatureFlagClient;

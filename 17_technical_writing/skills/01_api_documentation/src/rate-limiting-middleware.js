/**
 * Production-Ready Rate Limiting Middleware
 * Implements token bucket algorithm and sliding window strategies
 *
 * @module rate-limiting-middleware
 * @requires express
 * @requires redis (optional)
 */

/**
 * Token Bucket Rate Limiter
 * Classic algorithm for rate limiting with configurable refill rate
 */
class TokenBucketLimiter {
  /**
   * Initialize token bucket limiter
   * @param {Object} config - Configuration
   * @param {number} config.capacity - Maximum tokens in bucket
   * @param {number} config.refillRate - Tokens added per interval (ms)
   * @param {number} config.refillInterval - Interval in milliseconds
   */
  constructor(config) {
    this.capacity = config.capacity || 100;
    this.refillRate = config.refillRate || 1;
    this.refillInterval = config.refillInterval || 1000;
    this.buckets = new Map();
  }

  /**
   * Get or create bucket for identifier
   * @private
   * @param {string} identifier - Unique identifier (IP, user ID, etc.)
   * @returns {Object} Bucket state
   */
  getBucket(identifier) {
    if (!this.buckets.has(identifier)) {
      this.buckets.set(identifier, {
        tokens: this.capacity,
        lastRefill: Date.now()
      });
    }

    const bucket = this.buckets.get(identifier);
    this.refillBucket(bucket);
    return bucket;
  }

  /**
   * Refill tokens based on elapsed time
   * @private
   * @param {Object} bucket - Bucket to refill
   */
  refillBucket(bucket) {
    const now = Date.now();
    const elapsed = now - bucket.lastRefill;
    const tokensToAdd = (elapsed / this.refillInterval) * this.refillRate;

    if (tokensToAdd >= 1) {
      bucket.tokens = Math.min(
        this.capacity,
        bucket.tokens + Math.floor(tokensToAdd)
      );
      bucket.lastRefill = now;
    }
  }

  /**
   * Check if request is allowed
   * @param {string} identifier - Unique identifier
   * @param {number} tokensRequired - Tokens required for this request
   * @returns {Object} Result with allowed boolean and remaining tokens
   */
  isAllowed(identifier, tokensRequired = 1) {
    const bucket = this.getBucket(identifier);

    if (bucket.tokens >= tokensRequired) {
      bucket.tokens -= tokensRequired;
      return {
        allowed: true,
        remaining: bucket.tokens,
        resetAfter: this.refillInterval
      };
    }

    return {
      allowed: false,
      remaining: 0,
      resetAfter: Math.ceil(
        (tokensRequired - bucket.tokens) / this.refillRate * this.refillInterval
      )
    };
  }

  /**
   * Reset limit for identifier
   * @param {string} identifier - Unique identifier
   */
  reset(identifier) {
    this.buckets.delete(identifier);
  }

  /**
   * Clean up old buckets to prevent memory leaks
   * @param {number} maxIdleTime - Max idle time in ms before cleanup
   */
  cleanup(maxIdleTime = 3600000) {
    const now = Date.now();

    for (const [identifier, bucket] of this.buckets.entries()) {
      if (now - bucket.lastRefill > maxIdleTime) {
        this.buckets.delete(identifier);
      }
    }
  }
}

/**
 * Sliding Window Rate Limiter
 * Implements sliding window log algorithm
 */
class SlidingWindowLimiter {
  /**
   * Initialize sliding window limiter
   * @param {Object} config - Configuration
   * @param {number} config.maxRequests - Max requests allowed
   * @param {number} config.windowSize - Window size in milliseconds
   */
  constructor(config) {
    this.maxRequests = config.maxRequests || 100;
    this.windowSize = config.windowSize || 60000;
    this.windows = new Map();
  }

  /**
   * Get or create window for identifier
   * @private
   * @param {string} identifier - Unique identifier
   * @returns {Array} Request timestamps
   */
  getWindow(identifier) {
    if (!this.windows.has(identifier)) {
      this.windows.set(identifier, []);
    }
    return this.windows.get(identifier);
  }

  /**
   * Clean expired timestamps from window
   * @private
   * @param {Array} window - Window array
   * @returns {number} Count of requests in current window
   */
  cleanWindow(window) {
    const now = Date.now();
    const cutoff = now - this.windowSize;

    // Remove expired entries
    while (window.length > 0 && window[0] < cutoff) {
      window.shift();
    }

    return window.length;
  }

  /**
   * Check if request is allowed
   * @param {string} identifier - Unique identifier
   * @returns {Object} Result with allowed boolean and metrics
   */
  isAllowed(identifier) {
    const window = this.getWindow(identifier);
    const requestCount = this.cleanWindow(window);

    if (requestCount < this.maxRequests) {
      window.push(Date.now());
      return {
        allowed: true,
        remaining: this.maxRequests - requestCount - 1,
        resetAt: window[0] ? new Date(window[0] + this.windowSize) : null
      };
    }

    return {
      allowed: false,
      remaining: 0,
      resetAt: new Date(window[0] + this.windowSize)
    };
  }

  /**
   * Reset limit for identifier
   * @param {string} identifier - Unique identifier
   */
  reset(identifier) {
    this.windows.delete(identifier);
  }
}

/**
 * Express.js Rate Limiting Middleware
 * Factory for creating rate limiting middleware
 */
class RateLimitMiddleware {
  /**
   * Create rate limit middleware using token bucket
   * @param {Object} options - Configuration options
   * @param {number} options.capacity - Bucket capacity
   * @param {number} options.refillRate - Tokens per interval
   * @param {number} options.refillInterval - Interval in ms
   * @param {Function} options.keyGenerator - Function to extract rate limit key
   * @returns {Function} Express middleware
   */
  static createTokenBucketMiddleware(options = {}) {
    const {
      capacity = 100,
      refillRate = 1,
      refillInterval = 1000,
      keyGenerator = (req) => req.ip
    } = options;

    const limiter = new TokenBucketLimiter({
      capacity,
      refillRate,
      refillInterval
    });

    // Cleanup interval
    setInterval(() => limiter.cleanup(), 3600000);

    return (req, res, next) => {
      const key = keyGenerator(req);
      const result = limiter.isAllowed(key);

      // Add rate limit headers
      res.set({
        'X-RateLimit-Limit': capacity,
        'X-RateLimit-Remaining': result.remaining,
        'X-RateLimit-Reset': new Date(Date.now() + result.resetAfter).toISOString()
      });

      if (!result.allowed) {
        res.status(429).json({
          error: 'Too Many Requests',
          retryAfter: Math.ceil(result.resetAfter / 1000)
        });
        return;
      }

      next();
    };
  }

  /**
   * Create rate limit middleware using sliding window
   * @param {Object} options - Configuration options
   * @param {number} options.maxRequests - Max requests in window
   * @param {number} options.windowSize - Window size in ms
   * @param {Function} options.keyGenerator - Function to extract rate limit key
   * @returns {Function} Express middleware
   */
  static createSlidingWindowMiddleware(options = {}) {
    const {
      maxRequests = 100,
      windowSize = 60000,
      keyGenerator = (req) => req.ip
    } = options;

    const limiter = new SlidingWindowLimiter({
      maxRequests,
      windowSize
    });

    return (req, res, next) => {
      const key = keyGenerator(req);
      const result = limiter.isAllowed(key);

      res.set({
        'X-RateLimit-Limit': maxRequests,
        'X-RateLimit-Remaining': result.remaining,
        'X-RateLimit-Reset': result.resetAt
          ? result.resetAt.toISOString()
          : new Date().toISOString()
      });

      if (!result.allowed) {
        res.status(429).json({
          error: 'Too Many Requests',
          resetAt: result.resetAt
        });
        return;
      }

      next();
    };
  }

  /**
   * Create tiered rate limiting middleware
   * Different limits based on user tier or endpoint
   * @param {Object} options - Configuration
   * @param {Object} options.tiers - Tier configurations
   * @param {Function} options.tierDeterminer - Function to determine user tier
   * @returns {Function} Express middleware
   */
  static createTieredMiddleware(options = {}) {
    const {
      tiers = {
        free: { capacity: 10, refillRate: 1, refillInterval: 1000 },
        basic: { capacity: 100, refillRate: 10, refillInterval: 1000 },
        premium: { capacity: 1000, refillRate: 100, refillInterval: 1000 }
      },
      tierDeterminer = (req) => 'free'
    } = options;

    const limiters = new Map();

    // Create limiter for each tier
    for (const [tierName, config] of Object.entries(tiers)) {
      limiters.set(tierName, new TokenBucketLimiter(config));
    }

    return (req, res, next) => {
      const tier = tierDeterminer(req);
      const limiter = limiters.get(tier);

      if (!limiter) {
        return res.status(500).json({ error: 'Invalid tier configuration' });
      }

      const key = req.user?.id || req.ip;
      const result = limiter.isAllowed(key);

      const tierConfig = tiers[tier];
      res.set({
        'X-RateLimit-Limit': tierConfig.capacity,
        'X-RateLimit-Tier': tier,
        'X-RateLimit-Remaining': result.remaining,
        'X-RateLimit-Reset': new Date(Date.now() + result.resetAfter).toISOString()
      });

      if (!result.allowed) {
        res.status(429).json({
          error: 'Rate limit exceeded for your tier',
          tier,
          retryAfter: Math.ceil(result.resetAfter / 1000)
        });
        return;
      }

      next();
    };
  }

  /**
   * Create endpoint-specific rate limiting
   * Apply different limits to different endpoints
   * @param {Object} routeLimits - Route-specific configurations
   * @returns {Function} Express middleware
   */
  static createRouteSpecificMiddleware(routeLimits = {}) {
    const limiters = new Map();

    // Initialize limiters for each route
    for (const [route, config] of Object.entries(routeLimits)) {
      limiters.set(route, new TokenBucketLimiter(config));
    }

    // Default limiter
    const defaultLimiter = new TokenBucketLimiter({
      capacity: 100,
      refillRate: 1,
      refillInterval: 1000
    });

    return (req, res, next) => {
      const route = req.baseUrl;
      const limiter = limiters.get(route) || defaultLimiter;
      const key = req.ip;
      const result = limiter.isAllowed(key);

      res.set({
        'X-RateLimit-Remaining': result.remaining,
        'X-RateLimit-Reset': new Date(Date.now() + result.resetAfter).toISOString()
      });

      if (!result.allowed) {
        res.status(429).json({ error: 'Rate limit exceeded' });
        return;
      }

      next();
    };
  }
}

/**
 * Rate Limit Error Handler
 * Graceful error handling for rate limit scenarios
 */
class RateLimitErrorHandler {
  /**
   * Format rate limit error response
   * @param {Object} err - Error object
   * @param {Object} req - Express request
   * @param {Object} res - Express response
   * @param {Function} next - Next middleware
   */
  static handle(err, req, res, next) {
    if (err.status === 429) {
      return res.status(429).json({
        error: 'Too Many Requests',
        message: 'You have exceeded the rate limit. Please try again later.',
        retryAfter: err.retryAfter || 60,
        documentation: 'https://api.example.com/docs/rate-limiting'
      });
    }

    next(err);
  }
}

/**
 * Example: Using Token Bucket Middleware
 * @example
 * const express = require('express');
 * const app = express();
 *
 * app.use(RateLimitMiddleware.createTokenBucketMiddleware({
 *   capacity: 100,
 *   refillRate: 10,
 *   refillInterval: 1000,
 *   keyGenerator: (req) => req.user?.id || req.ip
 * }));
 *
 * app.get('/api/data', (req, res) => {
 *   res.json({ data: [] });
 * });
 */

/**
 * Example: Using Tiered Rate Limiting
 * @example
 * app.use(RateLimitMiddleware.createTieredMiddleware({
 *   tiers: {
 *     free: { capacity: 10, refillRate: 1, refillInterval: 1000 },
 *     pro: { capacity: 1000, refillRate: 100, refillInterval: 1000 }
 *   },
 *   tierDeterminer: (req) => req.user?.subscription || 'free'
 * }));
 */

module.exports = {
  TokenBucketLimiter,
  SlidingWindowLimiter,
  RateLimitMiddleware,
  RateLimitErrorHandler
};

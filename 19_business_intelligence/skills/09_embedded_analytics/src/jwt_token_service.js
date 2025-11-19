const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const Redis = require('ioredis');

/**
 * Production JWT token service with caching and revocation
 */
class TokenService {
  constructor() {
    this.redis = new Redis(process.env.REDIS_URL);
    this.jwtSecret = process.env.JWT_SECRET;
    this.tokenTTL = 30 * 60; // 30 minutes
  }

  /**
   * Generate embed token for user
   */
  async generateEmbedToken(user, dashboardId) {
    // Check if user has cached valid token
    const cached = await this.getCachedToken(user.id, dashboardId);
    if (cached) {
      return cached;
    }

    const tokenId = uuidv4();
    const now = Math.floor(Date.now() / 1000);

    const payload = {
      // Standard claims
      jti: tokenId,
      sub: user.id,
      iss: 'analytics-platform',
      aud: 'bi-platform',
      iat: now,
      exp: now + this.tokenTTL,

      // Custom claims
      email: user.email,
      tenant_id: user.tenantId,
      roles: user.roles,

      // RLS context
      rls: {
        tenant_id: user.tenantId,
        department: user.department,
        region: user.region
      },

      // Dashboard context
      dashboard_id: dashboardId
    };

    const token = jwt.sign(payload, this.jwtSecret, {
      algorithm: 'HS256'
    });

    // Cache token
    await this.cacheToken(user.id, dashboardId, token, this.tokenTTL - 60);

    // Log generation
    await this.logTokenGeneration(user, tokenId);

    return {
      token,
      expiresIn: this.tokenTTL,
      expiresAt: new Date((now + this.tokenTTL) * 1000).toISOString()
    };
  }

  /**
   * Verify and decode token
   */
  async verifyToken(token) {
    try {
      const decoded = jwt.verify(token, this.jwtSecret, {
        algorithms: ['HS256'],
        clockTolerance: 10 // 10 seconds tolerance
      });

      // Check if revoked
      const isRevoked = await this.isTokenRevoked(decoded.jti);
      if (isRevoked) {
        throw new Error('Token has been revoked');
      }

      return decoded;

    } catch (error) {
      await this.logTokenVerificationFailure(token, error);
      throw error;
    }
  }

  /**
   * Revoke token (logout, security incident)
   */
  async revokeToken(tokenId) {
    await this.redis.sadd('revoked_tokens', tokenId);
    await this.redis.expire('revoked_tokens', 86400); // 24 hours
  }

  /**
   * Revoke all tokens for user
   */
  async revokeAllUserTokens(userId) {
    const pattern = `token:${userId}:*`;
    const keys = await this.redis.keys(pattern);

    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  /**
   * Check if token is revoked
   */
  async isTokenRevoked(tokenId) {
    return await this.redis.sismember('revoked_tokens', tokenId);
  }

  /**
   * Get cached token
   */
  async getCachedToken(userId, dashboardId) {
    const key = `token:${userId}:${dashboardId}`;
    const cached = await this.redis.get(key);

    if (cached) {
      const { token, expiresAt } = JSON.parse(cached);

      // Verify not expired
      if (Date.now() < new Date(expiresAt).getTime()) {
        return { token, expiresAt, cached: true };
      }
    }

    return null;
  }

  /**
   * Cache token
   */
  async cacheToken(userId, dashboardId, token, ttl) {
    const key = `token:${userId}:${dashboardId}`;
    const expiresAt = new Date(Date.now() + ttl * 1000).toISOString();

    await this.redis.setex(
      key,
      ttl,
      JSON.stringify({ token, expiresAt })
    );
  }

  /**
   * Log token generation for audit
   */
  async logTokenGeneration(user, tokenId) {
    await this.redis.lpush(
      'token_audit_log',
      JSON.stringify({
        event: 'token_generated',
        tokenId,
        userId: user.id,
        tenantId: user.tenantId,
        timestamp: new Date().toISOString()
      })
    );

    await this.redis.ltrim('token_audit_log', 0, 9999); // Keep last 10k
  }

  /**
   * Log verification failure
   */
  async logTokenVerificationFailure(token, error) {
    await this.redis.lpush(
      'token_audit_log',
      JSON.stringify({
        event: 'token_verification_failed',
        token: token.substring(0, 20) + '...',
        error: error.message,
        timestamp: new Date().toISOString()
      })
    );
  }
}

module.exports = TokenService;

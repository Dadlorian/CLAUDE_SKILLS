/**
 * Production-Ready Authentication Examples
 * Demonstrates OAuth 2.0 flows and JWT validation
 *
 * @module authentication-examples
 * @requires jsonwebtoken
 * @requires axios
 * @requires express
 */

const jwt = require('jsonwebtoken');
const axios = require('axios');
const express = require('express');

/**
 * OAuth 2.0 Authorization Code Flow Handler
 * Implements the complete OAuth 2.0 authorization code flow
 */
class OAuth2Handler {
  /**
   * Initialize OAuth2 handler with configuration
   * @param {Object} config - OAuth2 configuration
   * @param {string} config.clientId - OAuth client ID
   * @param {string} config.clientSecret - OAuth client secret
   * @param {string} config.redirectUri - OAuth redirect URI
   * @param {string} config.authorizationEndpoint - Authorization server endpoint
   * @param {string} config.tokenEndpoint - Token endpoint
   * @throws {Error} If required config is missing
   */
  constructor(config) {
    this.validateConfig(config);
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
    this.redirectUri = config.redirectUri;
    this.authorizationEndpoint = config.authorizationEndpoint;
    this.tokenEndpoint = config.tokenEndpoint;
    this.tokenCache = new Map();
  }

  /**
   * Validate OAuth2 configuration
   * @private
   * @param {Object} config - Configuration to validate
   * @throws {Error} If config is invalid
   */
  validateConfig(config) {
    const required = ['clientId', 'clientSecret', 'redirectUri',
                     'authorizationEndpoint', 'tokenEndpoint'];
    for (const field of required) {
      if (!config[field]) {
        throw new Error(`OAuth2 config missing required field: ${field}`);
      }
    }
  }

  /**
   * Generate authorization URL for user login
   * @param {Object} options - Authorization options
   * @param {string} options.state - CSRF protection state token
   * @param {Array<string>} options.scopes - Requested scopes
   * @param {Object} options.extraParams - Additional parameters
   * @returns {string} Authorization URL
   */
  getAuthorizationUrl(options = {}) {
    const {
      state = this.generateState(),
      scopes = ['openid', 'profile', 'email'],
      extraParams = {}
    } = options;

    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      response_type: 'code',
      scope: scopes.join(' '),
      state,
      ...extraParams
    });

    return `${this.authorizationEndpoint}?${params.toString()}`;
  }

  /**
   * Exchange authorization code for tokens
   * @param {string} code - Authorization code from OAuth provider
   * @param {Object} options - Exchange options
   * @returns {Promise<Object>} Token response including access_token, id_token, etc.
   * @throws {Error} If token exchange fails
   */
  async exchangeCodeForToken(code, options = {}) {
    if (!code) {
      throw new Error('Authorization code is required');
    }

    try {
      const response = await axios.post(
        this.tokenEndpoint,
        {
          grant_type: 'authorization_code',
          code,
          client_id: this.clientId,
          client_secret: this.clientSecret,
          redirect_uri: this.redirectUri,
          ...options
        },
        {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          timeout: 10000
        }
      );

      return {
        accessToken: response.data.access_token,
        idToken: response.data.id_token,
        refreshToken: response.data.refresh_token,
        expiresIn: response.data.expires_in,
        tokenType: response.data.token_type,
        timestamp: Date.now()
      };
    } catch (error) {
      throw new Error(`Token exchange failed: ${error.message}`);
    }
  }

  /**
   * Refresh access token using refresh token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} New token response
   * @throws {Error} If refresh fails
   */
  async refreshAccessToken(refreshToken) {
    if (!refreshToken) {
      throw new Error('Refresh token is required');
    }

    try {
      const response = await axios.post(
        this.tokenEndpoint,
        {
          grant_type: 'refresh_token',
          refresh_token: refreshToken,
          client_id: this.clientId,
          client_secret: this.clientSecret
        },
        { timeout: 10000 }
      );

      return {
        accessToken: response.data.access_token,
        expiresIn: response.data.expires_in,
        timestamp: Date.now()
      };
    } catch (error) {
      throw new Error(`Token refresh failed: ${error.message}`);
    }
  }

  /**
   * Generate cryptographically secure state token
   * @private
   * @returns {string} State token
   */
  generateState() {
    return require('crypto')
      .randomBytes(32)
      .toString('hex');
  }
}

/**
 * JWT Validator and Token Handler
 * Handles JWT validation, decoding, and verification
 */
class JWTValidator {
  /**
   * Initialize JWT validator
   * @param {Object} config - JWT configuration
   * @param {string} config.secret - JWT secret key
   * @param {string|Array<string>} config.publicKey - Public key for RS256
   * @param {Object} config.options - JWT verification options
   */
  constructor(config) {
    this.secret = config.secret;
    this.publicKey = config.publicKey;
    this.options = config.options || {};
    this.tokenBlacklist = new Set();
  }

  /**
   * Verify and decode JWT token
   * @param {string} token - JWT token to verify
   * @param {Object} options - Verification options
   * @returns {Object} Decoded token payload
   * @throws {Error} If token is invalid
   */
  verifyToken(token, options = {}) {
    if (!token) {
      throw new Error('Token is required');
    }

    // Check if token is blacklisted
    if (this.tokenBlacklist.has(token)) {
      throw new Error('Token has been revoked');
    }

    try {
      const verifyOptions = {
        ...this.options,
        ...options
      };

      const key = this.publicKey || this.secret;
      return jwt.verify(token, key, verifyOptions);
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new Error('Token has expired');
      }
      if (error instanceof jwt.JsonWebTokenError) {
        throw new Error('Invalid token signature');
      }
      throw error;
    }
  }

  /**
   * Create new JWT token
   * @param {Object} payload - Token payload
   * @param {Object} options - Token options
   * @param {number} options.expiresIn - Token expiration in seconds
   * @returns {string} Signed JWT token
   */
  createToken(payload, options = {}) {
    const signOptions = {
      expiresIn: options.expiresIn || '24h',
      algorithm: this.publicKey ? 'RS256' : 'HS256',
      ...options
    };

    return jwt.sign(payload, this.secret, signOptions);
  }

  /**
   * Decode token without verification
   * @param {string} token - JWT token
   * @returns {Object} Decoded token
   */
  decodeToken(token) {
    return jwt.decode(token, { complete: true });
  }

  /**
   * Add token to revocation blacklist
   * @param {string} token - Token to revoke
   */
  revokeToken(token) {
    this.tokenBlacklist.add(token);
  }

  /**
   * Validate token claims
   * @param {string} token - JWT token
   * @param {Object} expectedClaims - Expected claim values
   * @returns {boolean} True if all claims match
   */
  validateClaims(token, expectedClaims) {
    try {
      const decoded = this.verifyToken(token);

      for (const [key, value] of Object.entries(expectedClaims)) {
        if (decoded[key] !== value) {
          return false;
        }
      }
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Express.js Authentication Middleware
 * Provides reusable middleware for Express applications
 */
class AuthenticationMiddleware {
  /**
   * Create authentication middleware
   * @param {JWTValidator} jwtValidator - JWT validator instance
   * @param {Object} options - Middleware options
   */
  constructor(jwtValidator, options = {}) {
    this.jwtValidator = jwtValidator;
    this.tokenExtractor = options.tokenExtractor || this.defaultTokenExtractor;
  }

  /**
   * Middleware to verify JWT token from Authorization header
   * @returns {Function} Express middleware
   */
  verifyJWT() {
    return (req, res, next) => {
      try {
        const token = this.tokenExtractor(req);

        if (!token) {
          return res.status(401).json({
            error: 'Authorization header missing or malformed'
          });
        }

        req.user = this.jwtValidator.verifyToken(token);
        req.token = token;
        next();
      } catch (error) {
        return res.status(401).json({
          error: error.message
        });
      }
    };
  }

  /**
   * Middleware to require specific scope
   * @param {string|Array<string>} requiredScopes - Required scopes
   * @returns {Function} Express middleware
   */
  requireScope(requiredScopes) {
    const scopes = Array.isArray(requiredScopes) ? requiredScopes : [requiredScopes];

    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ error: 'User not authenticated' });
      }

      const userScopes = (req.user.scope || '').split(' ');
      const hasScope = scopes.some(scope => userScopes.includes(scope));

      if (!hasScope) {
        return res.status(403).json({
          error: 'Insufficient permissions for this resource'
        });
      }

      next();
    };
  }

  /**
   * Middleware to require specific user role
   * @param {string|Array<string>} requiredRoles - Required roles
   * @returns {Function} Express middleware
   */
  requireRole(requiredRoles) {
    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];

    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ error: 'User not authenticated' });
      }

      const userRoles = Array.isArray(req.user.roles) ? req.user.roles : [];
      const hasRole = roles.some(role => userRoles.includes(role));

      if (!hasRole) {
        return res.status(403).json({
          error: 'User does not have required role'
        });
      }

      next();
    };
  }

  /**
   * Extract token from Authorization header
   * @private
   * @param {Object} req - Express request object
   * @returns {string|null} Token or null
   */
  defaultTokenExtractor(req) {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
      return null;
    }

    const parts = authHeader.split(' ');

    if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer') {
      return null;
    }

    return parts[1];
  }
}

/**
 * Example: Using OAuth2 in Express
 * @example
 * const app = express();
 * const oauth2 = new OAuth2Handler({
 *   clientId: 'your-client-id',
 *   clientSecret: 'your-client-secret',
 *   redirectUri: 'http://localhost:3000/callback',
 *   authorizationEndpoint: 'https://provider.com/oauth/authorize',
 *   tokenEndpoint: 'https://provider.com/oauth/token'
 * });
 *
 * app.get('/login', (req, res) => {
 *   const url = oauth2.getAuthorizationUrl({
 *     state: req.session.state
 *   });
 *   res.redirect(url);
 * });
 *
 * app.get('/callback', async (req, res) => {
 *   const tokens = await oauth2.exchangeCodeForToken(req.query.code);
 *   req.session.tokens = tokens;
 *   res.redirect('/');
 * });
 */

/**
 * Example: Using JWT Validator
 * @example
 * const jwtValidator = new JWTValidator({
 *   secret: process.env.JWT_SECRET,
 *   options: {
 *     issuer: 'https://example.com',
 *     audience: 'api-users'
 *   }
 * });
 *
 * const authMiddleware = new AuthenticationMiddleware(jwtValidator);
 * app.use(authMiddleware.verifyJWT());
 * app.get('/protected', (req, res) => {
 *   res.json({ user: req.user });
 * });
 */

module.exports = {
  OAuth2Handler,
  JWTValidator,
  AuthenticationMiddleware
};

/**
 * Patient Portal Authentication Service
 * Handles secure patient login with multi-factor authentication
 */

import crypto from 'crypto';
import jwt from 'jsonwebtoken';

class PatientAuthService {
  constructor(config) {
    this.dbConnection = config.dbConnection;
    this.jwtSecret = config.jwtSecret;
    this.mfaService = config.mfaService;
    this.sessionTimeout = 15 * 60 * 1000; // 15 minutes
  }

  /**
   * Login with username and password
   */
  async login(email, password) {
    // Validate inputs
    if (!email || !password) {
      throw new Error('Email and password required');
    }

    // Find patient
    const patient = await this.dbConnection.query(
      'SELECT id, email, password_hash, mfa_enabled FROM patients WHERE email = $1',
      [email]
    );

    if (patient.rows.length === 0) {
      // Log failed attempt
      await this.logFailedAttempt(email);
      throw new Error('Invalid credentials');
    }

    // Verify password
    const passwordMatch = await this.verifyPassword(
      password,
      patient.rows[0].password_hash
    );

    if (!passwordMatch) {
      await this.logFailedAttempt(email);
      throw new Error('Invalid credentials');
    }

    const patientId = patient.rows[0].id;

    // Check if MFA is enabled
    if (patient.rows[0].mfa_enabled) {
      // Generate and send OTP
      const otp = await this.generateAndSendOTP(patientId, email);
      return {
        status: 'mfa_required',
        tempToken: this.generateTempToken(patientId),
        message: 'OTP sent to your email'
      };
    }

    // Create session
    const token = this.generateAccessToken(patientId);
    await this.createSession(patientId, token);

    return {
      status: 'success',
      token: token,
      expiresIn: 3600
    };
  }

  /**
   * Verify OTP for multi-factor authentication
   */
  async verifyOTP(tempToken, otp) {
    // Verify temp token
    let decoded;
    try {
      decoded = jwt.verify(tempToken, this.jwtSecret);
    } catch (error) {
      throw new Error('Invalid temp token');
    }

    // Get OTP record
    const otpRecord = await this.dbConnection.query(
      `SELECT otp, created_at FROM otp_tokens
       WHERE patient_id = $1 AND used = false
       AND created_at > NOW() - INTERVAL '10 minutes'
       ORDER BY created_at DESC LIMIT 1`,
      [decoded.patientId]
    );

    if (otpRecord.rows.length === 0) {
      throw new Error('OTP expired or invalid');
    }

    // Verify OTP (timing-safe comparison)
    const storedOtp = otpRecord.rows[0].otp;
    const match = crypto.timingSafeEqual(
      Buffer.from(otp),
      Buffer.from(storedOtp)
    );

    if (!match) {
      throw new Error('Invalid OTP');
    }

    // Mark OTP as used
    await this.dbConnection.query(
      'UPDATE otp_tokens SET used = true WHERE patient_id = $1',
      [decoded.patientId]
    );

    // Create session
    const token = this.generateAccessToken(decoded.patientId);
    await this.createSession(decoded.patientId, token);

    return {
      status: 'success',
      token: token,
      expiresIn: 3600
    };
  }

  /**
   * Generate secure OTP and send via email
   */
  async generateAndSendOTP(patientId, email) {
    // Generate 6-digit OTP
    const otp = crypto.randomInt(100000, 999999).toString();

    // Hash OTP before storing
    const otpHash = crypto
      .createHash('sha256')
      .update(otp)
      .digest('hex');

    // Store OTP in database
    await this.dbConnection.query(
      `INSERT INTO otp_tokens (patient_id, otp, created_at)
       VALUES ($1, $2, NOW())`,
      [patientId, otpHash]
    );

    // Send OTP via email
    await this.mfaService.sendOTPEmail(email, otp);

    return otp; // Only for testing, not returned to client
  }

  /**
   * Hash password using bcrypt
   */
  async hashPassword(password) {
    const bcrypt = require('bcrypt');
    return await bcrypt.hash(password, 12);
  }

  /**
   * Verify password against hash
   */
  async verifyPassword(password, hash) {
    const bcrypt = require('bcrypt');
    return await bcrypt.compare(password, hash);
  }

  /**
   * Generate JWT access token
   */
  generateAccessToken(patientId) {
    const payload = {
      patientId: patientId,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600
    };

    return jwt.sign(payload, this.jwtSecret, {
      algorithm: 'HS256'
    });
  }

  /**
   * Generate temporary token for MFA flow
   */
  generateTempToken(patientId) {
    const payload = {
      patientId: patientId,
      type: 'temp',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 600 // 10 minutes
    };

    return jwt.sign(payload, this.jwtSecret);
  }

  /**
   * Create authenticated session
   */
  async createSession(patientId, token) {
    const sessionId = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + this.sessionTimeout);

    await this.dbConnection.query(
      `INSERT INTO sessions (session_id, patient_id, token, created_at, expires_at)
       VALUES ($1, $2, $3, NOW(), $4)`,
      [sessionId, patientId, token, expiresAt]
    );

    return sessionId;
  }

  /**
   * Verify token and return patient info
   */
  async verifyToken(token) {
    try {
      const decoded = jwt.verify(token, this.jwtSecret);

      // Check if session still exists
      const session = await this.dbConnection.query(
        `SELECT * FROM sessions
         WHERE patient_id = $1 AND token = $2 AND expires_at > NOW()`,
        [decoded.patientId, token]
      );

      if (session.rows.length === 0) {
        throw new Error('Session invalid or expired');
      }

      return decoded;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  /**
   * Logout patient
   */
  async logout(token) {
    const decoded = jwt.verify(token, this.jwtSecret);

    await this.dbConnection.query(
      'DELETE FROM sessions WHERE patient_id = $1 AND token = $2',
      [decoded.patientId, token]
    );

    return { status: 'success' };
  }

  /**
   * Log failed login attempts
   */
  async logFailedAttempt(email) {
    await this.dbConnection.query(
      `INSERT INTO login_attempts (email, status, timestamp)
       VALUES ($1, 'failed', NOW())`,
      [email]
    );
  }
}

export default PatientAuthService;

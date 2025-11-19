/**
 * Patient Portal Authentication
 * Secure authentication with MFA support
 */

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const speakeasy = require('speakeasy');
const nodemailer = require('nodemailer');

class PatientPortalAuth {
  constructor(config) {
    this.config = config;
    this.jwtSecret = config.jwtSecret;
    this.tokenExpiry = config.tokenExpiry || '1h';
    this.mfaRequired = config.mfaRequired || false;
  }

  /**
   * Register new patient portal user
   */
  async register(userData) {
    const {
      email,
      password,
      firstName,
      lastName,
      dateOfBirth,
      medicalRecordNumber
    } = userData;

    // Validate password strength
    if (!this.isStrongPassword(password)) {
      throw new Error(
        'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
      );
    }

    // Hash password
    const salt = await bcrypt.genSalt(12);
    const passwordHash = await bcrypt.hash(password, salt);

    // Verify patient exists in EHR
    const patient = await this.verifyPatientIdentity(
      medicalRecordNumber,
      dateOfBirth
    );

    if (!patient) {
      throw new Error('Unable to verify patient identity');
    }

    // Create portal user
    const user = await db.portal_user.create({
      patient_id: patient.patient_id,
      email,
      password_hash: passwordHash,
      first_name: firstName,
      last_name: lastName,
      email_verified: false,
      mfa_enabled: false,
      account_locked: false
    });

    // Send verification email
    await this.sendVerificationEmail(user);

    return {
      user_id: user.user_id,
      message: 'Registration successful. Please check email to verify account.'
    };
  }

  /**
   * Login with email and password
   */
  async login(email, password, mfaToken = null) {
    // Find user
    const user = await db.portal_user.findOne({ where: { email } });

    if (!user) {
      // Constant-time response to prevent user enumeration
      await bcrypt.hash(password, 10);
      throw new Error('Invalid email or password');
    }

    // Check if account is locked
    if (user.account_locked) {
      throw new Error('Account is locked. Please contact support.');
    }

    // Check if email is verified
    if (!user.email_verified) {
      throw new Error('Please verify your email address first.');
    }

    // Verify password
    const passwordValid = await bcrypt.compare(password, user.password_hash);

    if (!passwordValid) {
      await this.handleFailedLogin(user);
      throw new Error('Invalid email or password');
    }

    // Check MFA if enabled
    if (user.mfa_enabled) {
      if (!mfaToken) {
        return {
          requiresMFA: true,
          message: 'Please enter your MFA code'
        };
      }

      const mfaValid = this.verifyMFA(user.mfa_secret, mfaToken);
      if (!mfaValid) {
        throw new Error('Invalid MFA code');
      }
    }

    // Reset failed login attempts
    await this.resetFailedLogins(user);

    // Generate JWT token
    const token = this.generateToken(user);

    // Update last login
    await user.update({ last_login: new Date() });

    // Log successful login
    await this.logAuditEvent('LOGIN_SUCCESS', user.user_id);

    return {
      token,
      user: {
        user_id: user.user_id,
        email: user.email,
        name: `${user.first_name} ${user.last_name}`
      }
    };
  }

  /**
   * Setup MFA for user
   */
  async setupMFA(userId) {
    const secret = speakeasy.generateSecret({
      name: `PatientPortal (${userId})`,
      length: 32
    });

    // Store encrypted secret
    await db.portal_user.update(
      {
        mfa_secret: this.encrypt(secret.base32),
        mfa_enabled: false  // Not enabled until verified
      },
      { where: { user_id: userId } }
    );

    return {
      secret: secret.base32,
      qrCode: secret.otpauth_url
    };
  }

  /**
   * Verify MFA token
   */
  verifyMFA(secret, token) {
    return speakeasy.totp.verify({
      secret: this.decrypt(secret),
      encoding: 'base32',
      token,
      window: 2
    });
  }

  /**
   * Validate password strength
   */
  isStrongPassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return (
      password.length >= minLength &&
      hasUpperCase &&
      hasLowerCase &&
      hasNumbers &&
      hasSpecialChar
    );
  }

  /**
   * Generate JWT token
   */
  generateToken(user) {
    return jwt.sign(
      {
        user_id: user.user_id,
        patient_id: user.patient_id,
        email: user.email
      },
      this.jwtSecret,
      { expiresIn: this.tokenExpiry }
    );
  }

  /**
   * Verify patient identity against EHR
   */
  async verifyPatientIdentity(mrn, dateOfBirth) {
    // Query EHR database
    const patient = await db.patient.findOne({
      where: {
        medical_record_number: mrn,
        date_of_birth: dateOfBirth
      }
    });

    return patient;
  }

  /**
   * Handle failed login attempt
   */
  async handleFailedLogin(user) {
    const attempts = user.failed_login_attempts + 1;

    if (attempts >= 5) {
      await user.update({
        failed_login_attempts: attempts,
        account_locked: true
      });

      await this.sendAccountLockedEmail(user);
      throw new Error('Account locked due to multiple failed login attempts');
    }

    await user.update({ failed_login_attempts: attempts });
  }

  /**
   * Reset failed login attempts
   */
  async resetFailedLogins(user) {
    await user.update({ failed_login_attempts: 0 });
  }

  /**
   * Send verification email
   */
  async sendVerificationEmail(user) {
    const token = jwt.sign(
      { user_id: user.user_id },
      this.jwtSecret,
      { expiresIn: '24h' }
    );

    const verifyLink = `${this.config.portalUrl}/verify-email?token=${token}`;

    const transporter = nodemailer.createTransporter(this.config.emailConfig);

    await transporter.sendMail({
      from: this.config.emailFrom,
      to: user.email,
      subject: 'Verify Your Patient Portal Account',
      html: `
        <h2>Welcome to Our Patient Portal</h2>
        <p>Please click the link below to verify your email address:</p>
        <a href="${verifyLink}">Verify Email</a>
        <p>This link expires in 24 hours.</p>
      `
    });
  }

  /**
   * Log audit event
   */
  async logAuditEvent(eventType, userId, details = {}) {
    await db.audit_log.create({
      event_type: eventType,
      user_id: userId,
      details: JSON.stringify(details),
      ip_address: details.ip_address,
      user_agent: details.user_agent,
      timestamp: new Date()
    });
  }

  encrypt(text) {
    // Use AES-256-GCM encryption
    const crypto = require('crypto');
    const algorithm = 'aes-256-gcm';
    const key = Buffer.from(this.config.encryptionKey, 'hex');
    const iv = crypto.randomBytes(16);

    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
  }

  decrypt(text) {
    const crypto = require('crypto');
    const algorithm = 'aes-256-gcm';
    const key = Buffer.from(this.config.encryptionKey, 'hex');

    const parts = text.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const authTag = Buffer.from(parts[1], 'hex');
    const encrypted = parts[2];

    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }
}

module.exports = PatientPortalAuth;

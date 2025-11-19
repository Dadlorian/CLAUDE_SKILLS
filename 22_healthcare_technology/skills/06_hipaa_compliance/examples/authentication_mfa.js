/**
 * Multi-Factor Authentication Implementation
 * Required for remote access to ePHI per HIPAA Security Rule
 */
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

class MFAService {
  // Generate MFA secret for user
  static generateSecret(userEmail) {
    return speakeasy.generateSecret({
      name: `HIPAA App (${userEmail})`,
      length: 32
    });
  }

  // Generate QR code for setup
  static async generateQRCode(secret) {
    return await QRCode.toDataURL(secret.otpauth_url);
  }

  // Verify TOTP token
  static verifyToken(secret, token) {
    return speakeasy.totp.verify({
      secret: secret.base32,
      encoding: 'base32',
      token: token,
      window: 2  // Allow 2 time steps (60 seconds) tolerance
    });
  }

  // Generate backup codes
  static generateBackupCodes(count = 10) {
    const codes = [];
    for (let i = 0; i < count; i++) {
      codes.push(this.generateBackupCode());
    }
    return codes;
  }

  static generateBackupCode() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let code = '';
    for (let i = 0; i < 8; i++) {
      code += chars[Math.floor(Math.random() * chars.length)];
    }
    return code;
  }

  // Verify backup code
  static verifyBackupCode(userBackupCodes, providedCode) {
    const index = userBackupCodes.indexOf(providedCode);
    if (index > -1) {
      userBackupCodes.splice(index, 1);  // Remove used code
      return true;
    }
    return false;
  }
}

module.exports = MFAService;

// Telehealth patient authentication with MFA support
const bcrypt = require('bcrypt');
const speakeasy = require('speakeasy');
const jwt = require('jsonwebtoken');

class TelehealthAuthService {
  async authenticatePatient(email, password, mfaToken = null) {
    const user = await db.query('SELECT * FROM patients WHERE email = $1', [email]);
    
    if (!user.rows[0] || !await bcrypt.compare(password, user.rows[0].password_hash)) {
      throw new Error('Invalid credentials');
    }

    if (user.rows[0].mfa_enabled) {
      if (!mfaToken) {
        return { requiresMFA: true };
      }
      
      const verified = speakeasy.totp.verify({
        secret: user.rows[0].mfa_secret,
        encoding: 'base32',
        token: mfaToken
      });
      
      if (!verified) {
        throw new Error('Invalid MFA token');
      }
    }

    const token = jwt.sign(
      { userId: user.rows[0].id, role: 'patient' },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    return { token, user: user.rows[0] };
  }
}

module.exports = TelehealthAuthService;

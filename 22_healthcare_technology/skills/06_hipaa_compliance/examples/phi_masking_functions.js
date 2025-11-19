/**
 * PHI Masking Functions for Displays and Logs
 * Prevents accidental PHI exposure in logs, displays, and error messages
 */

class PHIMasker {
  // Mask SSN (show last 4 digits)
  static maskSSN(ssn) {
    if (!ssn) return '';
    return `***-**-${ssn.slice(-4)}`;
  }

  // Mask credit card
  static maskCreditCard(cardNumber) {
    if (!cardNumber) return '';
    return `****-****-****-${cardNumber.slice(-4)}`;
  }

  // Mask email (show first char and domain)
  static maskEmail(email) {
    if (!email) return '';
    const [name, domain] = email.split('@');
    return `${name[0]}***@${domain}`;
  }

  // Mask phone number (show last 4)
  static maskPhone(phone) {
    if (!phone) return '';
    return `***-***-${phone.slice(-4)}`;
  }

  // Mask name (show initials)
  static maskName(fullName) {
    if (!fullName) return '';
    const parts = fullName.split(' ');
    return parts.map(p => `${p[0]}.`).join(' ');
  }

  // Mask address
  static maskAddress(address) {
    if (!address) return '';
    return address.split(',')[0].split(' ')[0] + ' [REDACTED]';
  }

  // Mask date of birth (show year only)
  static maskDOB(dob) {
    if (!dob) return '';
    const year = dob.split('-')[0] || dob.split('/')[2];
    return `**/**/${year}`;
  }

  // Comprehensive masking for log entries
  static maskLogEntry(logEntry) {
    let masked = { ...logEntry };
    
    const fieldsToMask = ['ssn', 'email', 'phone', 'name', 'address', 'dob', 'creditCard'];
    
    for (const field of fieldsToMask) {
      if (masked[field]) {
        const maskMethod = `mask${field.charAt(0).toUpperCase() + field.slice(1)}`;
        if (this[maskMethod]) {
          masked[field] = this[maskMethod](masked[field]);
        }
      }
    }
    
    return masked;
  }

  // Mask patient record for display (keep some info visible)
  static maskPatientForDisplay(patient) {
    return {
      ...patient,
      ssn: this.maskSSN(patient.ssn),
      email: this.maskEmail(patient.email),
      phone: this.maskPhone(patient.phone),
      address: this.maskAddress(patient.address),
      dob: this.maskDOB(patient.dob)
    };
  }
}

module.exports = PHIMasker;

/**
 * HIPAA-Compliant Audit Logging Middleware for Express.js
 *
 * Logs all PHI access with required data elements:
 * - User ID
 * - Timestamp
 * - Action performed
 * - Patient identifier
 * - Result (success/failure)
 * - Workstation/IP address
 */

const crypto = require('crypto');

class HIPAAAuditLogger {
  constructor(options = {}) {
    this.logStorage = options.logStorage || console.log; // Should be replaced with proper storage
    this.sensitiveRoutes = options.sensitiveRoutes || ['/api/patients', '/api/records', '/api/phi'];
    this.includeRequestBody = options.includeRequestBody || false;
  }

  /**
   * Express middleware function
   */
  middleware() {
    return async (req, res, next) => {
      // Only log PHI-related endpoints
      if (!this.shouldLog(req.path)) {
        return next();
      }

      const startTime = Date.now();

      // Capture original end function
      const originalEnd = res.end;
      const self = this;

      // Override res.end to capture response
      res.end = function(chunk, encoding) {
        res.end = originalEnd;
        res.end(chunk, encoding);

        const duration = Date.now() - startTime;

        // Create audit log entry
        const auditEntry = self.createAuditEntry(req, res, duration);

        // Store audit log (should be tamper-resistant storage)
        self.storeAuditLog(auditEntry);
      };

      next();
    };
  }

  /**
   * Determine if request should be logged
   */
  shouldLog(path) {
    return this.sensitiveRoutes.some(route => path.startsWith(route));
  }

  /**
   * Create comprehensive audit log entry
   */
  createAuditEntry(req, res, duration) {
    const entry = {
      // Required HIPAA audit elements
      timestamp: new Date().toISOString(),
      userId: req.user?.id || 'ANONYMOUS',
      username: req.user?.username || 'ANONYMOUS',
      userRole: req.user?.role || 'UNKNOWN',

      // Action details
      action: this.determineAction(req.method, req.path),
      method: req.method,
      path: req.path,

      // Patient/PHI identifier
      patientId: req.params.patientId || req.query.patientId || req.body?.patientId || 'N/A',
      resourceType: this.determineResourceType(req.path),

      // Result
      statusCode: res.statusCode,
      result: res.statusCode < 400 ? 'SUCCESS' : 'FAILURE',

      // Source information
      ipAddress: req.ip || req.connection.remoteAddress,
      userAgent: req.get('user-agent'),
      workstation: req.get('x-workstation-id') || 'UNKNOWN',

      // Session information
      sessionId: req.session?.id || 'N/A',

      // Performance
      duration: duration,

      // Request details (configurable - may contain PHI)
      queryParams: this.sanitizeParams(req.query),

      // Security
      auditId: this.generateAuditId(),
      hash: null // Will be set after hashing
    };

    // Create hash for integrity
    entry.hash = this.createHash(entry);

    return entry;
  }

  /**
   * Determine action from HTTP method and path
   */
  determineAction(method, path) {
    const actionMap = {
      'GET': 'VIEW',
      'POST': 'CREATE',
      'PUT': 'UPDATE',
      'PATCH': 'UPDATE',
      'DELETE': 'DELETE'
    };

    return actionMap[method] || 'UNKNOWN';
  }

  /**
   * Determine resource type from path
   */
  determineResourceType(path) {
    if (path.includes('/patients')) return 'PATIENT_DEMOGRAPHICS';
    if (path.includes('/records')) return 'MEDICAL_RECORD';
    if (path.includes('/lab')) return 'LAB_RESULTS';
    if (path.includes('/imaging')) return 'IMAGING';
    if (path.includes('/medications')) return 'MEDICATIONS';
    if (path.includes('/billing')) return 'BILLING';
    return 'PHI';
  }

  /**
   * Sanitize parameters (remove actual PHI values, keep keys)
   */
  sanitizeParams(params) {
    const sanitized = {};
    for (const [key, value] of Object.entries(params)) {
      // Keep the parameter name, redact the value
      sanitized[key] = typeof value === 'string' ? '[REDACTED]' : typeof value;
    }
    return sanitized;
  }

  /**
   * Generate unique audit ID
   */
  generateAuditId() {
    return `AUDIT-${Date.now()}-${crypto.randomBytes(8).toString('hex')}`;
  }

  /**
   * Create cryptographic hash for audit log integrity
   */
  createHash(entry) {
    const entryString = JSON.stringify({
      timestamp: entry.timestamp,
      userId: entry.userId,
      action: entry.action,
      patientId: entry.patientId,
      result: entry.result,
      auditId: entry.auditId
    });

    return crypto
      .createHash('sha256')
      .update(entryString)
      .digest('hex');
  }

  /**
   * Store audit log (implement tamper-resistant storage)
   */
  async storeAuditLog(entry) {
    // In production, this should write to:
    // - Centralized SIEM
    // - Write-once database (append-only)
    // - Immutable log storage
    // - Encrypted log files

    // For demonstration:
    this.logStorage(JSON.stringify(entry));

    // Example production implementation:
    /*
    await AuditLogModel.create(entry); // Append-only table
    await SIEMService.send(entry); // Send to SIEM
    await BackupLogger.write(entry); // Redundant storage
    */
  }

  /**
   * Verify audit log integrity
   */
  verifyIntegrity(entry) {
    const storedHash = entry.hash;
    const tempEntry = { ...entry };
    delete tempEntry.hash;

    const computedHash = this.createHash(tempEntry);

    return storedHash === computedHash;
  }
}

// Usage example
/*
const express = require('express');
const app = express();

const auditLogger = new HIPAAAuditLogger({
  logStorage: async (entry) => {
    // Store in database
    await db.auditLogs.insert(entry);
    // Also send to SIEM
    await siem.send(entry);
  },
  sensitiveRoutes: ['/api/patients', '/api/records', '/api/phi']
});

app.use(auditLogger.middleware());

app.get('/api/patients/:patientId', authenticate, authorize('nurse'), async (req, res) => {
  // This will be automatically logged
  const patient = await getPatient(req.params.patientId);
  res.json(patient);
});
*/

module.exports = HIPAAAuditLogger;

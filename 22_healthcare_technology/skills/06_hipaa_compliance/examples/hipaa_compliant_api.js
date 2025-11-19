/**
 * HIPAA-Compliant RESTful API Template
 * Includes authentication, authorization, audit logging, encryption
 */
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();

// Security headers
app.use(helmet({
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// Rate limiting (prevent brute force)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// HIPAA-compliant API route
app.get('/api/patients/:id',
  authenticate,      // Verify JWT
  authorize('read'), // Check permissions
  auditLog,          // Log access
  async (req, res) => {
    try {
      const patient = await getPatient(req.params.id);
      
      // Filter based on minimum necessary
      const filtered = filterPHI(patient, req.user.role);
      
      // Mask sensitive fields for display
      const masked = maskPHI(filtered);
      
      res.json(masked);
    } catch (error) {
      // Don't expose PHI in error messages
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

module.exports = app;

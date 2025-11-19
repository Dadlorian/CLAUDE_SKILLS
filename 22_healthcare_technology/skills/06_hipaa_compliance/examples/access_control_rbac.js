/**
 * HIPAA-Compliant Role-Based Access Control (RBAC) System
 * 
 * Implements fine-grained access control for PHI based on roles
 * Enforces minimum necessary principle
 */

const rolePermissions = {
  physician: {
    patients: ['create', 'read', 'update', 'delete'],
    medicalRecords: ['create', 'read', 'update'],
    labResults: ['read', 'order'],
    medications: ['create', 'read', 'update', 'prescribe'],
    billing: ['read'],
    demographics: ['read', 'update']
  },
  nurse: {
    patients: ['read', 'update'],
    medicalRecords: ['read', 'update'],
    labResults: ['read'],
    medications: ['read', 'administer'],
    billing: [],
    demographics: ['read', 'update']
  },
  frontDesk: {
    patients: ['create', 'read'],
    medicalRecords: [],
    labResults: [],
    medications: [],
    billing: ['create', 'read'],
    demographics: ['create', 'read', 'update']
  },
  billingStaff: {
    patients: ['read'],
    medicalRecords: [],
    labResults: [],
    medications: [],
    billing: ['create', 'read', 'update'],
    demographics: ['read']
  },
  labTech: {
    patients: ['read'],
    medicalRecords: [],
    labResults: ['create', 'read', 'update'],
    medications: [],
    billing: [],
    demographics: ['read']
  }
};

class HIPAARBACService {
  constructor(auditLogger) {
    this.auditLogger = auditLogger;
  }

  /**
   * Check if user has permission for resource and action
   */
  hasPermission(user, resource, action) {
    if (!user || !user.role) {
      return false;
    }

    const permissions = rolePermissions[user.role];
    if (!permissions) {
      return false;
    }

    const resourcePermissions = permissions[resource];
    if (!resourcePermissions) {
      return false;
    }

    return resourcePermissions.includes(action);
  }

  /**
   * Middleware to enforce access control
   */
  authorize(resource, action) {
    return async (req, res, next) => {
      const user = req.user;

      // Check permission
      const hasPermission = this.hasPermission(user, resource, action);

      // Log access attempt
      if (this.auditLogger) {
        await this.auditLogger.log({
          userId: user?.id,
          userRole: user?.role,
          resource,
          action,
          result: hasPermission ? 'GRANTED' : 'DENIED',
          timestamp: new Date().toISOString(),
          ipAddress: req.ip
        });
      }

      if (!hasPermission) {
        return res.status(403).json({
          error: 'Access Denied',
          message: 'Insufficient permissions for this resource',
          required: `${resource}:${action}`
        });
      }

      next();
    };
  }

  /**
   * Check if user can access specific patient's data
   */
  canAccessPatient(user, patientId) {
    // Add logic for patient relationship checking
    // e.g., assigned provider, care team member, etc.
    return true; // Simplified for example
  }

  /**
   * Filter data based on minimum necessary
   */
  filterPHI(data, user) {
    const role = user.role;

    // Different roles see different PHI elements
    const fieldAccess = {
      physician: 'all',
      nurse: ['demographics', 'vitals', 'medications', 'allergies'],
      frontDesk: ['demographics', 'insurance'],
      billingStaff: ['demographics', 'insurance', 'billing'],
      labTech: ['demographics', 'labResults']
    };

    const allowedFields = fieldAccess[role];

    if (allowedFields === 'all') {
      return data;
    }

    // Filter to only allowed fields
    const filtered = {};
    for (const field of allowedFields) {
      if (data[field]) {
        filtered[field] = data[field];
      }
    }

    return filtered;
  }
}

// Usage example
module.exports = HIPAARBACService;

/*
const express = require('express');
const app = express();

const rbac = new HIPAARBACService(auditLogger);

// Protected route - only physicians can create medical records
app.post('/api/medical-records', 
  authenticate,
  rbac.authorize('medicalRecords', 'create'),
  async (req, res) => {
    // Create medical record
    const record = await createMedicalRecord(req.body);
    res.json(record);
  }
);

// Protected route - nurses can read medical records
app.get('/api/medical-records/:id',
  authenticate,
  rbac.authorize('medicalRecords', 'read'),
  async (req, res) => {
    const record = await getMedicalRecord(req.params.id);

    // Filter based on minimum necessary
    const filtered = rbac.filterPHI(record, req.user);

    res.json(filtered);
  }
);
*/

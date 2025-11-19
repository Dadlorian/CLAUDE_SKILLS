# Healthcare API Patterns

## Executive Summary

Production-grade patterns for designing RESTful healthcare APIs and async messaging systems that comply with healthcare regulations (HIPAA, FHIR, HL7) while maintaining high availability, security, and interoperability.

---

## Table of Contents

1. [RESTful Healthcare API Patterns](#restful-healthcare-api-patterns)
2. [Async Messaging Patterns](#async-messaging-patterns)
3. [Security & Compliance](#security--compliance)
4. [Performance Optimization](#performance-optimization)
5. [Error Handling & Resilience](#error-handling--resilience)
6. [Real-World Examples](#real-world-examples)

---

## RESTful Healthcare API Patterns

### 1. FHIR-Compliant Resource API

**Pattern**: Implement RESTful APIs following FHIR (Fast Healthcare Interoperability Resources) specification.

**Implementation**:

```javascript
// Base FHIR Resource Controller
class FHIRResourceController {
  async getResource(req, res) {
    const { resourceType, id } = req.params;
    const { _include, _revinclude, _elements } = req.query;

    try {
      const resource = await FHIRResourceService.fetch(
        resourceType,
        id,
        { include: _include, revinclude: _revinclude }
      );

      // Ensure HIPAA compliance: audit logging
      AuditLogger.log({
        action: 'READ',
        resourceType,
        resourceId: id,
        userId: req.user.id,
        timestamp: new Date(),
        ipAddress: req.ip
      });

      res.json(this.formatFHIRResponse(resource));
    } catch (error) {
      handleFHIRError(error, res);
    }
  }

  async searchResources(req, res) {
    const { resourceType } = req.params;
    const searchParams = this.parseFHIRSearchParams(req.query);

    try {
      const result = await FHIRResourceService.search(
        resourceType,
        searchParams
      );

      res.json({
        resourceType: 'Bundle',
        type: 'searchset',
        total: result.total,
        link: this.generatePaginationLinks(resourceType, searchParams, result),
        entry: result.entries.map(entry => ({
          fullUrl: `${process.env.API_BASE_URL}/${resourceType}/${entry.id}`,
          resource: entry,
          search: { mode: 'match' }
        }))
      });
    } catch (error) {
      handleFHIRError(error, res);
    }
  }

  async createResource(req, res) {
    const { resourceType } = req.params;

    try {
      // Validate FHIR schema
      const validated = await FHIRValidator.validate(resourceType, req.body);

      const resource = await FHIRResourceService.create(
        resourceType,
        validated
      );

      res.status(201)
        .location(`/${resourceType}/${resource.id}`)
        .json(resource);
    } catch (error) {
      handleFHIRError(error, res);
    }
  }

  async updateResource(req, res) {
    const { resourceType, id } = req.params;

    try {
      const validated = await FHIRValidator.validate(resourceType, req.body);

      const resource = await FHIRResourceService.update(
        resourceType,
        id,
        validated
      );

      res.json(resource);
    } catch (error) {
      handleFHIRError(error, res);
    }
  }

  formatFHIRResponse(resource) {
    return {
      ...resource,
      meta: {
        versionId: resource.version,
        lastUpdated: resource.updatedAt,
        profile: [`http://hl7.org/fhir/StructureDefinition/${resource.resourceType}`]
      }
    };
  }

  parseFHIRSearchParams(queryParams) {
    const params = {};
    Object.entries(queryParams).forEach(([key, value]) => {
      if (!key.startsWith('_')) {
        params[key] = Array.isArray(value) ? value : [value];
      }
    });
    return params;
  }

  generatePaginationLinks(resourceType, searchParams, result) {
    const links = [];
    const baseUrl = `${process.env.API_BASE_URL}/${resourceType}`;

    if (result.nextPage) {
      links.push({
        relation: 'next',
        url: `${baseUrl}?_offset=${result.nextOffset}&_count=${result.pageSize}`
      });
    }

    return links;
  }
}
```

**Key Features**:
- FHIR R4 compatibility
- Search parameter support
- Pagination with offset/count
- Response formatting with metadata
- Audit logging for compliance

**Use Cases**:
- Patient data retrieval
- Clinical resource management
- Interoperability with other FHIR systems

---

### 2. Versioning & Backwards Compatibility

**Pattern**: Maintain API versioning to support legacy clients while introducing new features.

**Implementation**:

```javascript
class VersionedAPIRouter {
  constructor(app) {
    this.app = app;
    this.versions = new Map();
  }

  registerVersion(version, handlers) {
    this.versions.set(version, handlers);
  }

  getRouter(version) {
    const router = express.Router();
    const handlers = this.versions.get(version);

    if (!handlers) {
      throw new Error(`API version ${version} not supported`);
    }

    Object.entries(handlers).forEach(([route, handler]) => {
      router.use(route, handler);
    });

    return router;
  }

  setupVersionedRoutes() {
    // v1: Legacy endpoints
    this.registerVersion('v1', {
      '/patient': patientHandlersV1,
      '/observation': observationHandlersV1
    });

    // v2: Enhanced with FHIR
    this.registerVersion('v2', {
      '/patient': patientHandlersV2,
      '/observation': observationHandlersV2
    });

    // Mount all versions
    this.app.use('/api/v1', this.getRouter('v1'));
    this.app.use('/api/v2', this.getRouter('v2'));

    // Deprecation warning middleware
    this.app.use('/api/v1', (req, res, next) => {
      res.set('Deprecation', 'true');
      res.set('Sunset', '2025-12-31T00:00:00Z');
      next();
    });
  }
}
```

**Best Practices**:
- Support at least 2 major versions
- Set deprecation notices (Deprecation header)
- Provide migration guides for deprecated endpoints
- Remove versions only after minimum 12-month notice

---

## Async Messaging Patterns

### 3. Event-Driven Health Data Pipeline

**Pattern**: Use event streaming for real-time health data processing while maintaining data integrity.

**Implementation**:

```javascript
class HealthDataEventBus {
  constructor(kafkaClient) {
    this.kafka = kafkaClient;
    this.producers = new Map();
    this.consumers = new Map();
  }

  async publishHealthEvent(eventType, data) {
    const producer = this.getOrCreateProducer(eventType);

    const event = {
      eventId: uuid(),
      eventType,
      timestamp: new Date().toISOString(),
      data: this.encryptPHI(data),
      version: '1.0',
      source: process.env.SERVICE_NAME
    };

    try {
      await producer.send({
        topic: `healthcare.${eventType}`,
        messages: [
          {
            key: data.patientId,
            value: JSON.stringify(event),
            headers: {
              'correlation-id': event.eventId,
              'encryption': 'AES-256-GCM'
            }
          }
        ]
      });

      return event.eventId;
    } catch (error) {
      // Retry with exponential backoff
      await this.retryWithBackoff(() =>
        producer.send({ topic: `healthcare.${eventType}`, messages: [...] })
      );
    }
  }

  async consumeHealthEvents(eventType, handler) {
    const consumer = this.kafka.consumer({
      groupId: `healthcare-consumer-${eventType}`,
      sessionTimeout: 30000
    });

    await consumer.subscribe({ topic: `healthcare.${eventType}` });

    await consumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        const event = JSON.parse(message.value.toString());

        try {
          // Decrypt PHI
          event.data = this.decryptPHI(event.data);

          // Process event with transaction
          await this.processWithTransaction(async () => {
            await handler(event);
          });

          // Commit offset after successful processing
        } catch (error) {
          AuditLogger.error({
            eventId: event.eventId,
            error: error.message,
            timestamp: new Date()
          });
          throw error; // Let framework handle retry/DLQ
        }
      },
      autoCommit: false
    });
  }

  encryptPHI(data) {
    // Encrypt sensitive fields
    return encryptionService.encrypt(JSON.stringify(data));
  }

  decryptPHI(encryptedData) {
    return JSON.parse(encryptionService.decrypt(encryptedData));
  }

  getOrCreateProducer(eventType) {
    if (!this.producers.has(eventType)) {
      this.producers.set(eventType, this.kafka.producer());
    }
    return this.producers.get(eventType);
  }

  async processWithTransaction(handler) {
    const transaction = await db.transaction();
    try {
      await handler();
      await transaction.commit();
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }

  async retryWithBackoff(fn, maxRetries = 3, delay = 1000) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        if (attempt === maxRetries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt)));
      }
    }
  }
}

// Usage
const eventBus = new HealthDataEventBus(kafkaClient);

// Publish vital sign measurement
await eventBus.publishHealthEvent('vital-sign.measured', {
  patientId: 'patient-123',
  vitals: { bp: '120/80', hr: 72 },
  timestamp: new Date()
});

// Subscribe to vital sign events
await eventBus.consumeHealthEvents('vital-sign.measured', async (event) => {
  const observation = await Observation.create({
    patientId: event.data.patientId,
    value: event.data.vitals,
    time: event.data.timestamp
  });

  // Trigger clinical alerts if thresholds exceeded
  await AlertService.checkThresholds(observation);
});
```

**Benefits**:
- Real-time data processing
- Decoupled services
- Event replay capability for audit
- Automatic retry with DLQ support

---

### 4. Request-Reply Pattern with Correlation

**Pattern**: Synchronous RPC-style communication with guaranteed delivery and correlation.

**Implementation**:

```javascript
class HealthcareRPCClient {
  constructor(messageBroker) {
    this.broker = messageBroker;
    this.pendingRequests = new Map();
  }

  async requestPatientMerge(sourceId, targetId, timeout = 30000) {
    const correlationId = uuid();
    const replyTo = `reply.${correlationId}`;

    const request = {
      requestId: correlationId,
      action: 'MERGE_PATIENT',
      payload: { sourceId, targetId },
      timestamp: new Date().toISOString()
    };

    // Create reply queue listener
    const replyPromise = new Promise((resolve, reject) => {
      this.pendingRequests.set(correlationId, {
        resolve,
        reject,
        timeout: setTimeout(() => {
          this.pendingRequests.delete(correlationId);
          reject(new Error(`RPC timeout for ${correlationId}`));
        }, timeout)
      });
    });

    // Send request
    await this.broker.publish({
      exchange: 'healthcare.rpc',
      routingKey: 'patient.merge',
      message: request,
      replyTo,
      correlationId
    });

    return replyPromise;
  }

  async handleReply(message) {
    const { correlationId } = message;
    const pending = this.pendingRequests.get(correlationId);

    if (pending) {
      clearTimeout(pending.timeout);
      this.pendingRequests.delete(correlationId);

      if (message.error) {
        pending.reject(new Error(message.error));
      } else {
        pending.resolve(message.result);
      }
    }
  }
}
```

---

## Security & Compliance

### 5. HIPAA-Compliant Data Handling

**Pattern**: Encrypt, audit, and control access to PHI (Protected Health Information).

**Implementation**:

```javascript
class HIPAACompliantDataHandler {
  async encryptPHI(plaintext, patientId) {
    const encryptionKey = await this.getPatientEncryptionKey(patientId);
    const iv = crypto.randomBytes(16);

    const cipher = crypto.createCipheriv('aes-256-gcm', encryptionKey, iv);
    let encrypted = cipher.update(plaintext, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const tag = cipher.getAuthTag();

    return {
      encrypted,
      iv: iv.toString('hex'),
      tag: tag.toString('hex'),
      algorithm: 'aes-256-gcm'
    };
  }

  async decryptPHI(encryptedData, patientId) {
    const encryptionKey = await this.getPatientEncryptionKey(patientId);
    const { encrypted, iv, tag } = encryptedData;

    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      encryptionKey,
      Buffer.from(iv, 'hex')
    );

    decipher.setAuthTag(Buffer.from(tag, 'hex'));

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  async logDataAccess(userId, patientId, action, success) {
    await AuditLog.create({
      userId,
      patientId,
      action,
      success,
      timestamp: new Date(),
      ipAddress: this.currentRequest?.ip,
      userAgent: this.currentRequest?.headers['user-agent']
    });
  }

  async enforceAccessControl(userId, patientId, permission) {
    const userRole = await User.getRoleForPatient(userId, patientId);
    const allowedPermissions = this.getPermissionsForRole(userRole);

    if (!allowedPermissions.includes(permission)) {
      throw new Error(`User ${userId} not authorized for ${permission}`);
    }
  }
}
```

### 6. End-to-End Encryption for Data in Transit

**Implementation**:

```javascript
class E2EEncryptionMiddleware {
  async decryptRequest(req, res, next) {
    if (req.headers['x-encrypted'] === 'true') {
      try {
        const decrypted = await this.decryptPayload(req.body);
        req.body = decrypted;
        req.encrypted = true;
      } catch (error) {
        return res.status(400).json({ error: 'Decryption failed' });
      }
    }
    next();
  }

  async encryptResponse(req, res, next) {
    if (req.encrypted) {
      const originalJson = res.json.bind(res);
      res.json = function(data) {
        const encrypted = encryptionService.encryptResponse(data);
        res.set('X-Encrypted', 'true');
        return originalJson({ encrypted });
      };
    }
    next();
  }

  async decryptPayload(payload) {
    return encryptionService.decrypt(payload.encrypted);
  }
}
```

---

## Performance Optimization

### 7. Response Caching Strategy

**Pattern**: Cache immutable health data while respecting privacy.

**Implementation**:

```javascript
class HealthcareResponseCache {
  async getCachedResource(resourceType, id, options = {}) {
    const cacheKey = `${resourceType}:${id}`;
    const cached = await redis.get(cacheKey);

    if (cached && !options.bypass) {
      return JSON.parse(cached);
    }

    const resource = await this.fetchResource(resourceType, id);

    // Determine cache TTL based on data type
    const ttl = this.getTTLForResourceType(resourceType);
    await redis.setex(cacheKey, ttl, JSON.stringify(resource));

    return resource;
  }

  getTTLForResourceType(resourceType) {
    const ttls = {
      'Patient': 3600,        // 1 hour - patient demographics rarely change
      'Observation': 300,     // 5 minutes - vital signs can change rapidly
      'MedicationStatement': 7200, // 2 hours - medications stable
      'Condition': 86400      // 24 hours - conditions stable
    };
    return ttls[resourceType] || 600;
  }

  invalidateCache(resourceType, id) {
    return redis.del(`${resourceType}:${id}`);
  }
}
```

---

## Error Handling & Resilience

### 8. Circuit Breaker for External Healthcare Systems

**Implementation**:

```javascript
class HealthcareCircuitBreaker {
  constructor(options = {}) {
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.failureCount = 0;
    this.lastFailureTime = null;
  }

  async execute(fn, fallback) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.resetTimeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();

      if (fallback) {
        return fallback();
      }
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
    }
  }
}
```

---

## Real-World Examples

### Example 1: Patient Admission Workflow

```javascript
async function admitPatient(patientData, admissionDetails) {
  // 1. Create/update patient resource
  const patient = await fhirAPI.createResource('Patient', patientData);

  // 2. Publish admission event
  await eventBus.publishHealthEvent('patient.admitted', {
    patientId: patient.id,
    admissionId: admissionDetails.id,
    timestamp: new Date()
  });

  // 3. Trigger downstream workflows
  await eventBus.consumeHealthEvents('patient.admitted', async (event) => {
    // Send to EHR
    // Create bed assignment
    // Schedule initial labs
    // Notify nursing unit
  });

  // 4. Return admission confirmation
  return {
    patientId: patient.id,
    admissionId: admissionDetails.id,
    resourceUrl: `/Patient/${patient.id}`
  };
}
```

### Example 2: Real-time Lab Result Distribution

```javascript
async function processLabResult(labOrder, result) {
  // Encrypt PHI
  const encrypted = await dataHandler.encryptPHI(
    JSON.stringify(result),
    labOrder.patientId
  );

  // Publish event
  const eventId = await eventBus.publishHealthEvent('lab-result.available', {
    patientId: labOrder.patientId,
    labOrderId: labOrder.id,
    result: encrypted,
    timestamp: new Date()
  });

  // Audit log
  await dataHandler.logDataAccess(
    process.env.LAB_SERVICE,
    labOrder.patientId,
    'CREATE_OBSERVATION',
    true
  );

  return eventId;
}
```

---

## Summary

This pattern guide provides production-grade approaches for:
- Building FHIR-compliant APIs
- Implementing secure async messaging
- Maintaining HIPAA compliance
- Optimizing performance
- Ensuring resilience

All patterns prioritize security, auditability, and interoperability essential for healthcare systems.

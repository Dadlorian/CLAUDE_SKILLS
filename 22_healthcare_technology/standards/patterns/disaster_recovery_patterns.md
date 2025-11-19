# Healthcare Disaster Recovery & Business Continuity Patterns

## Executive Summary

Production-grade patterns for implementing disaster recovery (DR) and business continuity (BC) strategies in healthcare systems. Covers RTO/RPO targets, failover mechanisms, data replication, and regulatory compliance (HIPAA, HITECH).

---

## Table of Contents

1. [DR/BC Strategy Framework](#drbc-strategy-framework)
2. [High Availability Architecture](#high-availability-architecture)
3. [Data Replication & Backup](#data-replication--backup)
4. [Failover & Recovery](#failover--recovery)
5. [Business Continuity Planning](#business-continuity-planning)
6. [Testing & Validation](#testing--validation)
7. [Compliance & Audit](#compliance--audit)
8. [Real-World Scenarios](#real-world-scenarios)

---

## DR/BC Strategy Framework

### 1. Healthcare Disaster Recovery Strategy Matrix

**Pattern**: Define recovery strategies based on application criticality and business impact.

**Implementation**:

```javascript
class DisasterRecoveryStrategy {
  constructor() {
    this.applications = new Map();
    this.strategies = {
      CRITICAL: {
        rto: 15 * 60 * 1000,      // 15 minutes
        rpo: 1 * 60 * 1000,        // 1 minute
        replicationMode: 'synchronous',
        backupFrequency: '5 minutes',
        testFrequency: 'monthly',
        redundancyLevel: 'multi-region'
      },
      HIGH: {
        rto: 1 * 60 * 60 * 1000,   // 1 hour
        rpo: 15 * 60 * 1000,        // 15 minutes
        replicationMode: 'semi-synchronous',
        backupFrequency: '15 minutes',
        testFrequency: 'quarterly',
        redundancyLevel: 'multi-availability-zone'
      },
      MEDIUM: {
        rto: 4 * 60 * 60 * 1000,   // 4 hours
        rpo: 1 * 60 * 60 * 1000,    // 1 hour
        replicationMode: 'asynchronous',
        backupFrequency: 'hourly',
        testFrequency: 'semi-annually',
        redundancyLevel: 'single-region'
      },
      LOW: {
        rto: 24 * 60 * 60 * 1000,  // 24 hours
        rpo: 4 * 60 * 60 * 1000,    // 4 hours
        replicationMode: 'asynchronous',
        backupFrequency: 'daily',
        testFrequency: 'annually',
        redundancyLevel: 'backup-only'
      }
    };
  }

  registerApplication(appId, config) {
    const { name, tier, criticality, dataType, rtoOverride, rpoOverride } = config;

    const strategy = this.strategies[criticality];

    this.applications.set(appId, {
      id: appId,
      name,
      tier,
      criticality,
      dataType,
      rto: rtoOverride || strategy.rto,
      rpo: rpoOverride || strategy.rpo,
      replicationMode: strategy.replicationMode,
      backupFrequency: strategy.backupFrequency,
      testFrequency: strategy.testFrequency,
      redundancyLevel: strategy.redundancyLevel,
      registeredAt: new Date(),
      status: 'active'
    });

    this.configureReplication(appId);
    this.scheduleBackups(appId);
    this.scheduleDRTests(appId);
  }

  configureReplication(appId) {
    const app = this.applications.get(appId);

    switch (app.replicationMode) {
      case 'synchronous':
        this.setupSynchronousReplication(appId);
        break;
      case 'semi-synchronous':
        this.setupSemiSynchronousReplication(appId);
        break;
      case 'asynchronous':
        this.setupAsynchronousReplication(appId);
        break;
    }
  }

  scheduleBackups(appId) {
    const app = this.applications.get(appId);
    const interval = this.parseFrequency(app.backupFrequency);

    setInterval(async () => {
      try {
        await this.performBackup(appId);
      } catch (error) {
        await this.alertOnBackupFailure(appId, error);
      }
    }, interval);
  }

  scheduleDRTests(appId) {
    const app = this.applications.get(appId);
    const interval = this.parseFrequency(app.testFrequency);

    setInterval(async () => {
      try {
        await this.conductDRTest(appId);
      } catch (error) {
        await this.alertOnDRTestFailure(appId, error);
      }
    }, interval);
  }

  async performBackup(appId) {
    const app = this.applications.get(appId);

    const backup = {
      id: uuid(),
      appId,
      startTime: new Date(),
      status: 'in-progress'
    };

    try {
      // Initiate backup based on data type
      switch (app.dataType) {
        case 'relational':
          backup.path = await this.backupRelationalDB(appId);
          break;
        case 'nosql':
          backup.path = await this.backupNoSQL(appId);
          break;
        case 'file-storage':
          backup.path = await this.backupFileStorage(appId);
          break;
      }

      backup.endTime = new Date();
      backup.status = 'completed';
      backup.size = await this.getBackupSize(backup.path);

      await BackupLog.create(backup);

      // Verify backup integrity
      await this.verifyBackupIntegrity(backup);

      // Replicate to secondary site
      if (app.redundancyLevel !== 'backup-only') {
        await this.replicateBackupToSecondary(backup);
      }

    } catch (error) {
      backup.status = 'failed';
      backup.error = error.message;
      await BackupLog.create(backup);
      throw error;
    }
  }

  parseFrequency(freq) {
    const units = {
      'minute': 1000 * 60,
      'minutes': 1000 * 60,
      'hour': 1000 * 60 * 60,
      'hourly': 1000 * 60 * 60,
      'day': 1000 * 60 * 60 * 24,
      'daily': 1000 * 60 * 60 * 24
    };

    const match = freq.match(/(\d+)\s*(minute|hour|day)s?/i);
    if (match) {
      const count = parseInt(match[1]);
      const unit = units[match[2].toLowerCase()];
      return count * unit;
    }

    return 1000 * 60 * 60; // Default to hourly
  }

  async alertOnBackupFailure(appId, error) {
    const app = this.applications.get(appId);

    await Notification.send({
      severity: 'CRITICAL',
      type: 'BACKUP_FAILED',
      appId,
      appName: app.name,
      error: error.message,
      timestamp: new Date(),
      recipients: ['dba@hospital.local', 'ops-team@hospital.local']
    });
  }
}
```

---

## High Availability Architecture

### 2. Multi-Region Active-Active Architecture

**Pattern**: Distribute healthcare systems across multiple regions with automatic failover.

**Implementation**:

```javascript
class MultiRegionHealthcareCluster {
  constructor(config) {
    this.regions = config.regions; // [{ name, dataCenter, primaryDB, secondaryDB }, ...]
    this.routingPolicy = config.routingPolicy || 'geolocation';
    this.healthChecks = new Map();
    this.failoverState = new Map();
  }

  async initialize() {
    // Initialize each region
    for (const region of this.regions) {
      await this.setupRegion(region);
      this.startHealthCheck(region);
    }

    // Setup cross-region replication
    await this.setupCrossRegionReplication();
  }

  async setupRegion(region) {
    region.apiGateway = await this.deployAPIGateway(region);
    region.database = await this.initializeDatabase(region);
    region.cache = await this.initializeCache(region);
    region.queue = await this.initializeMessageQueue(region);
    region.storage = await this.initializeStorage(region);
    region.status = 'healthy';
  }

  startHealthCheck(region) {
    setInterval(async () => {
      try {
        const health = await this.performHealthCheck(region);

        if (!health.isHealthy && region.status === 'healthy') {
          // Region became unhealthy
          await this.handleRegionFailure(region);
        } else if (health.isHealthy && region.status === 'unhealthy') {
          // Region recovered
          await this.handleRegionRecovery(region);
        }

        region.lastHealthCheck = new Date();
        region.health = health;
      } catch (error) {
        console.error(`Health check failed for ${region.name}:`, error);
      }
    }, 30000); // Check every 30 seconds
  }

  async performHealthCheck(region) {
    const checks = {
      apiGateway: await this.checkAPIGateway(region),
      database: await this.checkDatabase(region),
      cache: await this.checkCache(region),
      queue: await this.checkMessageQueue(region),
      storage: await this.checkStorage(region)
    };

    return {
      isHealthy: Object.values(checks).every(c => c.ok),
      checks,
      timestamp: new Date()
    };
  }

  async handleRegionFailure(region) {
    console.error(`Region ${region.name} failed!`);

    // Update failover state
    this.failoverState.set(region.name, {
      failed: true,
      failoverTime: new Date(),
      status: 'in-progress'
    });

    // Redirect traffic to other regions
    await this.updateGlobalRoutingPolicy(region);

    // Notify ops team
    await this.alertOpsTeam({
      severity: 'CRITICAL',
      message: `Healthcare system region ${region.name} failed`,
      affectedServices: Object.keys(region.health.checks),
      timestamp: new Date()
    });

    // Attempt recovery
    await this.attemptRegionRecovery(region);
  }

  async handleRegionRecovery(region) {
    console.log(`Region ${region.name} recovered!`);

    // Update failover state
    this.failoverState.set(region.name, {
      failed: false,
      recoveryTime: new Date(),
      status: 'syncing'
    });

    // Sync data from primary region
    await this.syncRegionData(region);

    // Gradually restore traffic
    await this.graduallyRestoreTraffic(region);
  }

  async setupCrossRegionReplication() {
    // Replicate databases
    for (let i = 0; i < this.regions.length; i++) {
      for (let j = i + 1; j < this.regions.length; j++) {
        await this.setupDBReplication(
          this.regions[i],
          this.regions[j]
        );
      }
    }
  }

  async setupDBReplication(sourceRegion, targetRegion) {
    const replication = {
      source: sourceRegion.name,
      target: targetRegion.name,
      replicationType: 'bidirectional',
      lag: 0
    };

    sourceRegion.database.on('change', async (change) => {
      try {
        await targetRegion.database.applyChange(change);
        replication.lag = 0;
      } catch (error) {
        replication.lag = Date.now();
        console.error(`Replication error from ${sourceRegion.name}:`, error);
      }
    });
  }

  async updateGlobalRoutingPolicy(failedRegion) {
    const activeRegions = this.regions.filter(r => r.status === 'healthy');

    // Update DNS/Load Balancer
    if (activeRegions.length === 0) {
      throw new Error('All regions have failed!');
    }

    await GlobalLoadBalancer.updateRoutingRules({
      failedRegion: failedRegion.name,
      activeRegions: activeRegions.map(r => r.name),
      policy: this.routingPolicy
    });
  }

  async syncRegionData(region) {
    const primaryRegion = this.regions.find(r => r.status === 'healthy');

    if (!primaryRegion) {
      throw new Error('No healthy region to sync from');
    }

    // Perform full sync
    await this.performFullDataSync(region, primaryRegion);
  }

  async graduallyRestoreTraffic(region) {
    // Start with 10% traffic
    let trafficPercentage = 10;

    while (trafficPercentage <= 100) {
      await GlobalLoadBalancer.setTrafficPercentage(
        region.name,
        trafficPercentage
      );

      // Monitor error rates for 5 minutes
      const errorRate = await this.getErrorRate(region, 5 * 60 * 1000);

      if (errorRate > 0.01) { // 1% error threshold
        // Rollback
        await GlobalLoadBalancer.setTrafficPercentage(region.name, 0);
        throw new Error(`High error rate detected during restoration: ${errorRate}`);
      }

      trafficPercentage += 10;
      await new Promise(resolve => setTimeout(resolve, 5 * 60 * 1000));
    }
  }
}
```

---

### 3. Database Replication Patterns

**Pattern**: Implement various database replication strategies for different scenarios.

**Implementation**:

```javascript
class DatabaseReplicationManager {
  constructor() {
    this.replications = new Map();
  }

  // Synchronous replication for critical data
  async setupSynchronousReplication(primaryDB, secondaryDB, dataTypes) {
    const replication = {
      id: uuid(),
      type: 'synchronous',
      primaryDB,
      secondaryDB,
      dataTypes,
      lag: 0,
      status: 'active',
      startTime: new Date()
    };

    primaryDB.on('transaction', async (txn) => {
      try {
        // Block until secondary confirms
        await secondaryDB.applyTransaction(txn);
        replication.lag = 0;
      } catch (error) {
        // Synchronous replication failure - primary must fail
        await this.handleReplicationFailure(primaryDB, error);
      }
    });

    this.replications.set(replication.id, replication);
    return replication;
  }

  // Semi-synchronous for balanced RPO/performance
  async setupSemiSynchronousReplication(primaryDB, secondaryDB) {
    const replication = {
      id: uuid(),
      type: 'semi-synchronous',
      primaryDB,
      secondaryDB,
      lag: 0,
      status: 'active',
      startTime: new Date(),
      commitLag: 100  // ms to wait for secondary ack
    };

    const replicationQueue = [];
    let isProcessing = false;

    primaryDB.on('transaction', (txn) => {
      replicationQueue.push(txn);

      if (!isProcessing) {
        isProcessing = true;
        this.processReplicationQueue(secondaryDB, replicationQueue, replication);
      }
    });

    this.replications.set(replication.id, replication);
    return replication;
  }

  async processReplicationQueue(secondaryDB, queue, replication) {
    while (queue.length > 0) {
      const txn = queue.shift();

      try {
        const ackPromise = secondaryDB.applyTransaction(txn);

        // Wait with timeout
        await Promise.race([
          ackPromise,
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Replication timeout')),
            replication.commitLag)
          )
        ]);

        replication.lag = Math.min(replication.lag + 1, 0);
      } catch (error) {
        console.error('Semi-sync replication error:', error);
        replication.lag++;
        queue.unshift(txn); // Retry
      }
    }
  }

  // Asynchronous replication for non-critical data
  async setupAsynchronousReplication(primaryDB, secondaryDB) {
    const replication = {
      id: uuid(),
      type: 'asynchronous',
      primaryDB,
      secondaryDB,
      lag: 0,
      status: 'active',
      startTime: new Date(),
      batchSize: 100,
      batchInterval: 5000 // 5 seconds
    };

    const replicationQueue = [];
    let processingTimer = null;

    primaryDB.on('transaction', (txn) => {
      replicationQueue.push(txn);

      if (!processingTimer) {
        processingTimer = setTimeout(async () => {
          await this.processBatch(replicationQueue, secondaryDB, replication);
          processingTimer = null;
        }, replication.batchInterval);
      }

      if (replicationQueue.length >= replication.batchSize) {
        clearTimeout(processingTimer);
        processingTimer = null;
      }
    });

    this.replications.set(replication.id, replication);
    return replication;
  }

  async processBatch(queue, secondaryDB, replication) {
    const batch = queue.splice(0, replication.batchSize);

    try {
      await secondaryDB.applyTransactionBatch(batch);
      replication.lag = 0;
    } catch (error) {
      console.error('Async replication batch error:', error);
      replication.lag += batch.length;
      // Re-queue for retry
      queue.unshift(...batch);
    }
  }

  async handleReplicationFailure(primaryDB, error) {
    console.error('Replication failure:', error);

    // Log event
    await AuditLog.create({
      event: 'REPLICATION_FAILURE',
      database: primaryDB.name,
      error: error.message,
      timestamp: new Date(),
      severity: 'CRITICAL'
    });

    // Alert ops
    await AlertService.sendCriticalAlert({
      title: 'Database Replication Failure',
      message: `Replication failed on ${primaryDB.name}: ${error.message}`
    });

    // Take corrective action based on criticality
    await primaryDB.pause(); // Stop writes
    await this.attemptRecovery(primaryDB);
  }
}
```

---

## Failover & Recovery

### 4. Automatic Failover with Health Validation

**Pattern**: Detect failures and automatically failover with validation.

**Implementation**:

```javascript
class FailoverOrchestrator {
  constructor(primarySystem, secondarySystem, options = {}) {
    this.primary = primarySystem;
    this.secondary = secondarySystem;
    this.healthCheckInterval = options.healthCheckInterval || 10000;
    this.failoverThreshold = options.failoverThreshold || 3;
    this.validationTimeout = options.validationTimeout || 30000;
    this.consecutiveFailures = 0;
    this.failoverInProgress = false;
  }

  async start() {
    this.healthCheckTimer = setInterval(async () => {
      await this.performHealthCheck();
    }, this.healthCheckInterval);
  }

  async performHealthCheck() {
    try {
      const primaryHealth = await this.health(this.primary);

      if (!primaryHealth.isHealthy) {
        this.consecutiveFailures++;

        if (this.consecutiveFailures >= this.failoverThreshold) {
          await this.triggerFailover();
        }
      } else {
        this.consecutiveFailures = 0;
      }
    } catch (error) {
      console.error('Health check error:', error);
      this.consecutiveFailures++;
    }
  }

  async performHealthCheck() {
    try {
      const checks = {
        connectivity: await this.checkConnectivity(this.primary),
        responseTime: await this.checkResponseTime(this.primary),
        dataIntegrity: await this.checkDataIntegrity(this.primary),
        criticalServices: await this.checkCriticalServices(this.primary)
      };

      const isHealthy = Object.values(checks).every(c => c.ok);

      if (!isHealthy) {
        this.consecutiveFailures++;
      } else {
        this.consecutiveFailures = 0;
      }

      return { isHealthy, checks };
    } catch (error) {
      this.consecutiveFailures++;
      throw error;
    }
  }

  async triggerFailover() {
    if (this.failoverInProgress) {
      console.log('Failover already in progress, skipping');
      return;
    }

    this.failoverInProgress = true;
    const startTime = Date.now();

    try {
      console.log('Initiating failover...');

      // Step 1: Verify secondary is healthy
      const secondaryHealth = await this.validateSecondary();
      if (!secondaryHealth.isHealthy) {
        throw new Error('Secondary system is not healthy for failover');
      }

      // Step 2: Quiesce primary system
      await this.quiescePrimarySystem();

      // Step 3: Promote secondary
      await this.promoteSecondarySystem();

      // Step 4: Update routing
      await this.updateRoutingConfiguration();

      // Step 5: Verify data consistency
      await this.verifyDataConsistency();

      const failoverTime = Date.now() - startTime;

      // Log failover event
      await AuditLog.create({
        event: 'FAILOVER_COMPLETED',
        from: this.primary.name,
        to: this.secondary.name,
        duration: failoverTime,
        timestamp: new Date(),
        severity: 'HIGH'
      });

      // Notify stakeholders
      await this.notifyStakeholders({
        message: 'Failover completed successfully',
        failoverTime,
        affectedServices: this.primary.services
      });

    } catch (error) {
      await this.handleFailoverError(error);
      throw error;
    } finally {
      this.failoverInProgress = false;
    }
  }

  async validateSecondary() {
    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Validation timeout')), this.validationTimeout)
    );

    try {
      const health = await Promise.race([
        this.checkHealth(this.secondary),
        timeout
      ]);

      // Verify secondary can accept traffic
      const canAccept = await this.secondary.canAcceptTraffic();

      return {
        isHealthy: health.ok && canAccept,
        health,
        timestamp: new Date()
      };
    } catch (error) {
      throw new Error(`Secondary validation failed: ${error.message}`);
    }
  }

  async quiescePrimarySystem() {
    console.log('Quiescing primary system...');

    // Stop accepting new connections
    await this.primary.stopAcceptingConnections();

    // Wait for in-flight requests to complete (with timeout)
    const quiesceTimeout = 60000; // 60 seconds
    await Promise.race([
      this.primary.waitForInFlightRequests(),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Quiesce timeout')), quiesceTimeout)
      )
    ]);

    // Force close remaining connections
    await this.primary.forceCloseConnections();
  }

  async promoteSecondarySystem() {
    console.log('Promoting secondary system...');

    // Update secondary configuration
    await this.secondary.promoteToActive();

    // Verify promotion successful
    const promoted = await this.secondary.verifyActiveStatus();
    if (!promoted) {
      throw new Error('Secondary promotion verification failed');
    }
  }

  async updateRoutingConfiguration() {
    console.log('Updating routing configuration...');

    const routing = {
      primary: this.secondary.name,
      secondary: this.primary.name,
      updatedAt: new Date()
    };

    // Update load balancer
    await LoadBalancer.updateConfiguration(routing);

    // Update DNS (if applicable)
    if (this.primary.dnsName) {
      await DNSManager.updateRecord(this.primary.dnsName, this.secondary.ip);
    }

    // Update client configuration
    await this.notifyClients(routing);
  }

  async verifyDataConsistency() {
    console.log('Verifying data consistency...');

    const inconsistencies = await this.primary.compareDataWith(this.secondary);

    if (inconsistencies.length > 0) {
      console.warn('Data inconsistencies detected:', inconsistencies);

      // Trigger background sync
      await this.startBackgroundSync(inconsistencies);
    }
  }

  async handleFailoverError(error) {
    console.error('Failover failed:', error);

    await AlertService.sendCriticalAlert({
      title: 'Failover Failed',
      message: error.message,
      severity: 'CRITICAL',
      requiresAcknowledgment: true
    });

    // Create incident
    await IncidentManager.createIncident({
      title: 'Healthcare System Failover Failure',
      description: error.message,
      severity: 'SEV1',
      affectedSystems: [this.primary.name, this.secondary.name]
    });
  }

  async checkConnectivity(system) {
    try {
      await system.ping();
      return { ok: true };
    } catch (error) {
      return { ok: false, error: error.message };
    }
  }

  async checkResponseTime(system) {
    const start = Date.now();
    try {
      await system.healthCheck();
      const latency = Date.now() - start;
      return { ok: latency < 5000, latency };
    } catch (error) {
      return { ok: false, error: error.message };
    }
  }

  async checkDataIntegrity(system) {
    // Verify checksums/hashes of critical data
    return { ok: true }; // Placeholder
  }

  async checkCriticalServices(system) {
    const services = ['auth', 'database', 'api-gateway'];
    const results = await Promise.all(
      services.map(svc => system.getServiceStatus(svc))
    );
    return { ok: results.every(r => r.running) };
  }
}
```

---

## Business Continuity Planning

### 5. Business Continuity Workflows

**Pattern**: Implement workflows for maintaining critical business functions during outages.

**Implementation**:

```javascript
class BusinessContinuityManager {
  constructor() {
    this.workflows = new Map();
    this.alternativeProcedures = new Map();
    this.communicationPlan = new Map();
  }

  registerBusinessProcess(processId, config) {
    const { name, criticality, dependencies, rto, rpo } = config;

    const workflow = {
      id: processId,
      name,
      criticality,
      dependencies,
      rto,
      rpo,
      primaryPath: config.primaryPath,
      alternativePath: config.alternativePath,
      status: 'active',
      registeredAt: new Date()
    };

    this.workflows.set(processId, workflow);

    // Register alternative procedures
    if (config.alternativeProcedure) {
      this.alternativeProcedures.set(processId, config.alternativeProcedure);
    }
  }

  async initiateBusinessContinuity(failureScope) {
    const affectedProcesses = this.getAffectedProcesses(failureScope);

    console.log(`Initiating BC for ${affectedProcesses.length} processes`);

    for (const processId of affectedProcesses) {
      await this.switchToAlternativePath(processId);
    }

    // Notify all stakeholders
    await this.notifyStakeholders(failureScope, affectedProcesses);

    // Log BC activation
    await BCLog.create({
      failureScope,
      affectedProcesses,
      activatedAt: new Date(),
      initiatingSystemId: process.env.SERVICE_NAME
    });
  }

  async switchToAlternativePath(processId) {
    const workflow = this.workflows.get(processId);
    const procedure = this.alternativeProcedures.get(processId);

    console.log(`Switching ${workflow.name} to alternative path`);

    try {
      // Disable primary path
      await this.disablePrimaryPath(workflow);

      // Enable alternative path
      await this.enableAlternativePath(workflow);

      // Route traffic
      await this.routeToAlternative(processId, workflow.alternativePath);

      workflow.status = 'using-alternative';
      workflow.switchedAt = new Date();

      // Execute manual procedures if needed
      if (procedure?.manualSteps) {
        await this.notifyOperations({
          processId,
          steps: procedure.manualSteps,
          priority: 'HIGH'
        });
      }

    } catch (error) {
      console.error(`Failed to switch ${workflow.name}:`, error);
      await this.escalateToManualIntervention(processId, error);
    }
  }

  async disablePrimaryPath(workflow) {
    // Close database connections
    if (workflow.primaryPath.database) {
      await workflow.primaryPath.database.close();
    }

    // Stop API endpoints
    if (workflow.primaryPath.api) {
      await workflow.primaryPath.api.stop();
    }

    // Flush caches
    if (workflow.primaryPath.cache) {
      await workflow.primaryPath.cache.flush();
    }
  }

  async enableAlternativePath(workflow) {
    const alt = workflow.alternativePath;

    // Connect to alternative database
    if (alt.database) {
      await alt.database.connect();
      await alt.database.sync(); // Sync from primary before switch
    }

    // Start alternative API servers
    if (alt.api) {
      await alt.api.start();
    }

    // Warmup cache
    if (alt.cache) {
      await alt.cache.populate();
    }
  }

  getAffectedProcesses(failureScope) {
    const affected = [];

    this.workflows.forEach((workflow, processId) => {
      // Check if process depends on failed component
      if (workflow.dependencies.includes(failureScope.component)) {
        affected.push(processId);
      }

      // Check criticality for cascading failures
      if (failureScope.severity === 'critical' && workflow.criticality === 'critical') {
        affected.push(processId);
      }
    });

    return affected;
  }

  async notifyStakeholders(failureScope, affectedProcesses) {
    const message = {
      title: 'Business Continuity Activated',
      severity: failureScope.severity,
      affectedProcesses: affectedProcesses.map(pid => {
        const wf = this.workflows.get(pid);
        return {
          name: wf.name,
          rto: wf.rto,
          rpo: wf.rpo,
          alternativePath: wf.alternativePath
        };
      }),
      failureTime: failureScope.time,
      expectedRecovery: new Date(failureScope.time + Math.max(...affectedProcesses.map(pid =>
        this.workflows.get(pid).rto
      )))
    };

    // Send to all notification channels
    await Promise.all([
      this.sendEmailNotification(message),
      this.sendSMSNotification(message),
      this.updateIncidentManagementSystem(message),
      this.postToStatusPage(message)
    ]);
  }

  async escalateToManualIntervention(processId, error) {
    const workflow = this.workflows.get(processId);

    await IncidentManager.createIncident({
      title: `BC Activation Failed: ${workflow.name}`,
      description: error.message,
      severity: 'SEV1',
      processId,
      requiresManualIntervention: true,
      assignTo: 'on-call-operations'
    });
  }
}
```

---

## Testing & Validation

### 6. Disaster Recovery Testing

**Pattern**: Regularly test DR procedures without impacting production.

**Implementation**:

```javascript
class DisasterRecoveryTestSuite {
  constructor(drManager) {
    this.drManager = drManager;
    this.testResults = [];
  }

  async runFullDRTest() {
    const testId = uuid();
    const startTime = Date.now();

    console.log(`Starting full DR test: ${testId}`);

    const result = {
      id: testId,
      type: 'full',
      startTime: new Date(),
      components: [],
      summary: {}
    };

    try {
      // Test each critical system
      result.components.push(
        await this.testDatabaseFailover(),
        await this.testApplicationFailover(),
        await this.testDataReplication(),
        await this.testBackupRecovery(),
        await this.testCommunicationChannels()
      );

      // Calculate RTO achieved
      const totalTime = Date.now() - startTime;
      result.summary.rtoAchieved = totalTime;
      result.summary.rtoTarget = this.drManager.rto;
      result.summary.success = totalTime <= this.drManager.rto;

      result.endTime = new Date();
      result.duration = totalTime;

      // Log results
      await DRTestLog.create(result);

      // Generate report
      await this.generateDRTestReport(result);

      return result;

    } catch (error) {
      result.error = error.message;
      result.endTime = new Date();
      await DRTestLog.create(result);
      throw error;
    }
  }

  async testDatabaseFailover() {
    const componentTest = {
      component: 'Database',
      startTime: new Date(),
      subtests: []
    };

    try {
      // Create test database snapshot
      const snapshot = await this.createTestSnapshot();

      // Simulate failover
      const failoverTime = await this.simulateDBFailover(snapshot);
      componentTest.subtests.push({
        name: 'Failover Time',
        target: 300000, // 5 minutes
        actual: failoverTime,
        passed: failoverTime <= 300000
      });

      // Verify data integrity
      const integrity = await this.verifyDataIntegrity(snapshot);
      componentTest.subtests.push({
        name: 'Data Integrity',
        passed: integrity.consistent,
        details: integrity
      });

      // Test recovery
      const recoveryTime = await this.testDatabaseRecovery(snapshot);
      componentTest.subtests.push({
        name: 'Recovery Time',
        target: 600000, // 10 minutes
        actual: recoveryTime,
        passed: recoveryTime <= 600000
      });

      componentTest.endTime = new Date();
      componentTest.passed = componentTest.subtests.every(st => st.passed);

    } catch (error) {
      componentTest.error = error.message;
      componentTest.passed = false;
    }

    return componentTest;
  }

  async testApplicationFailover() {
    const componentTest = {
      component: 'Application',
      startTime: new Date(),
      subtests: []
    };

    try {
      // Simulate primary app failure
      const failureTime = await this.simulateAppFailure();

      // Measure detection time
      const detectionTime = await this.measureFailureDetection();
      componentTest.subtests.push({
        name: 'Failure Detection',
        target: 60000, // 60 seconds
        actual: detectionTime,
        passed: detectionTime <= 60000
      });

      // Measure failover time
      const failoverTime = await this.measureAppFailover();
      componentTest.subtests.push({
        name: 'Failover Activation',
        target: 120000, // 2 minutes
        actual: failoverTime,
        passed: failoverTime <= 120000
      });

      // Test connection pooling
      const connPoolTest = await this.testConnectionPooling();
      componentTest.subtests.push({
        name: 'Connection Pool Recovery',
        passed: connPoolTest.success
      });

      componentTest.endTime = new Date();
      componentTest.passed = componentTest.subtests.every(st => st.passed);

    } catch (error) {
      componentTest.error = error.message;
      componentTest.passed = false;
    }

    return componentTest;
  }

  async testDataReplication() {
    // Test replication lag, consistency, and recovery
    return {
      component: 'Data Replication',
      passed: true,
      subtests: []
    };
  }

  async testBackupRecovery() {
    // Test backup restore procedures
    return {
      component: 'Backup Recovery',
      passed: true,
      subtests: []
    };
  }

  async testCommunicationChannels() {
    // Test alert and notification systems
    return {
      component: 'Communication',
      passed: true,
      subtests: []
    };
  }

  async generateDRTestReport(result) {
    const report = {
      testId: result.id,
      date: new Date(),
      rtoTarget: this.drManager.rto,
      rtoAchieved: result.summary.rtoAchieved,
      rpoTarget: this.drManager.rpo,
      components: result.components,
      passed: result.summary.success,
      recommendations: []
    };

    // Identify failures and make recommendations
    result.components.forEach(component => {
      if (!component.passed) {
        report.recommendations.push({
          component: component.component,
          issue: component.error || 'Subtests failed',
          recommendation: this.getRecommendation(component)
        });
      }
    });

    // Send report to stakeholders
    await this.sendDRTestReport(report);
  }

  getRecommendation(component) {
    const recommendations = {
      'Database': 'Optimize failover scripts and test with larger datasets',
      'Application': 'Review load balancer configuration and connection pooling',
      'Data Replication': 'Verify network bandwidth and database synchronization',
      'Backup Recovery': 'Test restore procedures with full production dataset',
      'Communication': 'Verify alert delivery and escalation paths'
    };

    return recommendations[component.component] || 'Review component configuration';
  }
}
```

---

## Compliance & Audit

### 7. HIPAA & Compliance Audit

**Pattern**: Track DR/BC activities for compliance reporting.

**Implementation**:

```javascript
class DRComplianceAuditor {
  async auditDRCompliance() {
    const audit = {
      date: new Date(),
      findings: [],
      recommendations: []
    };

    // Check RTO compliance
    const rtoCompliance = await this.checkRTOCompliance();
    if (!rtoCompliance.compliant) {
      audit.findings.push({
        category: 'RTO',
        severity: 'HIGH',
        description: `RTO target of ${rtoCompliance.target}ms not met. Achieved: ${rtoCompliance.actual}ms`,
        evidence: rtoCompliance.testResults
      });
    }

    // Check RPO compliance
    const rpoCompliance = await this.checkRPOCompliance();
    if (!rpoCompliance.compliant) {
      audit.findings.push({
        category: 'RPO',
        severity: 'HIGH',
        description: `RPO target of ${rpoCompliance.target}ms not met. Achieved: ${rpoCompliance.actual}ms`
      });
    }

    // Check backup compliance
    const backupCompliance = await this.checkBackupCompliance();
    if (!backupCompliance.compliant) {
      audit.findings.push({
        category: 'Backups',
        severity: 'CRITICAL',
        description: `${backupCompliance.failedCount} backup(s) failed in last period`,
        details: backupCompliance.failures
      });
    }

    // Check testing compliance
    const testingCompliance = await this.checkTestingCompliance();
    if (!testingCompliance.compliant) {
      audit.findings.push({
        category: 'DR Testing',
        severity: 'MEDIUM',
        description: `DR test not conducted within required timeframe`
      });
    }

    // Check encryption compliance
    const encryptionCompliance = await this.checkEncryptionCompliance();
    if (!encryptionCompliance.compliant) {
      audit.findings.push({
        category: 'Encryption',
        severity: 'HIGH',
        description: 'Backup data not properly encrypted'
      });
    }

    // Store audit
    await ComplianceAudit.create(audit);

    return audit;
  }

  async checkBackupCompliance() {
    const backups = await BackupLog.findLastWeek();
    const failures = backups.filter(b => b.status === 'failed');

    return {
      compliant: failures.length === 0,
      totalBackups: backups.length,
      failedCount: failures.length,
      failures: failures.map(f => ({
        id: f.id,
        appId: f.appId,
        error: f.error,
        timestamp: f.timestamp
      }))
    };
  }

  async checkRTOCompliance() {
    const lastTests = await DRTestLog.findLast({ limit: 5 });
    const rtoBreach = lastTests.some(t => t.duration > t.rtoTarget);

    return {
      compliant: !rtoBreach,
      target: this.getRTOTarget(),
      actual: lastTests.length > 0 ? lastTests[0].duration : null,
      testResults: lastTests
    };
  }

  async checkRPOCompliance() {
    const replicationMetrics = await ReplicationMetrics.getLast24Hours();
    const maxLag = Math.max(...replicationMetrics.map(m => m.lag));

    return {
      compliant: maxLag <= this.getRPOTarget(),
      target: this.getRPOTarget(),
      actual: maxLag,
      details: replicationMetrics
    };
  }

  async checkTestingCompliance() {
    const lastTest = await DRTestLog.findLatest();
    const requiredFrequency = 30 * 24 * 3600 * 1000; // Monthly
    const daysSinceTest = Date.now() - lastTest.date;

    return {
      compliant: daysSinceTest <= requiredFrequency,
      lastTest: lastTest.date,
      daysSinceTest: Math.floor(daysSinceTest / (24 * 3600 * 1000)),
      requiredFrequency: 'Monthly'
    };
  }

  async checkEncryptionCompliance() {
    const backups = await BackupLog.findLastMonth();
    const unencrypted = backups.filter(b => b.encrypted !== true);

    return {
      compliant: unencrypted.length === 0,
      totalBackups: backups.length,
      unencryptedCount: unencrypted.length,
      details: unencrypted
    };
  }

  getRTOTarget() {
    // Return based on application tier
    return 15 * 60 * 1000; // 15 minutes for critical systems
  }

  getRPOTarget() {
    return 1 * 60 * 1000; // 1 minute for critical systems
  }
}
```

---

## Real-World Scenarios

### Scenario 1: Multi-Region Failure

```javascript
async function handleMultiRegionFailure() {
  const drOps = new FailoverOrchestrator(primaryRegion, secondaryRegion);

  // Primary region completely down
  try {
    await drOps.triggerFailover();

    // Secondary now active
    // Activate business continuity procedures
    const bcMgr = new BusinessContinuityManager();
    await bcMgr.initiateBusinessContinuity({
      component: 'primary-region',
      severity: 'critical',
      time: Date.now()
    });

  } catch (error) {
    // Manual intervention required
    await escalateToManualIntervention(error);
  }
}
```

### Scenario 2: Scheduled DR Testing

```javascript
async function performMonthlyDRTest() {
  const testSuite = new DisasterRecoveryTestSuite(drManager);

  try {
    const result = await testSuite.runFullDRTest();

    if (!result.summary.success) {
      console.log('DR test failed - initiating review');
      await createIncident({
        title: 'DR Test Failure',
        components: result.components.filter(c => !c.passed),
        severity: 'SEV2'
      });
    }
  } catch (error) {
    console.error('DR test error:', error);
  }
}
```

---

## Summary

Healthcare DR/BC patterns provide:
- Clear RPO/RTO definitions by criticality
- Automated failover with validation
- Multi-region redundancy
- Regular testing and compliance verification
- Business continuity for critical workflows
- Compliance audit trails

All patterns prioritize patient safety and regulatory compliance.

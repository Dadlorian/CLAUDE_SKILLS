/**
 * Real-time PHI Access Tracking Dashboard
 * WebSocket-based real-time monitoring of PHI access
 */
const EventEmitter = require('events');

class PHIAccessTracker extends EventEmitter {
  constructor() {
    super();
    this.recentAccess = [];
    this.alertThresholds = {
      massAccess: 50,
      timeWindowMinutes: 15,
      unusualHourStart: 22,
      unusualHourEnd: 6
    };
  }

  trackAccess(accessEvent) {
    // Add to recent access
    this.recentAccess.push({
      ...accessEvent,
      timestamp: new Date()
    });

    // Keep only last hour
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    this.recentAccess = this.recentAccess.filter(a => a.timestamp > oneHourAgo);

    // Check for suspicious patterns
    this.checkForAnomalies(accessEvent);

    // Emit event for real-time dashboard
    this.emit('phi-access', accessEvent);
  }

  checkForAnomalies(event) {
    const userAccesses = this.recentAccess.filter(a => a.userId === event.userId);
    const recentUserAccesses = userAccesses.filter(a => 
      new Date() - a.timestamp < this.alertThresholds.timeWindowMinutes * 60 * 1000
    );

    if (recentUserAccesses.length > this.alertThresholds.massAccess) {
      this.emit('anomaly', {
        type: 'MASS_ACCESS',
        userId: event.userId,
        count: recentUserAccesses.length,
        timeframe: `${this.alertThresholds.timeWindowMinutes} minutes`
      });
    }

    // Check unusual hours
    const hour = new Date().getHours();
    if (hour >= this.alertThresholds.unusualHourStart || hour < this.alertThresholds.unusualHourEnd) {
      this.emit('anomaly', {
        type: 'UNUSUAL_HOURS',
        userId: event.userId,
        hour: hour
      });
    }
  }

  getRealtimeStats() {
    const now = new Date();
    const last15Min = this.recentAccess.filter(a => 
      now - a.timestamp < 15 * 60 * 1000
    );

    return {
      totalAccessesLastHour: this.recentAccess.length,
      totalAccessesLast15Min: last15Min.length,
      uniqueUsersLastHour: new Set(this.recentAccess.map(a => a.userId)).size,
      topAccessedPatients: this.getTopAccessed(10),
      activeUsers: this.getActiveUsers()
    };
  }

  getTopAccessed(limit = 10) {
    const patientCounts = {};
    this.recentAccess.forEach(a => {
      if (a.patientId) {
        patientCounts[a.patientId] = (patientCounts[a.patientId] || 0) + 1;
      }
    });

    return Object.entries(patientCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([patientId, count]) => ({ patientId, count }));
  }

  getActiveUsers() {
    const userActivity = {};
    this.recentAccess.forEach(a => {
      if (!userActivity[a.userId]) {
        userActivity[a.userId] = {
          userId: a.userId,
          username: a.username,
          role: a.role,
          accessCount: 0,
          lastAccess: a.timestamp
        };
      }
      userActivity[a.userId].accessCount++;
      if (a.timestamp > userActivity[a.userId].lastAccess) {
        userActivity[a.userId].lastAccess = a.timestamp;
      }
    });

    return Object.values(userActivity);
  }
}

module.exports = PHIAccessTracker;

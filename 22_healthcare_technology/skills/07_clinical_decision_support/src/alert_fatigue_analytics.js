/**
 * Alert Fatigue Analytics
 * Tracks alert metrics and identifies problematic alerts
 */

class AlertFatigueAnalytics {
  constructor() {
    this.metrics = new Map();
  }
  
  logAlert(alertType, patientId, severity, outcome) {
    const key = alertType;
    if (!this.metrics.has(key)) {
      this.metrics.set(key, {
        fired: 0,
        overridden: 0,
        accepted: 0,
        totalResponseTime: 0,
        overrideReasons: {}
      });
    }
    
    const metric = this.metrics.get(key);
    metric.fired++;
    
    if (outcome.action === 'OVERRIDE') {
      metric.overridden++;
      const reason = outcome.reason || 'UNKNOWN';
      metric.overrideReasons[reason] = (metric.overrideReasons[reason] || 0) + 1;
    } else if (outcome.action === 'ACCEPT') {
      metric.accepted++;
    }
    
    metric.totalResponseTime += outcome.responseTimeSeconds;
  }
  
  analyzeAlertPerformance() {
    const analysis = [];
    
    for (const [alertType, metrics] of this.metrics) {
      const overrideRate = metrics.overridden / metrics.fired;
      const acceptanceRate = metrics.accepted / metrics.fired;
      const avgResponseTime = metrics.totalResponseTime / metrics.fired;
      
      const issues = [];
      
      // High override rate
      if (overrideRate > 0.5) {
        issues.push(`High override rate: ${(overrideRate * 100).toFixed(1)}%`);
      }
      
      // Low acceptance
      if (acceptanceRate < 0.3) {
        issues.push(`Low acceptance: ${(acceptanceRate * 100).toFixed(1)}%`);
      }
      
      // Slow response time
      if (avgResponseTime > 10) {
        issues.push(`Slow response: ${avgResponseTime.toFixed(1)}s average`);
      }
      
      // Check override reasons
      const topReason = this.getTopOverrideReason(metrics.overrideReasons);
      if (topReason.reason === 'NOT_APPLICABLE' && topReason.percentage > 0.6) {
        issues.push(`Poor specificity: ${(topReason.percentage * 100).toFixed(1)}% "not applicable"`);
      }
      
      if (issues.length > 0) {
        analysis.push({
          alertType,
          overrideRate,
          acceptanceRate,
          avgResponseTime,
          issues,
          recommendation: this.generateRecommendation(issues)
        });
      }
    }
    
    return analysis.sort((a, b) => b.issues.length - a.issues.length);
  }
  
  getTopOverrideReason(reasons) {
    let topReason = null;
    let topCount = 0;
    let total = 0;
    
    for (const [reason, count] of Object.entries(reasons)) {
      total += count;
      if (count > topCount) {
        topCount = count;
        topReason = reason;
      }
    }
    
    return {
      reason: topReason,
      count: topCount,
      percentage: topCount / total
    };
  }
  
  generateRecommendation(issues) {
    const recommendations = [];
    
    if (issues.some(i => i.includes('High override'))) {
      recommendations.push('Review rule logic for specificity');
    }
    if (issues.some(i => i.includes('Poor specificity'))) {
      recommendations.push('Add contextual filters to reduce false positives');
    }
    if (issues.some(i => i.includes('Slow response'))) {
      recommendations.push('Simplify alert UI or adjust severity');
    }
    
    return recommendations;
  }
}

module.exports = AlertFatigueAnalytics;

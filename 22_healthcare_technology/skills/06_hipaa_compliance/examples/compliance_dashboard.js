/**
 * Real-time HIPAA Compliance Monitoring Dashboard
 * Tracks key compliance metrics
 */
class ComplianceDashboard {
  constructor() {
    this.metrics = {
      trainingCompliance: 0,
      riskAssessmentCurrent: false,
      baaCompliance: 0,
      auditLogReview: null,
      incidentCount: 0,
      breachCount: 0,
      policyReviewDate: null
    };
  }

  updateTrainingCompliance(completed, total) {
    this.metrics.trainingCompliance = (completed / total) * 100;
  }

  markRiskAssessmentComplete(date) {
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
    
    this.metrics.riskAssessmentCurrent = new Date(date) > oneYearAgo;
  }

  updateBAACompliance(signedCount, totalCount) {
    this.metrics.baaCompliance = (signedCount / totalCount) * 100;
  }

  recordAuditReview(date) {
    this.metrics.auditLogReview = date;
  }

  recordIncident(incident) {
    this.metrics.incidentCount++;
    if (incident.isBreech) {
      this.metrics.breachCount++;
    }
  }

  getComplianceScore() {
    let score = 0;
    
    // Training compliance (25 points)
    score += (this.metrics.trainingCompliance / 100) * 25;
    
    // Risk assessment current (25 points)
    score += this.metrics.riskAssessmentCurrent ? 25 : 0;
    
    // BAA compliance (20 points)
    score += (this.metrics.baaCompliance / 100) * 20;
    
    // Audit review within 90 days (15 points)
    if (this.metrics.auditLogReview) {
      const ninetyDaysAgo = new Date();
      ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
      score += new Date(this.metrics.auditLogReview) > ninetyDaysAgo ? 15 : 0;
    }
    
    // No breaches (15 points)
    score += this.metrics.breachCount === 0 ? 15 : 0;
    
    return Math.round(score);
  }

  getComplianceStatus() {
    const score = this.getComplianceScore();
    
    if (score >= 90) return 'EXCELLENT';
    if (score >= 75) return 'GOOD';
    if (score >= 60) return 'NEEDS_IMPROVEMENT';
    return 'NON_COMPLIANT';
  }

  getDashboardData() {
    return {
      ...this.metrics,
      complianceScore: this.getComplianceScore(),
      complianceStatus: this.getComplianceStatus(),
      generatedAt: new Date().toISOString()
    };
  }
}

module.exports = ComplianceDashboard;

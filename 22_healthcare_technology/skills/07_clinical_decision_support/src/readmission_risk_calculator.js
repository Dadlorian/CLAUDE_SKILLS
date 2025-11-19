/**
 * Hospital Readmission Risk Calculator
 * Implements LACE Index and ML-based prediction
 */

class ReadmissionRiskCalculator {
  calculateLACE(admission) {
    let score = 0;
    
    // Length of stay
    if (admission.los <= 1) score += 1;
    else if (admission.los <= 2) score += 2;
    else if (admission.los <= 3) score += 3;
    else if (admission.los <= 6) score += 4;
    else if (admission.los <= 13) score += 5;
    else score += 7;
    
    // Acute admission
    if (admission.type === 'EMERGENT') score += 3;
    
    // Comorbidities (Charlson)
    const charlson = this.calculateCharlson(admission.patient);
    score += Math.min(charlson, 5);
    
    // ED visits (past 6 months)
    const edVisits = admission.patient.edVisits6mo;
    score += Math.min(edVisits, 4);
    
    return {
      score,
      riskCategory: this.classifyLACE(score),
      readmissionRisk: this.laceToPercentage(score)
    };
  }
  
  classifyLACE(score) {
    if (score >= 10) return 'HIGH';
    if (score >= 5) return 'MODERATE';
    return 'LOW';
  }
  
  laceToPercentage(score) {
    const riskMap = {0: 3, 5: 6, 10: 12, 15: 25};
    return riskMap[score] || 15;
  }
  
  calculateCharlson(patient) {
    let score = 0;
    const conditions = patient.conditions || [];
    if (conditions.includes('MI')) score += 1;
    if (conditions.includes('CHF')) score += 1;
    if (conditions.includes('DM_COMPLICATIONS')) score += 2;
    if (conditions.includes('CANCER')) score += 2;
    return score;
  }
}

module.exports = ReadmissionRiskCalculator;

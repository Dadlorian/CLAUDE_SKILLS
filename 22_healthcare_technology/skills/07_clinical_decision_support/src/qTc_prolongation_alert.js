/**
 * QTc Prolongation Risk Alert
 * Detects medications that prolong QT interval
 */

const QT_PROLONGING_DRUGS = {
  HIGH_RISK: ['azithromycin', 'clarithromycin', 'levofloxacin', 'moxifloxacin', 'haloperidol', 'methadone'],
  MODERATE_RISK: ['ondansetron', 'escitalopram', 'citalopram', 'fluconazole']
};

class QTcProlongationChecker {
  checkQTcRisk(medications, patient) {
    const qtDrugs = this.identifyQTDrugs(medications);
    
    if (qtDrugs.length === 0) {
      return null;
    }
    
    const riskFactors = this.assessRiskFactors(patient);
    const overallRisk = this.calculateOverallRisk(qtDrugs, riskFactors);
    
    return {
      qtProlongingDrugs: qtDrugs,
      riskFactors: riskFactors,
      overallRisk: overallRisk,
      recommendation: this.generateRecommendation(qtDrugs, riskFactors, overallRisk)
    };
  }
  
  identifyQTDrugs(medications) {
    const qtDrugs = [];
    
    for (const med of medications) {
      const medName = med.name.toLowerCase();
      
      if (QT_PROLONGING_DRUGS.HIGH_RISK.some(d => medName.includes(d))) {
        qtDrugs.push({ drug: med.name, risk: 'HIGH' });
      } else if (QT_PROLONGING_DRUGS.MODERATE_RISK.some(d => medName.includes(d))) {
        qtDrugs.push({ drug: med.name, risk: 'MODERATE' });
      }
    }
    
    return qtDrugs;
  }
  
  assessRiskFactors(patient) {
    const factors = [];
    
    if (patient.sex === 'F') factors.push('Female sex');
    if (patient.age > 65) factors.push('Age > 65');
    if (patient.conditions.includes('Hypokalemia')) factors.push('Hypokalemia');
    if (patient.conditions.includes('Hypomagnesemia')) factors.push('Hypomagnesemia');
    if (patient.conditions.includes('CHF')) factors.push('Heart failure');
    if (patient.conditions.includes('Bradycardia')) factors.push('Bradycardia');
    if (patient.labs?.qtc > 450) factors.push(`Baseline QTc ${patient.labs.qtc} ms`);
    
    return factors;
  }
  
  calculateOverallRisk(qtDrugs, riskFactors) {
    let risk = 'LOW';
    
    const hasHighRiskDrug = qtDrugs.some(d => d.risk === 'HIGH');
    const multipleQTDrugs = qtDrugs.length > 1;
    const hasMultipleRiskFactors = riskFactors.length >= 2;
    
    if ((hasHighRiskDrug && hasMultipleRiskFactors) || (multipleQTDrugs && riskFactors.length > 0)) {
      risk = 'HIGH';
    } else if (hasHighRiskDrug || multipleQTDrugs || hasMultipleRiskFactors) {
      risk = 'MODERATE';
    }
    
    return risk;
  }
  
  generateRecommendation(qtDrugs, riskFactors, overallRisk) {
    const recs = [];
    
    if (overallRisk === 'HIGH') {
      recs.push('URGENT: Obtain baseline EKG');
      recs.push('Consider alternative medications');
      recs.push('Correct electrolyte abnormalities');
    } else if (overallRisk === 'MODERATE') {
      recs.push('Obtain baseline EKG');
      recs.push('Monitor electrolytes (K+, Mg2+)');
      recs.push('Consider EKG monitoring during therapy');
    }
    
    if (riskFactors.includes('Hypokalemia') || riskFactors.includes('Hypomagnesemia')) {
      recs.push('Correct electrolyte abnormalities before starting QT-prolonging drug');
    }
    
    return recs;
  }
}

module.exports = QTcProlongationChecker;

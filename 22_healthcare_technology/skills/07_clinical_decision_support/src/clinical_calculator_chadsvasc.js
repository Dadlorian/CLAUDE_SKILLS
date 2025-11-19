/**
 * CHADS2-VASc Score Calculator
 * Stroke risk stratification for atrial fibrillation
 */

function calculateCHADSVASc(patient) {
  let score = 0;
  
  // CHF (Congestive Heart Failure)
  if (patient.conditions.includes('CHF')) score += 1;
  
  // Hypertension
  if (patient.conditions.includes('Hypertension')) score += 1;
  
  // Age >= 75
  if (patient.age >= 75) {
    score += 2;
  } else if (patient.age >= 65) {
    // Age 65-74
    score += 1;
  }
  
  // Diabetes
  if (patient.conditions.includes('Diabetes')) score += 1;
  
  // Stroke/TIA/Thromboembolism history
  if (patient.conditions.some(c => ['Stroke', 'TIA', 'Thromboembolism'].includes(c))) {
    score += 2;
  }
  
  // Vascular disease (MI, PAD, aortic plaque)
  if (patient.conditions.some(c => ['MI', 'PAD', 'AorticPlaque'].includes(c))) {
    score += 1;
  }
  
  // Sex category (Female)
  if (patient.sex === 'F') score += 1;
  
  // Risk stratification
  let annualStrokeRisk, recommendation;
  
  if (patient.sex === 'M') {
    if (score === 0) {
      annualStrokeRisk = '0-1%';
      recommendation = 'No antithrombotic therapy or aspirin';
    } else if (score === 1) {
      annualStrokeRisk = '1-2%';
      recommendation = 'Consider anticoagulation';
    } else {
      annualStrokeRisk = '2-15%';
      recommendation = 'Oral anticoagulation recommended';
    }
  } else {  // Female
    if (score === 1) {
      annualStrokeRisk = '0-1%';
      recommendation = 'No antithrombotic therapy or aspirin';
    } else if (score === 2) {
      annualStrokeRisk = '1-2%';
      recommendation = 'Consider anticoagulation';
    } else {
      annualStrokeRisk = '2-15%';
      recommendation = 'Oral anticoagulation recommended';
    }
  }
  
  return {
    score,
    annualStrokeRisk,
    recommendation,
    components: {
      chf: patient.conditions.includes('CHF'),
      hypertension: patient.conditions.includes('Hypertension'),
      age: patient.age,
      diabetes: patient.conditions.includes('Diabetes'),
      strokeHistory: patient.conditions.some(c => ['Stroke', 'TIA'].includes(c)),
      vascularDisease: patient.conditions.some(c => ['MI', 'PAD'].includes(c)),
      sex: patient.sex
    }
  };
}

module.exports = { calculateCHADSVASc };

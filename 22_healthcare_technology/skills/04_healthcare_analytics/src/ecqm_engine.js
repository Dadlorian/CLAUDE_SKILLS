/**
 * eCQM Calculation Engine
 * Implements electronic Clinical Quality Measure logic
 */

class ECQMEngine {
  constructor(measureDefinition) {
    this.measure = measureDefinition;
    this.valueSets = {};
  }

  async loadValueSets(vsacService) {
    for (const vs of this.measure.valueSets) {
      this.valueSets[vs.oid] = await vsacService.getValueSet(vs.oid);
    }
  }

  evaluateMeasure(patient, measurementPeriod) {
    const context = this.buildPatientContext(patient, measurementPeriod);
    
    const initialPopulation = this.evaluatePopulation('initialPopulation', context);
    if (!initialPopulation) return null;

    const denominator = this.evaluatePopulation('denominator', context);
    if (!denominator) return null;

    const denominatorExclusions = this.evaluatePopulation('denominatorExclusions', context);
    if (denominatorExclusions) return { population: 'excluded' };

    const denominatorExceptions = this.evaluatePopulation('denominatorExceptions', context);

    const numerator = this.evaluatePopulation('numerator', context);

    return {
      patientId: patient.id,
      measureId: this.measure.id,
      initialPopulation: initialPopulation,
      denominator: denominator && !denominatorExclusions,
      denominatorExclusions: denominatorExclusions,
      denominatorExceptions: denominatorExceptions,
      numerator: numerator,
      performanceMet: numerator && denominator && !denominatorExclusions && !denominatorExceptions
    };
  }

  buildPatientContext(patient, measurementPeriod) {
    return {
      patient: patient,
      measurementPeriod: measurementPeriod,
      age: this.calculateAge(patient.birthDate, measurementPeriod.end),
      diagnoses: this.getRelevantDiagnoses(patient, measurementPeriod),
      procedures: this.getRelevantProcedures(patient, measurementPeriod),
      medications: this.getRelevantMedications(patient, measurementPeriod),
      labs: this.getRelevantLabs(patient, measurementPeriod),
      encounters: this.getRelevantEncounters(patient, measurementPeriod)
    };
  }

  evaluatePopulation(populationType, context) {
    const logic = this.measure.populations[populationType];
    if (!logic) return false;
    
    // Execute CQL or custom logic
    return this.executeCQL(logic, context);
  }

  calculateAggregateRate(results) {
    const validResults = results.filter(r => r && r.denominator);
    const denominator = validResults.length;
    const numerator = validResults.filter(r => r.performanceMet).length;
    
    return {
      measureId: this.measure.id,
      measureName: this.measure.name,
      denominator: denominator,
      numerator: numerator,
      rate: denominator > 0 ? (numerator / denominator * 100).toFixed(2) : 0,
      measurementPeriod: this.measure.measurementPeriod
    };
  }
}

// Example usage
const cms122 = new ECQMEngine({
  id: 'CMS122v11',
  name: 'Diabetes: HbA1c Poor Control (>9%)',
  populations: {
    initialPopulation: 'age >= 18 AND age < 75 AND hasDiabetes',
    denominator: 'initialPopulation',
    denominatorExclusions: 'hasHospice',
    numerator: 'mostRecentHbA1c > 9.0'
  }
});

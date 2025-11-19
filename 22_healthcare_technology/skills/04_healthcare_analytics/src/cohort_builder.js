/**
 * Cohort Builder for Clinical Analytics
 * Build patient cohorts based on clinical criteria
 */

class CohortBuilder {
  constructor(dataSource) {
    this.dataSource = dataSource;
    this.criteria = [];
  }

  addDiagnosisCriteria(icd10Codes, dateRange) {
    this.criteria.push({
      type: 'diagnosis',
      codes: icd10Codes,
      dateRange: dateRange
    });
    return this;
  }

  addMedicationCriteria(medications, dateRange) {
    this.criteria.push({
      type: 'medication',
      medications: medications,
      dateRange: dateRange
    });
    return this;
  }

  addLabCriteria(labCode, operator, value, dateRange) {
    this.criteria.push({
      type: 'lab',
      labCode: labCode,
      operator: operator,
      value: value,
      dateRange: dateRange
    });
    return this;
  }

  async buildCohort() {
    let cohort = await this.getInitialPopulation();
    
    for (const criterion of this.criteria) {
      cohort = await this.applyCriterion(cohort, criterion);
    }
    
    return {
      cohortSize: cohort.length,
      patients: cohort,
      criteria: this.criteria,
      buildDate: new Date()
    };
  }

  async getInitialPopulation() {
    return await this.dataSource.query('SELECT DISTINCT patient_id FROM patients WHERE active = true');
  }

  async applyCriterion(currentCohort, criterion) {
    switch (criterion.type) {
      case 'diagnosis':
        return await this.filterByDiagnosis(currentCohort, criterion);
      case 'medication':
        return await this.filterByMedication(currentCohort, criterion);
      case 'lab':
        return await this.filterByLab(currentCohort, criterion);
      default:
        return currentCohort;
    }
  }
}

// Usage example
const builder = new CohortBuilder(databaseConnection);
const diabetesCohort = await builder
  .addDiagnosisCriteria(['E11%'], { start: '2023-01-01', end: '2023-12-31' })
  .addLabCriteria('4548-4', '>', 9.0, { start: '2023-01-01', end: '2023-12-31' })
  .buildCohort();

/**
 * Medication Reconciliation
 * Compare and reconcile medication lists from different sources
 */

class MedicationReconciliation {
  /**
   * Reconcile home medications with hospital medications
   */
  reconcile(homeMeds, hospitalMeds) {
    const reconciliation = {
      continued: [],
      discontinued: [],
      newlyAdded: [],
      modified: []
    };

    // Check each home medication
    homeMeds.forEach(homeMed => {
      const match = hospitalMeds.find(hospMed =>
        this.isSameMedication(homeMed, hospMed)
      );

      if (match) {
        if (this.isSameDose(homeMed, match)) {
          reconciliation.continued.push(homeMed);
        } else {
          reconciliation.modified.push({
            original: homeMed,
            modified: match
          });
        }
      } else {
        reconciliation.discontinued.push(homeMed);
      }
    });

    // Find newly added medications
    hospitalMeds.forEach(hospMed => {
      const existsAtHome = homeMeds.find(homeMed =>
        this.isSameMedication(homeMed, hospMed)
      );

      if (!existsAtHome) {
        reconciliation.newlyAdded.push(hospMed);
      }
    });

    return reconciliation;
  }

  isSameMedication(med1, med2) {
    // Compare RxNorm codes if available
    if (med1.rxnorm && med2.rxnorm) {
      return med1.rxnorm === med2.rxnorm;
    }

    // Otherwise compare names (normalized)
    const name1 = med1.name.toLowerCase().replace(/\s+/g, '');
    const name2 = med2.name.toLowerCase().replace(/\s+/g, '');
    return name1 === name2;
  }

  isSameDose(med1, med2) {
    return med1.dose === med2.dose &&
           med1.unit === med2.unit &&
           med1.frequency === med2.frequency;
  }
}

// Example usage
const reconciler = new MedicationReconciliation();

const homeMeds = [
  { name: 'Lisinopril', dose: 10, unit: 'mg', frequency: 'daily', rxnorm: '314076' },
  { name: 'Metformin', dose: 500, unit: 'mg', frequency: 'BID', rxnorm: '860975' }
];

const hospitalMeds = [
  { name: 'Lisinopril', dose: 20, unit: 'mg', frequency: 'daily', rxnorm: '314076' },
  { name: 'Insulin', dose: 10, unit: 'units', frequency: 'QHS', rxnorm: '253182' }
];

const result = reconciler.reconcile(homeMeds, hospitalMeds);
console.log('Reconciliation Result:', JSON.stringify(result, null, 2));

module.exports = MedicationReconciliation;

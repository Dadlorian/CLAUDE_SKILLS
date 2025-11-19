/**
 * Duplicate Therapy Detection
 * Identifies duplicate medications and therapeutic class overlap
 */

const THERAPEUTIC_CLASSES = {
  'ACE_INHIBITORS': ['lisinopril', 'enalapril', 'ramipril'],
  'ARBs': ['losartan', 'valsartan', 'irbesartan'],
  'STATINS': ['atorvastatin', 'simvastatin', 'rosuvastatin'],
  'PPIs': ['omeprazole', 'pantoprazole', 'esomeprazole'],
  'SSRIs': ['fluoxetine', 'sertraline', 'escitalopram']
};

const INGREDIENT_COMBINATIONS = {
  'percocet': ['acetaminophen', 'oxycodone'],
  'vicodin': ['acetaminophen', 'hydrocodone'],
  'norco': ['acetaminophen', 'hydrocodone']
};

class DuplicateTherapyDetector {
  checkDuplicates(activeMedications, newMedication) {
    const duplicates = [];
    
    // Check same ingredient
    const sameIngredient = this.checkSameIngredient(activeMedications, newMedication);
    if (sameIngredient) {
      duplicates.push(sameIngredient);
    }
    
    // Check therapeutic class overlap
    const classOverlap = this.checkTherapeuticClass(activeMedications, newMedication);
    if (classOverlap) {
      duplicates.push(classOverlap);
    }
    
    // Check ingredient combinations (e.g., Percocet + Tylenol)
    const ingredientDup = this.checkIngredientCombination(activeMedications, newMedication);
    if (ingredientDup) {
      duplicates.push(ingredientDup);
    }
    
    return duplicates;
  }
  
  checkSameIngredient(active, newMed) {
    for (const med of active) {
      if (this.extractIngredient(med) === this.extractIngredient(newMed)) {
        return {
          type: 'SAME_INGREDIENT',
          severity: 'HIGH',
          existing: med,
          message: `Patient already taking ${med.name}`,
          recommendation: 'Discontinue existing medication or cancel new order'
        };
      }
    }
    return null;
  }
  
  checkTherapeuticClass(active, newMed) {
    const newClass = this.getDrugClass(newMed.name.toLowerCase());
    
    for (const med of active) {
      const activeClass = this.getDrugClass(med.name.toLowerCase());
      if (newClass && activeClass === newClass) {
        return {
          type: 'THERAPEUTIC_CLASS',
          severity: 'MODERATE',
          therapeuticClass: newClass,
          existing: med,
          message: `Duplicate ${newClass} therapy`,
          recommendation: 'Review if dual therapy intended'
        };
      }
    }
    return null;
  }
  
  checkIngredientCombination(active, newMed) {
    const newIngredients = this.getIngredients(newMed.name.toLowerCase());
    
    for (const med of active) {
      const activeIngredients = this.getIngredients(med.name.toLowerCase());
      const overlap = newIngredients.filter(i => activeIngredients.includes(i));
      
      if (overlap.length > 0) {
        return {
          type: 'INGREDIENT_OVERLAP',
          severity: 'HIGH',
          overlappingIngredients: overlap,
          existing: med,
          message: `Overlapping ingredients: ${overlap.join(', ')}`,
          recommendation: 'Check total daily dose, especially for acetaminophen (max 4g/day)'
        };
      }
    }
    return null;
  }
  
  getDrugClass(drugName) {
    for (const [className, drugs] of Object.entries(THERAPEUTIC_CLASSES)) {
      if (drugs.some(d => drugName.includes(d))) {
        return className;
      }
    }
    return null;
  }
  
  getIngredients(drugName) {
    for (const [combo, ingredients] of Object.entries(INGREDIENT_COMBINATIONS)) {
      if (drugName.includes(combo)) {
        return ingredients;
      }
    }
    return [drugName];
  }
  
  extractIngredient(medication) {
    return medication.ingredient || medication.name.split(' ')[0].toLowerCase();
  }
}

module.exports = DuplicateTherapyDetector;

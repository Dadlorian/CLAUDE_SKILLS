/**
 * Metadata Auto-fill - Auto-populate forms with contract metadata
 * Client-side form automation
 */

class MetadataAutoFill {
  constructor(formId) {
    this.form = document.getElementById(formId);
    this.fieldMappings = {};
    this.metadata = {};
  }

  defineFieldMapping(formField, metadataKey, transformer = null) {
    this.fieldMappings[formField] = {
      metadataKey,
      transformer
    };
    return this;
  }

  setMetadata(metadata) {
    this.metadata = metadata;
    return this;
  }

  autofill() {
    for (const [fieldName, mapping] of Object.entries(this.fieldMappings)) {
      const field = this.form.querySelector(`[name="${fieldName}"]`);

      if (!field) {
        console.warn(`Field not found: ${fieldName}`);
        continue;
      }

      let value = this.getNestedValue(this.metadata, mapping.metadataKey);

      if (value && mapping.transformer) {
        value = mapping.transformer(value);
      }

      this.setFieldValue(field, value);
    }
  }

  getNestedValue(obj, path) {
    return path.split('.').reduce((current, prop) => current?.[prop], obj);
  }

  setFieldValue(field, value) {
    if (!value) return;

    switch (field.type) {
      case 'text':
      case 'email':
      case 'tel':
      case 'date':
      case 'number':
        field.value = value;
        break;
      case 'textarea':
        field.textContent = value;
        break;
      case 'select-one':
      case 'select-multiple':
        this.setSelectValue(field, value);
        break;
      case 'checkbox':
        field.checked = Boolean(value);
        break;
      case 'radio':
        const radio = this.form.querySelector(`input[name="${field.name}"][value="${value}"]`);
        if (radio) radio.checked = true;
        break;
      default:
        field.value = value;
    }

    // Trigger change event for validation
    field.dispatchEvent(new Event('change', { bubbles: true }));
  }

  setSelectValue(selectField, value) {
    if (Array.isArray(value)) {
      value.forEach(v => {
        const option = selectField.querySelector(`option[value="${v}"]`);
        if (option) option.selected = true;
      });
    } else {
      const option = selectField.querySelector(`option[value="${value}"]`);
      if (option) option.selected = true;
    }
  }

  extractFormData() {
    const formData = new FormData(this.form);
    const data = {};

    for (const [key, value] of formData.entries()) {
      data[key] = value;
    }

    return data;
  }

  validate() {
    const errors = [];

    for (const [fieldName, mapping] of Object.entries(this.fieldMappings)) {
      const field = this.form.querySelector(`[name="${fieldName}"]`);

      if (!field) continue;

      if (field.required && !field.value) {
        errors.push(`${fieldName} is required`);
      }

      if (field.type === 'email' && field.value && !this.isValidEmail(field.value)) {
        errors.push(`${fieldName} is not a valid email`);
      }

      if (field.type === 'date' && field.value && !this.isValidDate(field.value)) {
        errors.push(`${fieldName} is not a valid date`);
      }

      if (field.type === 'number' && field.value && isNaN(field.value)) {
        errors.push(`${fieldName} must be a number`);
      }
    }

    return errors;
  }

  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  isValidDate(date) {
    return !isNaN(Date.parse(date));
  }

  clearForm() {
    this.form.reset();
  }
}

// Example usage
document.addEventListener('DOMContentLoaded', () => {
  const metadata = {
    contract: {
      title: 'Service Agreement',
      parties: {
        primary: {
          name: 'ABC Corporation',
          address: '123 Main St, New York, NY 10001'
        },
        secondary: {
          name: 'XYZ Inc.',
          address: '456 Oak Ave, San Francisco, CA 94105'
        }
      },
      dates: {
        effective: '2024-01-15',
        expiration: '2025-01-15'
      },
      financial: {
        value: 150000,
        currency: 'USD',
        paymentTerms: 'Net 30'
      }
    }
  };

  const autofill = new MetadataAutoFill('contractForm')
    .defineFieldMapping('contractTitle', 'contract.title')
    .defineFieldMapping('primaryPartyName', 'contract.parties.primary.name')
    .defineFieldMapping('primaryPartyAddress', 'contract.parties.primary.address')
    .defineFieldMapping('secondaryPartyName', 'contract.parties.secondary.name')
    .defineFieldMapping('effectiveDate', 'contract.dates.effective')
    .defineFieldMapping('expirationDate', 'contract.dates.expiration')
    .defineFieldMapping('contractValue', 'contract.financial.value', 
      (value) => `$${value.toLocaleString()}`)
    .defineFieldMapping('currency', 'contract.financial.currency')
    .defineFieldMapping('paymentTerms', 'contract.financial.paymentTerms')
    .setMetadata(metadata)
    .autofill();

  // Validate form
  const errors = autofill.validate();
  if (errors.length > 0) {
    console.log('Validation errors:', errors);
  }
});

module.exports = MetadataAutoFill;

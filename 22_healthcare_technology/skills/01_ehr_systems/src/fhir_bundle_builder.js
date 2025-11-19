/**
 * FHIR Bundle Builder
 * Build FHIR transaction bundles for batch operations
 */

class FHIRBundleBuilder {
  constructor() {
    this.entries = [];
  }

  /**
   * Add resource to bundle
   */
  addEntry(resource, method = 'POST', url = null) {
    const entry = {
      resource,
      request: {
        method,
        url: url || resource.resourceType
      }
    };

    if (resource.id && method === 'PUT') {
      entry.request.url = `${resource.resourceType}/${resource.id}`;
    }

    this.entries.push(entry);
    return this;
  }

  /**
   * Build transaction bundle
   */
  build(type = 'transaction') {
    return {
      resourceType: 'Bundle',
      type,
      entry: this.entries
    };
  }
}

// Example usage
const builder = new FHIRBundleBuilder();

builder
  .addEntry({
    resourceType: 'Patient',
    name: [{ family: 'Doe', given: ['John'] }],
    birthDate: '1980-01-15'
  })
  .addEntry({
    resourceType: 'Observation',
    status: 'final',
    code: {
      coding: [{ system: 'http://loinc.org', code: '2339-0' }]
    },
    valueQuantity: { value: 95, unit: 'mg/dL' }
  });

const bundle = builder.build();
console.log(JSON.stringify(bundle, null, 2));

module.exports = FHIRBundleBuilder;

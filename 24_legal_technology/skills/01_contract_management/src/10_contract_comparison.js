/**
 * Contract Comparison Tool - Compare contracts and highlight differences
 * Node.js implementation
 */

const levenshtein = require('levenshtein-edit-distance');

class ContractComparison {
  constructor(contract1, contract2) {
    this.contract1 = contract1; // {text, metadata}
    this.contract2 = contract2;
    this.differences = [];
    this.similarity = 0;
  }

  compareClauses() {
    const clauses1 = this.extractClauses(this.contract1.text);
    const clauses2 = this.extractClauses(this.contract2.text);

    const clauseComparisons = [];

    for (const [type, clause1] of Object.entries(clauses1)) {
      if (clauses2[type]) {
        const similarity = this.calculateSimilarity(clause1, clauses2[type]);
        clauseComparisons.push({
          clauseType: type,
          similarity: similarity,
          clause1: clause1.substring(0, 100),
          clause2: clauses2[type].substring(0, 100)
        });

        if (similarity < 0.9) {
          this.differences.push({
            type: 'clause_difference',
            clauseType: type,
            contract1: clause1.substring(0, 200),
            contract2: clauses2[type].substring(0, 200),
            severity: similarity < 0.5 ? 'high' : 'medium'
          });
        }
      } else {
        this.differences.push({
          type: 'missing_clause',
          clauseType: type,
          contract: 1,
          severity: 'medium'
        });
      }
    }

    return clauseComparisons;
  }

  compareMetadata() {
    const metadata1 = this.contract1.metadata || {};
    const metadata2 = this.contract2.metadata || {};

    const metadataComparisons = {};

    const allKeys = new Set([...Object.keys(metadata1), ...Object.keys(metadata2)]);

    for (const key of allKeys) {
      const value1 = metadata1[key];
      const value2 = metadata2[key];

      if (value1 !== value2) {
        this.differences.push({
          type: 'metadata_difference',
          field: key,
          contract1Value: value1,
          contract2Value: value2,
          severity: this.getMetadataSeverity(key)
        });

        metadataComparisons[key] = {
          contract1: value1,
          contract2: value2,
          different: true
        };
      }
    }

    return metadataComparisons;
  }

  compareFinancialTerms() {
    const terms1 = this.contract1.metadata?.financialTerms || {};
    const terms2 = this.contract2.metadata?.financialTerms || {};

    const financialComparisons = {};

    // Compare contract value
    if (terms1.value !== terms2.value) {
      this.differences.push({
        type: 'financial_difference',
        field: 'contract_value',
        contract1: terms1.value,
        contract2: terms2.value,
        variance: this.calculateVariance(terms1.value, terms2.value),
        severity: 'high'
      });
    }

    // Compare payment terms
    if (terms1.paymentTerms !== terms2.paymentTerms) {
      this.differences.push({
        type: 'financial_difference',
        field: 'payment_terms',
        contract1: terms1.paymentTerms,
        contract2: terms2.paymentTerms,
        severity: 'high'
      });
    }

    return financialComparisons;
  }

  extractClauses(text) {
    const clauses = {};

    const clausePatterns = {
      termination: /termination.*?(?=\n|$)/gi,
      liability: /liability.*?(?=\n|$)/gi,
      confidentiality: /confidential.*?(?=\n|$)/gi,
      payment: /payment.*?(?=\n|$)/gi
    };

    for (const [type, pattern] of Object.entries(clausePatterns)) {
      const match = text.match(pattern);
      clauses[type] = match ? match[0] : '';
    }

    return clauses;
  }

  calculateSimilarity(text1, text2) {
    if (!text1 || !text2) return 0;

    const distance = levenshtein(text1, text2);
    const maxLength = Math.max(text1.length, text2.length);

    return 1 - distance / maxLength;
  }

  calculateVariance(value1, value2) {
    if (!value1 || !value2) return 0;

    return Math.abs((value2 - value1) / value1) * 100;
  }

  getMetadataSeverity(fieldName) {
    const highSeverityFields = [
      'effectiveDate',
      'expirationDate',
      'contractValue',
      'paymentTerms'
    ];

    return highSeverityFields.includes(fieldName) ? 'high' : 'medium';
  }

  generateReport() {
    this.compareClauses();
    this.compareMetadata();
    this.compareFinancialTerms();

    const highSeverity = this.differences.filter(d => d.severity === 'high').length;
    const mediumSeverity = this.differences.filter(d => d.severity === 'medium').length;

    return {
      contractId1: this.contract1.id,
      contractId2: this.contract2.id,
      totalDifferences: this.differences.length,
      highSeverityCount: highSeverity,
      mediumSeverityCount: mediumSeverity,
      differences: this.differences,
      summary: `Found ${highSeverity} high-severity and ${mediumSeverity} medium-severity differences`
    };
  }
}

module.exports = ContractComparison;

// Example usage
if (require.main === module) {
  const contract1 = {
    id: 'CNT-001',
    text: 'This contract includes unlimited liability...',
    metadata: {
      effectiveDate: '2024-01-01',
      contractValue: 100000,
      paymentTerms: 'Net 30'
    }
  };

  const contract2 = {
    id: 'CNT-002',
    text: 'This contract limits liability to contract value...',
    metadata: {
      effectiveDate: '2024-02-01',
      contractValue: 150000,
      paymentTerms: 'Net 45'
    }
  };

  const comparison = new ContractComparison(contract1, contract2);
  const report = comparison.generateReport();

  console.log(JSON.stringify(report, null, 2));
}

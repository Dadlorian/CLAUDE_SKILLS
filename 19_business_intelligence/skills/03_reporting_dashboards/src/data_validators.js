/**
 * Data Validation Utilities for Dashboards
 * Ensure data quality before visualization
 */

class DataValidators {
    // Validate required fields exist
    static validateRequiredFields(data, requiredFields) {
        const errors = [];
        
        data.forEach((item, index) => {
            requiredFields.forEach(field => {
                if (item[field] === undefined || item[field] === null) {
                    errors.push(`Row ${index}: Missing required field "${field}"`);
                }
            });
        });
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Validate data types
    static validateDataTypes(data, schema) {
        const errors = [];
        
        data.forEach((item, index) => {
            Object.entries(schema).forEach(([field, expectedType]) => {
                const actualType = typeof item[field];
                if (actualType !== expectedType && item[field] !== null) {
                    errors.push(`Row ${index}: Field "${field}" should be ${expectedType}, got ${actualType}`);
                }
            });
        });
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Validate numeric ranges
    static validateRange(data, field, min, max) {
        const errors = [];
        
        data.forEach((item, index) => {
            const value = item[field];
            if (typeof value === 'number') {
                if (value < min || value > max) {
                    errors.push(`Row ${index}: ${field} value ${value} outside range [${min}, ${max}]`);
                }
            }
        });
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Validate date formats
    static validateDates(data, dateFields) {
        const errors = [];
        
        data.forEach((item, index) => {
            dateFields.forEach(field => {
                const value = item[field];
                if (value && isNaN(Date.parse(value))) {
                    errors.push(`Row ${index}: Invalid date in field "${field}": ${value}`);
                }
            });
        });
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Check for duplicates
    static checkDuplicates(data, uniqueFields) {
        const seen = new Set();
        const duplicates = [];
        
        data.forEach((item, index) => {
            const key = uniqueFields.map(f => item[f]).join('|');
            if (seen.has(key)) {
                duplicates.push(`Row ${index}: Duplicate entry for ${uniqueFields.join(', ')}: ${key}`);
            }
            seen.add(key);
        });
        
        return {
            isValid: duplicates.length === 0,
            errors: duplicates
        };
    }

    // Validate completeness (no missing data)
    static validateCompleteness(data, threshold = 0.95) {
        const fieldCompleteness = {};
        const totalRows = data.length;
        
        if (totalRows === 0) return { isValid: false, errors: ['No data provided'] };
        
        // Get all fields
        const allFields = new Set();
        data.forEach(item => {
            Object.keys(item).forEach(key => allFields.add(key));
        });
        
        // Calculate completeness for each field
        allFields.forEach(field => {
            const nonNullCount = data.filter(item =>
                item[field] !== null && item[field] !== undefined && item[field] !== ''
            ).length;
            fieldCompleteness[field] = nonNullCount / totalRows;
        });
        
        // Find fields below threshold
        const incompleteFields = Object.entries(fieldCompleteness)
            .filter(([_, completeness]) => completeness < threshold)
            .map(([field, completeness]) =>
                `Field "${field}" only ${(completeness * 100).toFixed(1)}% complete`
            );
        
        return {
            isValid: incompleteFields.length === 0,
            completeness: fieldCompleteness,
            errors: incompleteFields
        };
    }

    // Comprehensive validation
    static validate(data, config) {
        const results = {
            isValid: true,
            errors: [],
            warnings: []
        };
        
        // Required fields
        if (config.requiredFields) {
            const req = this.validateRequiredFields(data, config.requiredFields);
            if (!req.isValid) {
                results.isValid = false;
                results.errors.push(...req.errors);
            }
        }
        
        // Data types
        if (config.schema) {
            const types = this.validateDataTypes(data, config.schema);
            if (!types.isValid) {
                results.isValid = false;
                results.errors.push(...types.errors);
            }
        }
        
        // Ranges
        if (config.ranges) {
            Object.entries(config.ranges).forEach(([field, {min, max}]) => {
                const range = this.validateRange(data, field, min, max);
                if (!range.isValid) {
                    results.warnings.push(...range.errors);
                }
            });
        }
        
        // Dates
        if (config.dateFields) {
            const dates = this.validateDates(data, config.dateFields);
            if (!dates.isValid) {
                results.isValid = false;
                results.errors.push(...dates.errors);
            }
        }
        
        // Duplicates
        if (config.uniqueFields) {
            const dups = this.checkDuplicates(data, config.uniqueFields);
            if (!dups.isValid) {
                results.warnings.push(...dups.errors);
            }
        }
        
        // Completeness
        if (config.completenessThreshold) {
            const completeness = this.validateCompleteness(data, config.completenessThreshold);
            if (!completeness.isValid) {
                results.warnings.push(...completeness.errors);
            }
        }
        
        return results;
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataValidators;
}

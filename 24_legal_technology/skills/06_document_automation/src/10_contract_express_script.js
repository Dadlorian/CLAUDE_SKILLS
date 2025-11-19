/**
 * ContractExpress-Style Document Automation
 * Demonstrates document assembly using JavaScript similar to LawConnect's ContractExpress.
 *
 * This implementation shows:
 * - Template variable substitution
 * - Conditional logic and branching
 * - Repeating sections/arrays
 * - Document generation
 *
 * Note: This is a simplified educational implementation.
 */

/**
 * Document Template Class
 * Handles template parsing and variable substitution
 */
class DocumentTemplate {
    constructor(templateText) {
        this.templateText = templateText;
        this.variables = {};
        this.repeatingData = {};
        this.parseTemplate();
    }

    /**
     * Parse template for variables and conditional sections
     */
    parseTemplate() {
        // Extract variable placeholders: [VAR:variable_name]
        const varPattern = /\[VAR:(\w+)\]/g;
        let match;

        while ((match = varPattern.exec(this.templateText)) !== null) {
            const varName = match[1];
            if (!this.variables[varName]) {
                this.variables[varName] = {
                    name: varName,
                    value: null,
                    type: 'text'
                };
            }
        }
    }

    /**
     * Set a variable value
     */
    setVariable(name, value, type = 'text') {
        if (!this.variables[name]) {
            this.variables[name] = {};
        }
        this.variables[name] = {
            name: name,
            value: value,
            type: type
        };
    }

    /**
     * Set multiple variables at once
     */
    setVariables(data) {
        Object.keys(data).forEach(key => {
            this.setVariable(key, data[key]);
        });
    }

    /**
     * Add repeating section data
     */
    addRepeatingSection(sectionName, items) {
        this.repeatingData[sectionName] = items;
    }

    /**
     * Assemble the document
     */
    assemble() {
        let result = this.templateText;

        // Replace variables
        for (const [varName, variable] of Object.entries(this.variables)) {
            const placeholder = `[VAR:${varName}]`;
            const value = variable.value !== null ? String(variable.value) : '';
            result = result.split(placeholder).join(value);
        }

        // Process conditionals
        result = this.processConditionals(result);

        // Process repeating sections
        result = this.processRepeatingDirectives(result);

        return result;
    }

    /**
     * Process conditional blocks: [IF:condition]content[ELSE]else_content[END]
     */
    processConditionals(text) {
        // Pattern: [IF:variable_name]content[ELSE]else_content[END]
        const pattern = /\[IF:(\w+)\]([\s\S]*?)(?:\[ELSE\]([\s\S]*?))?\[END\]/g;

        const result = text.replace(pattern, (match, varName, trueContent, falseContent) => {
            const variable = this.variables[varName];
            const isTruthy = variable && variable.value;
            return isTruthy ? trueContent : (falseContent || '');
        });

        return result;
    }

    /**
     * Process repeating sections: [REPEAT:section_name]content[END_REPEAT]
     */
    processRepeatingDirectives(text) {
        // Pattern: [REPEAT:section_name]content[END_REPEAT]
        const pattern = /\[REPEAT:(\w+)\]([\s\S]*?)\[END_REPEAT\]/g;

        const result = text.replace(pattern, (match, sectionName, content) => {
            if (!this.repeatingData[sectionName]) {
                return '';
            }

            const items = this.repeatingData[sectionName];
            let output = '';

            items.forEach((item, index) => {
                let itemContent = content;

                // Replace item variables
                Object.keys(item).forEach(key => {
                    const placeholder = `[VAR:${sectionName}_${key}]`;
                    itemContent = itemContent.split(placeholder).join(String(item[key]));
                });

                // Replace index if needed
                itemContent = itemContent.split('[VAR:INDEX]').join(String(index + 1));

                output += itemContent;
            });

            return output;
        });

        return result;
    }

    /**
     * Get list of variables that need values
     */
    getRequiredVariables() {
        return Object.values(this.variables)
            .filter(v => v.value === null || v.value === undefined)
            .map(v => ({ name: v.name, type: v.type }));
    }
}

/**
 * Contract Assembly Engine
 * High-level interface for creating documents
 */
class ContractAssemblyEngine {
    /**
     * Create an NDA
     */
    static createNDA(data) {
        const template = `NON-DISCLOSURE AGREEMENT

THIS AGREEMENT is made as of [VAR:agreement_date] between:

DISCLOSING PARTY: [VAR:disclosing_party_name]
Address: [VAR:disclosing_party_address]

RECEIVING PARTY: [VAR:receiving_party_name]
Address: [VAR:receiving_party_address]

1. DEFINITION OF CONFIDENTIAL INFORMATION

Confidential Information includes [IF:include_trade_secrets]trade secrets, [END]technical data,
business information, [IF:include_financial_data]financial information, [END]and other proprietary data.

2. PERMITTED USES

Receiving Party may use Confidential Information solely for:
[VAR:permitted_purpose]

3. OBLIGATIONS

Receiving Party agrees to:
- Maintain strict confidentiality
- Limit access to employees with need-to-know
- Protect information using reasonable security measures
[IF:include_return_clause]- Return or destroy Confidential Information upon request[END]

4. TERM

This Agreement shall remain in effect for [VAR:confidentiality_period] years.

[IF:include_governing_law]
5. GOVERNING LAW

This Agreement shall be governed by the laws of [VAR:governing_jurisdiction].
[END]

IN WITNESS WHEREOF:

Disclosing Party Signature: _______________________________
                           [VAR:disclosing_party_name]
                           Date: ______________

Receiving Party Signature: _______________________________
                          [VAR:receiving_party_name]
                          Date: ______________
`;

        const doc = new DocumentTemplate(template);
        doc.setVariables(data);
        return doc.assemble();
    }

    /**
     * Create a Service Agreement
     */
    static createServiceAgreement(data, services) {
        const template = `SERVICE AGREEMENT

This Agreement is entered into as of [VAR:date] between:

SERVICE PROVIDER: [VAR:provider_name]
Address: [VAR:provider_address]
Phone: [VAR:provider_phone]

CLIENT: [VAR:client_name]
Address: [VAR:client_address]
Phone: [VAR:client_phone]

1. SERVICES

Provider shall provide the following services to Client:

[REPEAT:services]
[VAR:INDEX]. [VAR:services_description]
[END_REPEAT]

2. FEES AND PAYMENT

[IF:hourly_billing]
Hourly Rate: [VAR:hourly_rate] per hour
[END]

[IF:retainer_billing]
Monthly Retainer: [VAR:monthly_retainer]
[END]

Payment Terms: Net [VAR:payment_terms] days from invoice

3. TERM AND RENEWAL

This Agreement shall commence on [VAR:start_date] and continue for [VAR:contract_duration] year(s).

[IF:auto_renewal]
This Agreement shall automatically renew unless either party provides [VAR:termination_notice] days written notice prior to expiration.
[ELSE]
This Agreement shall expire on [VAR:expiration_date] and may be renewed by mutual written agreement.
[END]

4. CONFIDENTIALITY AND NON-COMPETE

[IF:include_confidentiality]
Both parties agree to maintain confidentiality of proprietary information for [VAR:confidentiality_period] years.
[END]

[IF:include_non_compete]
Provider agrees not to compete within [VAR:non_compete_radius] miles for [VAR:non_compete_period] years after termination.
[END]

5. LIMITATION OF LIABILITY

Neither party shall be liable for indirect or consequential damages. Total liability is limited to fees paid in the [VAR:liability_lookback] months preceding the claim.

IN WITNESS WHEREOF:

Provider:

_______________________________
[VAR:provider_name]
Date: ______________


Client:

_______________________________
[VAR:client_name]
Date: ______________
`;

        const doc = new DocumentTemplate(template);
        doc.setVariables(data);
        doc.addRepeatingSection('services', services);
        return doc.assemble();
    }

    /**
     * Create an Employment Agreement
     */
    static createEmploymentAgreement(data) {
        const template = `EMPLOYMENT AGREEMENT

This Agreement is entered into as of [VAR:date] between:

EMPLOYER: [VAR:employer_name]
Address: [VAR:employer_address]

EMPLOYEE: [VAR:employee_name]
Address: [VAR:employee_address]

1. POSITION

Employee is hired as [VAR:job_title] in the [VAR:department] department.
Location: [VAR:work_location]
Reports To: [VAR:reports_to]

2. COMPENSATION

Annual Salary: [VAR:annual_salary]
[IF:include_bonus]Bonus: [VAR:bonus_percentage]% of annual salary[END]
[IF:include_stock]Stock Options: [VAR:stock_options] shares[END]

3. BENEFITS

- Health Insurance: [IF:health_insurance]Provided[ELSE]Employee Responsibility[END]
- Retirement Plan: [IF:retirement_plan][VAR:retirement_plan][ELSE]None[END]
- Paid Time Off: [VAR:pto_days] days per year
- Professional Development Budget: [VAR:professional_development_budget]/year

4. EMPLOYMENT TERM

Start Date: [VAR:start_date]

[IF:at_will_employment]
Employment is at-will and may be terminated by either party with [VAR:termination_notice] days notice.
[ELSE]
Initial Term: [VAR:initial_term] year(s)
[END]

5. CONFIDENTIALITY AND NON-COMPETE

Employee agrees to:
- Maintain strict confidentiality of proprietary information
[IF:include_non_compete]- Not compete for [VAR:non_compete_period] years within [VAR:non_compete_radius] miles[END]
[IF:include_non_solicitation]- Not solicit clients or employees for [VAR:non_solicitation_period] years[END]

6. DUTIES AND RESPONSIBILITIES

Employee agrees to perform duties as assigned by Employer, including:
- Regular attendance and punctuality
- Professional conduct
- Adherence to company policies
- [VAR:additional_duties]

IN WITNESS WHEREOF:

EMPLOYER:

_______________________________
[VAR:employer_name]
By: [VAR:hiring_manager]
Date: ______________


EMPLOYEE:

_______________________________
[VAR:employee_name]
Date: ______________
`;

        const doc = new DocumentTemplate(template);
        doc.setVariables(data);
        return doc.assemble();
    }
}

/**
 * Example Usage Functions
 */

function exampleCreateNDA() {
    console.log('='.repeat(60));
    console.log('EXAMPLE 1: Creating an NDA');
    console.log('='.repeat(60));

    const ndaData = {
        agreement_date: 'January 15, 2024',
        disclosing_party_name: 'TechStartup Inc.',
        disclosing_party_address: '123 Innovation Dr, San Francisco, CA',
        receiving_party_name: 'Potential Investor LLC',
        receiving_party_address: '456 Capital Ave, New York, NY',
        include_trade_secrets: true,
        include_financial_data: true,
        permitted_purpose: 'Evaluating business opportunity and potential investment',
        include_return_clause: true,
        confidentiality_period: '3',
        include_governing_law: true,
        governing_jurisdiction: 'California'
    };

    const nda = ContractAssemblyEngine.createNDA(ndaData);
    console.log(nda);
    console.log('\n');

    return nda;
}

function exampleCreateServiceAgreement() {
    console.log('='.repeat(60));
    console.log('EXAMPLE 2: Creating a Service Agreement');
    console.log('='.repeat(60));

    const services = [
        { description: 'Legal consultation and advice' },
        { description: 'Document drafting and review' },
        { description: 'Compliance consulting' },
        { description: 'Litigation support and representation' }
    ];

    const agreementData = {
        date: 'January 15, 2024',
        provider_name: 'Legal Solutions LLC',
        provider_address: '789 Law Street, San Francisco, CA',
        provider_phone: '(415) 123-4567',
        client_name: 'Acme Corporation',
        client_address: '999 Business Avenue, San Jose, CA',
        client_phone: '(408) 987-6543',
        hourly_billing: true,
        hourly_rate: '250',
        retainer_billing: true,
        monthly_retainer: '5000',
        payment_terms: '30',
        start_date: 'February 1, 2024',
        contract_duration: '1',
        auto_renewal: true,
        termination_notice: '30',
        include_confidentiality: true,
        confidentiality_period: '3',
        include_non_compete: true,
        non_compete_radius: '50',
        non_compete_period: '2',
        liability_lookback: '12'
    };

    const agreement = ContractAssemblyEngine.createServiceAgreement(agreementData, services);
    console.log(agreement);
    console.log('\n');

    return agreement;
}

function exampleCreateEmploymentAgreement() {
    console.log('='.repeat(60));
    console.log('EXAMPLE 3: Creating an Employment Agreement');
    console.log('='.repeat(60));

    const employmentData = {
        date: 'January 15, 2024',
        employer_name: 'TechCorp Industries',
        employer_address: '321 Tech Drive, San Francisco, CA',
        employee_name: 'Jane Smith',
        employee_address: '456 Oak Lane, San Francisco, CA',
        job_title: 'Senior Software Engineer',
        department: 'Engineering',
        work_location: 'San Francisco, CA',
        reports_to: 'Director of Engineering',
        annual_salary: '180,000',
        include_bonus: true,
        bonus_percentage: '20',
        include_stock: true,
        stock_options: '5000',
        health_insurance: true,
        retirement_plan: '401(k) with 4% match',
        pto_days: '20',
        professional_development_budget: '5000',
        start_date: 'February 1, 2024',
        at_will_employment: true,
        termination_notice: '2',
        include_non_compete: true,
        non_compete_period: '1',
        non_compete_radius: '25',
        include_non_solicitation: true,
        non_solicitation_period: '1',
        additional_duties: 'Participate in code reviews, mentor junior engineers, contribute to technical documentation'
    };

    const agreement = ContractAssemblyEngine.createEmploymentAgreement(employmentData);
    console.log(agreement);
    console.log('\n');

    return agreement;
}

function demonstrateConditionalLogic() {
    console.log('='.repeat(60));
    console.log('EXAMPLE 4: Demonstrating Conditional Logic');
    console.log('='.repeat(60));

    const template = new DocumentTemplate(`
AGREEMENT COMPARISON

[IF:premium_package]
PREMIUM PACKAGE FEATURES:
- 24/7 support
- Priority updates
- Dedicated account manager
[ELSE]
STANDARD PACKAGE FEATURES:
- Business hours support (9-5 EST)
- Regular updates
- Standard support channel
[END]

[IF:include_sla]
Service Level Agreement: [VAR:sla_percentage]% uptime guarantee
[END]

[IF:include_insurance]
Insurance Coverage: [VAR:insurance_amount]
[END]
`);

    template.setVariables({
        premium_package: true,
        include_sla: true,
        sla_percentage: '99.9%',
        include_insurance: false,
        insurance_amount: '1,000,000'
    });

    const output = template.assemble();
    console.log(output);
    console.log('\n');
}

function demonstrateRepeatingItems() {
    console.log('='.repeat(60));
    console.log('EXAMPLE 5: Demonstrating Repeating Sections');
    console.log('='.repeat(60));

    const template = new DocumentTemplate(`
INVOICE

Invoice Number: [VAR:invoice_number]
Date: [VAR:invoice_date]

ITEMS:
[REPEAT:line_items]
[VAR:INDEX]. [VAR:line_items_description]
    Quantity: [VAR:line_items_quantity]
    Rate: $[VAR:line_items_rate]
    Amount: $[VAR:line_items_amount]

[END_REPEAT]

TOTAL: $[VAR:total_amount]
`);

    template.setVariables({
        invoice_number: 'INV-2024-001',
        invoice_date: 'January 15, 2024',
        total_amount: '3900'
    });

    const lineItems = [
        { description: 'Contract Review', quantity: '4', rate: '250', amount: '1000' },
        { description: 'Legal Research', quantity: '8', rate: '200', amount: '1600' },
        { description: 'Document Drafting', quantity: '2', rate: '300', amount: '600' },
        { description: 'Consultation', quantity: '2', rate: '350', amount: '700' }
    ];

    template.addRepeatingSection('line_items', lineItems);
    const output = template.assemble();
    console.log(output);
    console.log('\n');
}

/**
 * Main execution
 */
if (typeof module !== 'undefined' && require.main === module) {
    // Node.js execution
    exampleCreateNDA();
    exampleCreateServiceAgreement();
    exampleCreateEmploymentAgreement();
    demonstrateConditionalLogic();
    demonstrateRepeatingItems();

    console.log('='.repeat(60));
    console.log('All ContractExpress examples completed!');
    console.log('='.repeat(60));
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DocumentTemplate,
        ContractAssemblyEngine,
        exampleCreateNDA,
        exampleCreateServiceAgreement,
        exampleCreateEmploymentAgreement,
        demonstrateConditionalLogic,
        demonstrateRepeatingItems
    };
}

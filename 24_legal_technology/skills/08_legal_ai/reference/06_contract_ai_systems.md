# Contract AI Systems

## Overview
Contract AI systems use machine learning and natural language processing to analyze, extract, generate, and manage legal contracts throughout their lifecycle. These systems range from clause extraction tools to fully autonomous contract negotiation platforms.

## Contract AI Workflow
```
┌─────────────────────────────────────────────────┐
│         Contract Lifecycle with AI               │
├─────────────────────────────────────────────────┤
│  1. DRAFTING                                    │
│     - Template Selection (AI-recommended)       │
│     - Clause Generation (GPT/Claude)            │
│     - Risk-based Customization                  │
├─────────────────────────────────────────────────┤
│  2. NEGOTIATION                                 │
│     - Redline Analysis (AI highlights changes)  │
│     - Playbook Comparison (auto-flag deviations)│
│     - Counter-proposal Generation               │
├─────────────────────────────────────────────────┤
│  3. REVIEW & APPROVAL                           │
│     - Risk Scoring (ML-based assessment)        │
│     - Compliance Checking (regulatory AI)       │
│     - Approval Routing (risk-based workflows)   │
├─────────────────────────────────────────────────┤
│  4. EXECUTION                                   │
│     - E-signature Integration                   │
│     - Metadata Extraction                       │
│     - Repository Storage                        │
├─────────────────────────────────────────────────┤
│  5. MANAGEMENT                                  │
│     - Obligation Tracking (NLP extraction)      │
│     - Renewal Monitoring (deadline alerts)      │
│     - Amendment Processing (version control)    │
├─────────────────────────────────────────────────┤
│  6. ANALYTICS                                   │
│     - Portfolio Analysis (aggregate insights)   │
│     - Risk Reporting (dashboards)               │
│     - Performance Metrics (cycle time, etc.)    │
└─────────────────────────────────────────────────┘
```

## Core Contract AI Capabilities

### 1. Clause Extraction and Classification

```python
class ContractClauseExtractor:
    """Extract and classify clauses from contracts"""

    def __init__(self, model_name="nlpaueb/legal-bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(
            "contract-clause-extractor"  # Fine-tuned model
        )

        self.clause_types = [
            "confidentiality",
            "indemnification",
            "limitation_of_liability",
            "termination",
            "payment_terms",
            "intellectual_property",
            "warranties",
            "dispute_resolution",
            "governing_law",
            "assignment",
            "force_majeure",
            "entire_agreement"
        ]

    def extract_clauses(self, contract_text):
        """Extract all clauses from contract"""
        # Split into sentences
        sentences = self.split_legal_sentences(contract_text)

        clauses = []
        for sentence in sentences:
            inputs = self.tokenizer(
                sentence,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )

            outputs = self.model(**inputs)
            prediction = outputs.logits.argmax(dim=-1)

            # If sentence contains a clause
            if prediction.any():
                clause_type = self.clause_types[prediction.max().item()]
                clauses.append({
                    "text": sentence,
                    "type": clause_type,
                    "confidence": torch.softmax(outputs.logits, dim=-1).max().item()
                })

        return clauses

    def split_legal_sentences(self, text):
        """Smart sentence splitting for legal text"""
        # Handle legal citations, abbreviations, etc.
        import re
        # Preserve legal citations like "123 F.3d 456"
        text = re.sub(r'(\d+)\s+([A-Z]\.\s*\d+)', r'\1_\2', text)
        sentences = sent_tokenize(text)
        # Restore citations
        sentences = [s.replace('_', ' ') for s in sentences]
        return sentences

# Usage
extractor = ContractClauseExtractor()

contract = """
This Master Services Agreement ("Agreement") is entered into on January 1, 2024.

CONFIDENTIALITY: Each party agrees to maintain in confidence all Confidential
Information disclosed by the other party and shall not disclose such information
to third parties without prior written consent.

INDEMNIFICATION: Supplier shall indemnify, defend, and hold harmless Client from
any claims arising out of Supplier's negligence or willful misconduct.

LIMITATION OF LIABILITY: In no event shall either party's liability exceed the
fees paid under this Agreement in the twelve months preceding the claim.
"""

clauses = extractor.extract_clauses(contract)
for clause in clauses:
    print(f"{clause['type']}: {clause['text'][:100]}... (confidence: {clause['confidence']:.2%})")
```

### 2. Contract Risk Scoring

```python
class ContractRiskScorer:
    """Assess risk levels in contracts"""

    def __init__(self):
        self.risk_factors = {
            "high_risk": [
                "unlimited_liability",
                "no_limitation_of_liability",
                "broad_indemnification",
                "automatic_renewal",
                "no_termination_for_convenience",
                "assignment_to_competitors",
                "exclusive_dealing",
                "liquidated_damages"
            ],
            "medium_risk": [
                "liability_cap_low",
                "long_term_commitment",
                "restrictive_ip_terms",
                "broad_warranty",
                "foreign_governing_law",
                "mandatory_arbitration"
            ],
            "low_risk": [
                "mutual_terms",
                "standard_liability_cap",
                "termination_for_convenience",
                "reasonable_notice_period"
            ]
        }

    def score_contract(self, clauses):
        """Calculate overall risk score"""
        risk_score = 0
        risk_flags = []

        for clause in clauses:
            clause_risk = self.assess_clause_risk(clause)
            risk_score += clause_risk['score']
            if clause_risk['flags']:
                risk_flags.extend(clause_risk['flags'])

        # Normalize to 0-100 scale
        final_score = min(100, risk_score)

        return {
            "overall_score": final_score,
            "risk_level": self.get_risk_level(final_score),
            "flags": risk_flags,
            "recommendation": self.get_recommendation(final_score)
        }

    def assess_clause_risk(self, clause):
        """Assess risk of individual clause"""
        text_lower = clause['text'].lower()
        score = 0
        flags = []

        # Check for high-risk patterns
        if any(term in text_lower for term in ["unlimited liability", "no limit"]):
            score += 30
            flags.append("Unlimited liability exposure")

        if "indemnify" in text_lower and "all claims" in text_lower:
            score += 20
            flags.append("Broad indemnification obligation")

        if "automatic" in text_lower and "renew" in text_lower:
            score += 15
            flags.append("Automatic renewal clause")

        # Check for missing protections
        if clause['type'] == "limitation_of_liability":
            if "consequential" not in text_lower:
                score += 10
                flags.append("Missing consequential damages waiver")

        return {"score": score, "flags": flags}

    def get_risk_level(self, score):
        if score < 30:
            return "LOW"
        elif score < 60:
            return "MEDIUM"
        else:
            return "HIGH"

    def get_recommendation(self, score):
        if score < 30:
            return "Standard approval process"
        elif score < 60:
            return "Legal review recommended"
        else:
            return "Senior counsel review required"

# Usage
scorer = ContractRiskScorer()
risk_assessment = scorer.score_contract(clauses)

print(f"Risk Score: {risk_assessment['overall_score']}/100")
print(f"Risk Level: {risk_assessment['risk_level']}")
print(f"Recommendation: {risk_assessment['recommendation']}")
print("\nRisk Flags:")
for flag in risk_assessment['flags']:
    print(f"  - {flag}")
```

### 3. Contract Comparison and Redlining

```python
class ContractComparator:
    """Compare contract versions and generate redlines"""

    def __init__(self):
        from difflib import SequenceMatcher
        self.matcher = SequenceMatcher

    def compare_versions(self, original, revised):
        """Compare two contract versions"""
        changes = []

        # Sentence-level comparison
        original_sentences = self.split_sentences(original)
        revised_sentences = self.split_sentences(revised)

        matcher = self.matcher(None, original_sentences, revised_sentences)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes.append({
                    "type": "modified",
                    "original": " ".join(original_sentences[i1:i2]),
                    "revised": " ".join(revised_sentences[j1:j2]),
                    "position": i1
                })
            elif tag == 'delete':
                changes.append({
                    "type": "deleted",
                    "text": " ".join(original_sentences[i1:i2]),
                    "position": i1
                })
            elif tag == 'insert':
                changes.append({
                    "type": "added",
                    "text": " ".join(revised_sentences[j1:j2]),
                    "position": i1
                })

        return changes

    def generate_redline(self, original, revised):
        """Generate Word-style redline document"""
        changes = self.compare_versions(original, revised)

        redline = []
        for change in changes:
            if change['type'] == 'modified':
                redline.append(
                    f"[DELETED: {change['original']}] "
                    f"[ADDED: {change['revised']}]"
                )
            elif change['type'] == 'deleted':
                redline.append(f"[DELETED: {change['text']}]")
            elif change['type'] == 'added':
                redline.append(f"[ADDED: {change['text']}]")

        return "\n".join(redline)

    def analyze_changes(self, changes):
        """Analyze materiality of changes"""
        material_changes = []
        minor_changes = []

        for change in changes:
            if self.is_material_change(change):
                material_changes.append(change)
            else:
                minor_changes.append(change)

        return {
            "material": material_changes,
            "minor": minor_changes,
            "summary": f"{len(material_changes)} material, {len(minor_changes)} minor changes"
        }

    def is_material_change(self, change):
        """Determine if change is material"""
        material_keywords = [
            "liability", "indemnif", "payment", "price",
            "termination", "warranty", "intellectual property",
            "confidential", "damages", "dispute"
        ]

        text = change.get('original', '') + change.get('revised', '') + change.get('text', '')
        return any(keyword in text.lower() for keyword in material_keywords)

# Usage
comparator = ContractComparator()

original = "The liability cap shall be $1,000,000."
revised = "The liability cap shall be $500,000 per incident."

changes = comparator.compare_versions(original, revised)
analysis = comparator.analyze_changes(changes)

print(f"Change Analysis: {analysis['summary']}")
for change in analysis['material']:
    print(f"\nMaterial Change: {change['type']}")
    print(f"Details: {change}")
```

### 4. Obligation and Deadline Extraction

```python
class ContractObligationExtractor:
    """Extract obligations and deadlines from contracts"""

    def __init__(self):
        import dateparser
        from transformers import pipeline

        self.ner_pipeline = pipeline(
            "ner",
            model="legal-ner-model",
            aggregation_strategy="simple"
        )

    def extract_obligations(self, contract_text):
        """Extract all obligations from contract"""
        obligations = []

        # Find obligation patterns
        obligation_patterns = [
            r"(shall|must|will|agrees to)\s+(.+?)(?:\.|;|\n)",
            r"(is required to|is obligated to)\s+(.+?)(?:\.|;|\n)",
            r"(Party|Supplier|Client|Company)\s+(shall|must|will)\s+(.+?)(?:\.|;|\n)"
        ]

        for pattern in obligation_patterns:
            matches = re.finditer(pattern, contract_text, re.IGNORECASE)
            for match in matches:
                obligation_text = match.group(0)

                # Extract who, what, when
                obligation = {
                    "text": obligation_text,
                    "party": self.extract_party(obligation_text),
                    "action": self.extract_action(obligation_text),
                    "deadline": self.extract_deadline(obligation_text),
                    "conditional": self.is_conditional(obligation_text)
                }

                obligations.append(obligation)

        return obligations

    def extract_deadline(self, text):
        """Extract deadlines from obligation text"""
        import dateparser

        # Look for time expressions
        time_patterns = [
            r"within\s+(\d+)\s+(days|weeks|months|years)",
            r"by\s+([A-Z][a-z]+\s+\d+,\s+\d{4})",
            r"on or before\s+([A-Z][a-z]+\s+\d+,\s+\d{4})",
            r"no later than\s+(.+?)(?:\.|;)"
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline_text = match.group(1) if len(match.groups()) == 1 else match.group(0)
                parsed_date = dateparser.parse(deadline_text)
                return {
                    "text": deadline_text,
                    "date": parsed_date,
                    "relative": "within" in text.lower()
                }

        return None

    def extract_party(self, text):
        """Identify which party has the obligation"""
        entities = self.ner_pipeline(text)
        parties = [e['word'] for e in entities if e['entity_group'] == 'ORG']
        return parties[0] if parties else None

    def extract_action(self, text):
        """Extract the required action"""
        # Remove modal verbs and party names
        action = re.sub(r'(shall|must|will|agrees to)\s+', '', text, flags=re.IGNORECASE)
        action = re.sub(r'(Party|Supplier|Client|Company)\s+', '', action, flags=re.IGNORECASE)
        return action.strip()

    def is_conditional(self, text):
        """Check if obligation is conditional"""
        conditional_words = ['if', 'unless', 'provided that', 'subject to', 'in the event']
        return any(word in text.lower() for word in conditional_words)

    def create_obligation_calendar(self, obligations):
        """Create calendar of upcoming obligations"""
        from datetime import datetime, timedelta

        calendar = []
        today = datetime.now()

        for obligation in obligations:
            if obligation['deadline'] and obligation['deadline']['date']:
                deadline_date = obligation['deadline']['date']

                # Calculate days until deadline
                if obligation['deadline']['relative']:
                    # For relative deadlines, we'd need context (e.g., contract effective date)
                    pass
                else:
                    days_until = (deadline_date - today).days

                calendar.append({
                    "obligation": obligation['action'],
                    "party": obligation['party'],
                    "deadline": deadline_date,
                    "days_until": days_until,
                    "urgency": "high" if days_until < 30 else "medium" if days_until < 90 else "low"
                })

        # Sort by deadline
        calendar.sort(key=lambda x: x['deadline'])
        return calendar

# Usage
extractor = ContractObligationExtractor()

contract = """
The Supplier shall deliver the goods within 30 days of the order date.
The Client must provide specifications by March 15, 2024.
If the goods are defective, Supplier shall replace them within 10 business days.
"""

obligations = extractor.extract_obligations(contract)
calendar = extractor.create_obligation_calendar(obligations)

print("Extracted Obligations:")
for obl in obligations:
    print(f"\nParty: {obl['party']}")
    print(f"Action: {obl['action']}")
    print(f"Deadline: {obl['deadline']}")
    print(f"Conditional: {obl['conditional']}")
```

### 5. Contract Generation from Templates

```python
class ContractGenerator:
    """Generate contracts from templates using AI"""

    def __init__(self, model="gpt-4"):
        import openai
        self.model = model

    def generate_contract(self, contract_type, parameters):
        """Generate contract from parameters"""

        template = self.load_template(contract_type)
        prompt = self.create_generation_prompt(template, parameters)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert legal contract drafter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for consistency
        )

        generated_contract = response.choices[0].message.content
        return self.post_process(generated_contract, parameters)

    def create_generation_prompt(self, template, parameters):
        """Create prompt for contract generation"""
        prompt = f"""
Generate a {parameters['contract_type']} based on the following template and parameters:

TEMPLATE:
{template}

PARAMETERS:
"""
        for key, value in parameters.items():
            prompt += f"- {key}: {value}\n"

        prompt += """
INSTRUCTIONS:
1. Fill in all placeholders with the provided parameters
2. Ensure legal accuracy and completeness
3. Use proper legal terminology and formatting
4. Include all standard clauses for this contract type
5. Flag any missing required information

Generate the complete contract:
"""
        return prompt

    def load_template(self, contract_type):
        """Load contract template"""
        templates = {
            "NDA": """
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of [DATE]
by and between [PARTY_1] and [PARTY_2] (each a "Party" and collectively, the "Parties").

1. DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" means...

2. OBLIGATIONS
Each Party agrees to:
(a) Maintain confidentiality...
(b) Not disclose...

[Additional standard NDA provisions]
""",
            "MSA": """
MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is entered into as of [DATE]
by and between [CLIENT] and [SUPPLIER].

1. SERVICES
Supplier shall provide [SERVICES_DESCRIPTION]...

2. PAYMENT TERMS
[PAYMENT_TERMS]...

[Additional MSA provisions]
"""
        }
        return templates.get(contract_type, "")

    def post_process(self, contract, parameters):
        """Post-process generated contract"""
        # Replace any remaining placeholders
        for key, value in parameters.items():
            placeholder = f"[{key.upper()}]"
            contract = contract.replace(placeholder, str(value))

        # Add metadata
        metadata = {
            "generated_date": datetime.now().isoformat(),
            "contract_type": parameters.get('contract_type'),
            "parties": [parameters.get('party_1'), parameters.get('party_2')],
            "parameters": parameters
        }

        return {
            "contract": contract,
            "metadata": metadata,
            "word_count": len(contract.split()),
            "requires_review": True
        }

# Usage
generator = ContractGenerator()

nda_params = {
    "contract_type": "NDA",
    "date": "January 1, 2024",
    "party_1": "Acme Corporation",
    "party_2": "Widget Industries",
    "confidentiality_period": "3 years",
    "governing_law": "Delaware",
    "mutual": True
}

generated = generator.generate_contract("NDA", nda_params)
print(generated['contract'])
print(f"\nMetadata: {generated['metadata']}")
```

## Contract AI Platforms Comparison

```python
platform_comparison = {
    "Ironclad": {
        "strengths": ["CLM workflow", "Clickthrough agreements", "Developer-friendly"],
        "best_for": "Tech companies, high-volume contracts",
        "pricing": "$$$"
    },
    "Icertis": {
        "strengths": ["Enterprise-scale", "Complex workflows", "Compliance"],
        "best_for": "Large enterprises, procurement",
        "pricing": "$$$$"
    },
    "ContractWorks": {
        "strengths": ["Simplicity", "OCR", "Search"],
        "best_for": "Small to mid-size companies",
        "pricing": "$$"
    },
    "Agiloft": {
        "strengths": ["Customization", "No-code", "Value"],
        "best_for": "Organizations needing custom workflows",
        "pricing": "$$"
    },
    "Concord": {
        "strengths": ["User interface", "Collaboration", "Negotiation"],
        "best_for": "Modern teams, ease of use",
        "pricing": "$$"
    }
}
```

## Best Practices

### 1. Data Quality
- Clean OCR artifacts from scanned contracts
- Standardize date formats
- Normalize party names
- Handle multi-language contracts appropriately

### 2. Model Validation
- Test on diverse contract types
- Validate against expert review (gold standard)
- Monitor false positive/negative rates
- Regular recalibration with new data

### 3. Human Oversight
- Never fully automate high-stakes decisions
- Implement approval workflows based on risk
- Maintain audit trails of AI recommendations
- Train users on AI limitations

### 4. Integration
- Integrate with existing CLM systems
- Connect to e-signature platforms
- Enable API access for custom workflows
- Provide export capabilities (Word, PDF, JSON)

---

*Contract AI systems are transforming how organizations draft, review, and manage agreements, delivering significant time savings while improving consistency and reducing risk.*

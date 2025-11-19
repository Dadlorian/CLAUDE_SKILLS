# Explainable AI for Legal Applications

## Overview
Explainability in legal AI is critical because legal decisions affect fundamental rights, require justification, and must be defensible in court. This guide covers techniques and best practices for making legal AI systems interpretable and explainable.

## Why Explainability Matters in Legal AI

### Legal and Regulatory Requirements
- **Right to Explanation**: GDPR Article 22 - right to explanation for automated decisions
- **Legal Reasoning**: Courts require logical justification for decisions
- **Professional Responsibility**: Attorneys must understand basis for legal advice
- **Client Communication**: Clients deserve to understand AI-assisted recommendations
- **Audit and Compliance**: Regulators need to verify AI decision-making

### Interpretability vs. Explainability
```python
interpretability_vs_explainability = {
    "interpretability": {
        "definition": "Model is inherently understandable",
        "examples": ["Linear regression", "Decision trees", "Rule-based systems"],
        "pros": "Transparent by design",
        "cons": "May sacrifice accuracy"
    },
    "explainability": {
        "definition": "Can explain model decisions post-hoc",
        "examples": ["SHAP", "LIME", "Attention visualization"],
        "pros": "Works with complex models",
        "cons": "Explanation may not fully represent model"
    }
}
```

## Explainability Techniques

### 1. SHAP (SHapley Additive exPlanations)

```python
import shap
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class LegalAISHAPExplainer:
    """Explain legal AI predictions using SHAP"""

    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)

    def explain_contract_risk(self, contract_features):
        """Explain contract risk prediction"""

        # Calculate SHAP values
        shap_values = self.explainer.shap_values(contract_features)

        # Get base value (average prediction)
        base_value = self.explainer.expected_value

        # Create explanation
        explanation = {
            "predicted_risk": self.model.predict_proba([contract_features])[0][1],
            "base_risk": base_value,
            "feature_contributions": self.get_feature_contributions(
                contract_features,
                shap_values[1] if isinstance(shap_values, list) else shap_values
            ),
            "narrative": self.generate_narrative_explanation(
                contract_features,
                shap_values[1] if isinstance(shap_values, list) else shap_values
            )
        }

        return explanation

    def get_feature_contributions(self, features, shap_values):
        """Get individual feature contributions"""

        contributions = []

        for i, (feature_name, feature_value) in enumerate(zip(self.feature_names, features)):
            contributions.append({
                "feature": feature_name,
                "value": feature_value,
                "shap_value": shap_values[i],
                "impact": "increases risk" if shap_values[i] > 0 else "decreases risk",
                "magnitude": abs(shap_values[i])
            })

        # Sort by magnitude
        contributions.sort(key=lambda x: x['magnitude'], reverse=True)
        return contributions

    def generate_narrative_explanation(self, features, shap_values):
        """Generate human-readable explanation"""

        contributions = self.get_feature_contributions(features, shap_values)

        narrative = "Risk Assessment Explanation:\n\n"

        # Positive contributors (increase risk)
        positive = [c for c in contributions if c['shap_value'] > 0]
        if positive:
            narrative += "Factors INCREASING risk:\n"
            for i, contrib in enumerate(positive[:3], 1):
                narrative += f"{i}. {contrib['feature']}: {contrib['value']} "
                narrative += f"(impact: +{contrib['magnitude']:.3f})\n"

        # Negative contributors (decrease risk)
        negative = [c for c in contributions if c['shap_value'] < 0]
        if negative:
            narrative += "\nFactors DECREASING risk:\n"
            for i, contrib in enumerate(negative[:3], 1):
                narrative += f"{i}. {contrib['feature']}: {contrib['value']} "
                narrative += f"(impact: {contrib['magnitude']:.3f})\n"

        return narrative

    def plot_waterfall(self, contract_features):
        """Create waterfall plot showing contribution of each feature"""

        shap_values = self.explainer.shap_values(contract_features)

        # Create waterfall plot
        shap.plots.waterfall(
            shap.Explanation(
                values=shap_values[1][0] if isinstance(shap_values, list) else shap_values[0],
                base_values=self.explainer.expected_value,
                data=contract_features[0],
                feature_names=self.feature_names
            )
        )

# Usage Example
# Train contract risk model
X_train = pd.DataFrame({
    'liability_cap': [1000000, 500000, 2000000, 100000],
    'has_indemnification': [1, 1, 1, 0],
    'term_years': [3, 1, 5, 2],
    'auto_renewal': [1, 0, 1, 0],
    'has_limitation_liability': [1, 1, 0, 1]
})
y_train = [0, 0, 1, 0]  # 0=low risk, 1=high risk

model = RandomForestClassifier()
model.fit(X_train, y_train)

# Create explainer
explainer = LegalAISHAPExplainer(model, X_train.columns.tolist())

# Explain prediction for new contract
new_contract = pd.DataFrame({
    'liability_cap': [100000],
    'has_indemnification': [1],
    'term_years': [5],
    'auto_renewal': [1],
    'has_limitation_liability': [0]
})

explanation = explainer.explain_contract_risk(new_contract.values[0])

print(f"Predicted Risk: {explanation['predicted_risk']:.1%}")
print(f"\n{explanation['narrative']}")
```

### 2. LIME (Local Interpretable Model-agnostic Explanations)

```python
from lime.lime_text import LimeTextExplainer
from lime.lime_tabular import LimeTabularExplainer

class LegalAILIMEExplainer:
    """Explain legal AI using LIME"""

    def __init__(self, model):
        self.model = model

    def explain_clause_classification(self, clause_text, class_names):
        """Explain why clause was classified a certain way"""

        # Create LIME text explainer
        explainer = LimeTextExplainer(class_names=class_names)

        # Generate explanation
        explanation = explainer.explain_instance(
            clause_text,
            self.model.predict_proba,
            num_features=10,
            top_labels=2
        )

        # Extract key information
        predicted_class = self.model.predict([clause_text])[0]
        confidence = self.model.predict_proba([clause_text])[0].max()

        # Get words that support/oppose prediction
        supporting_words = []
        opposing_words = []

        for word, weight in explanation.as_list(label=predicted_class):
            if weight > 0:
                supporting_words.append((word, weight))
            else:
                opposing_words.append((word, abs(weight)))

        return {
            "predicted_class": class_names[predicted_class],
            "confidence": confidence,
            "supporting_evidence": supporting_words,
            "contrary_evidence": opposing_words,
            "explanation_html": explanation.as_html(),
            "narrative": self.generate_clause_explanation(
                clause_text,
                class_names[predicted_class],
                supporting_words,
                opposing_words
            )
        }

    def generate_clause_explanation(self, clause, predicted_class, supporting, opposing):
        """Generate narrative explanation for clause classification"""

        explanation = f"This clause was classified as '{predicted_class}' because:\n\n"

        if supporting:
            explanation += "Key phrases supporting this classification:\n"
            for word, weight in supporting[:5]:
                explanation += f"  - '{word}' (importance: {weight:.3f})\n"

        if opposing:
            explanation += "\nPhrases suggesting alternative classifications:\n"
            for word, weight in opposing[:3]:
                explanation += f"  - '{word}' (importance: {weight:.3f})\n"

        return explanation

# Usage
lime_explainer = LegalAILIMEExplainer(clause_classifier_model)

clause = """
The Supplier shall indemnify, defend, and hold harmless the Client, its officers,
directors, and employees from and against any and all claims, damages, losses,
and expenses arising out of or resulting from the Supplier's performance under
this Agreement, including but not limited to claims of negligence or breach of contract.
"""

class_names = ["indemnification", "limitation_of_liability", "warranty", "termination"]

explanation = lime_explainer.explain_clause_classification(clause, class_names)

print(f"Classification: {explanation['predicted_class']} ({explanation['confidence']:.1%})")
print(f"\n{explanation['narrative']}")
```

### 3. Attention Visualization for Legal Text

```python
import torch
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
import seaborn as sns

class LegalBERTAttentionVisualizer:
    """Visualize attention patterns in Legal BERT"""

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.model = AutoModel.from_pretrained(
            "nlpaueb/legal-bert-base-uncased",
            output_attentions=True
        )

    def visualize_attention(self, legal_text, layer=-1, head=0):
        """Visualize which words the model attends to"""

        # Tokenize
        inputs = self.tokenizer(legal_text, return_tensors="pt")
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

        # Get attention weights
        with torch.no_grad():
            outputs = self.model(**inputs)
            attentions = outputs.attentions  # Tuple of attention weights per layer

        # Get attention for specified layer and head
        attention = attentions[layer][0, head].numpy()

        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            attention,
            xticklabels=tokens,
            yticklabels=tokens,
            cmap='YlOrRd',
            square=True
        )
        plt.title(f'Attention Pattern (Layer {layer}, Head {head})')
        plt.xlabel('Tokens')
        plt.ylabel('Tokens')
        plt.xticks(rotation=90)
        plt.yticks(rotation=0)
        plt.tight_layout()

        return plt

    def explain_attention_pattern(self, legal_text):
        """Explain what the model is focusing on"""

        # Get all attention weights
        inputs = self.tokenizer(legal_text, return_tensors="pt")
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

        with torch.no_grad():
            outputs = self.model(**inputs)
            attentions = outputs.attentions

        # Average attention across all heads and layers
        avg_attention = torch.stack(attentions).mean(dim=(0, 1, 2))

        # Find most attended tokens
        token_importance = []
        for i, token in enumerate(tokens):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                token_importance.append({
                    "token": token,
                    "attention_score": avg_attention[i].item()
                })

        token_importance.sort(key=lambda x: x['attention_score'], reverse=True)

        explanation = "The model focused most on these terms:\n"
        for item in token_importance[:10]:
            explanation += f"  - '{item['token']}' (attention: {item['attention_score']:.3f})\n"

        return explanation

# Usage
visualizer = LegalBERTAttentionVisualizer()

contract_clause = """
The limitation of liability shall not apply to damages arising from gross
negligence or willful misconduct of the indemnifying party.
"""

# Visualize attention
plt = visualizer.visualize_attention(contract_clause, layer=-1, head=0)
plt.savefig('attention_heatmap.png')

# Get explanation
explanation = visualizer.explain_attention_pattern(contract_clause)
print(explanation)
```

### 4. Rule Extraction from Neural Networks

```python
class NeuralRuleExtractor:
    """Extract interpretable rules from trained neural networks"""

    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names

    def extract_rules(self, training_data):
        """Extract decision rules from neural network"""

        from sklearn.tree import DecisionTreeClassifier, export_text

        # Get neural network predictions on training data
        nn_predictions = self.model.predict(training_data)

        # Train decision tree to mimic neural network
        surrogate_tree = DecisionTreeClassifier(
            max_depth=5,  # Keep rules interpretable
            min_samples_split=50
        )
        surrogate_tree.fit(training_data, nn_predictions)

        # Extract rules as text
        rules = export_text(surrogate_tree, feature_names=self.feature_names)

        # Convert to more readable format
        readable_rules = self.format_rules(rules)

        # Calculate fidelity (how well tree approximates NN)
        tree_predictions = surrogate_tree.predict(training_data)
        fidelity = (nn_predictions == tree_predictions).mean()

        return {
            "rules": readable_rules,
            "fidelity": fidelity,
            "tree_accuracy": surrogate_tree.score(training_data, nn_predictions),
            "interpretable": True
        }

    def format_rules(self, tree_rules):
        """Format rules for legal professionals"""

        # Parse tree rules into if-then statements
        lines = tree_rules.split('\n')
        formatted_rules = []

        for line in lines:
            if '|--- class:' in line:
                # This is a prediction
                formatted_rules.append(f"THEN classify as {line.split(':')[1].strip()}")
            elif '|---' in line:
                # This is a condition
                condition = line.split('|---')[1].strip()
                formatted_rules.append(f"IF {condition}")

        return '\n'.join(formatted_rules)

# Usage
rule_extractor = NeuralRuleExtractor(neural_network_model, feature_names)
rules = rule_extractor.extract_rules(X_train)

print("Extracted Decision Rules:")
print(rules['rules'])
print(f"\nFidelity to Original Model: {rules['fidelity']:.1%}")
```

## Explainability for Different Legal AI Tasks

### 1. Contract Review Explanations

```python
class ContractReviewExplainer:
    """Explain contract review AI decisions"""

    def explain_risk_assessment(self, contract, risk_score, contributing_clauses):
        """Explain contract risk score to attorney"""

        explanation = {
            "overall_risk": risk_score,
            "risk_level": self.categorize_risk(risk_score),
            "key_issues": [],
            "recommendations": [],
            "supporting_precedents": []
        }

        # Explain each contributing clause
        for clause in contributing_clauses:
            issue = {
                "clause_type": clause['type'],
                "clause_text": clause['text'],
                "risk_contribution": clause['risk_score'],
                "reasoning": self.explain_clause_risk(clause),
                "similar_precedents": self.find_similar_precedents(clause),
                "suggested_modification": self.suggest_modification(clause)
            }
            explanation['key_issues'].append(issue)

        # Generate recommendations
        explanation['recommendations'] = self.generate_recommendations(
            risk_score,
            contributing_clauses
        )

        return explanation

    def explain_clause_risk(self, clause):
        """Explain why specific clause is risky"""

        risk_factors = []

        if clause['type'] == 'indemnification':
            if 'unlimited' in clause['text'].lower():
                risk_factors.append("Unlimited indemnification exposure")
            if 'all claims' in clause['text'].lower():
                risk_factors.append("Broad scope covering all claims")
            if not 'except for' in clause['text'].lower():
                risk_factors.append("No exceptions or carve-outs")

        reasoning = {
            "risk_factors": risk_factors,
            "severity": len(risk_factors) * 0.25,  # Each factor adds 25% risk
            "explanation": " | ".join(risk_factors) if risk_factors else "Standard language"
        }

        return reasoning

# Usage
explainer = ContractReviewExplainer()

contract = load_contract("vendor_agreement.pdf")
risk_score = 0.75  # 75% risk score
contributing_clauses = [
    {
        "type": "indemnification",
        "text": "Supplier shall indemnify Client against all claims...",
        "risk_score": 0.4
    }
]

explanation = explainer.explain_risk_assessment(contract, risk_score, contributing_clauses)

print(f"Risk Level: {explanation['risk_level']}")
for issue in explanation['key_issues']:
    print(f"\nIssue: {issue['clause_type']}")
    print(f"Reasoning: {issue['reasoning']['explanation']}")
    print(f"Suggested Fix: {issue['suggested_modification']}")
```

### 2. Case Outcome Prediction Explanations

```python
class CaseOutcomeExplainer:
    """Explain litigation outcome predictions"""

    def explain_prediction(self, case_facts, prediction, model):
        """Explain predicted case outcome"""

        explanation = {
            "predicted_outcome": prediction['outcome'],
            "confidence": prediction['confidence'],
            "key_factors": self.identify_key_factors(case_facts, model),
            "supporting_precedents": self.find_supporting_precedents(case_facts),
            "opposing_precedents": self.find_opposing_precedents(case_facts),
            "uncertainty_factors": self.identify_uncertainties(case_facts),
            "sensitivity_analysis": self.perform_sensitivity_analysis(case_facts, model)
        }

        return explanation

    def identify_key_factors(self, case_facts, model):
        """Identify which facts were most important"""

        # Use SHAP or similar
        feature_importance = self.calculate_feature_importance(case_facts, model)

        key_factors = []
        for factor in feature_importance[:5]:
            key_factors.append({
                "factor": factor['name'],
                "value": factor['value'],
                "impact": factor['impact'],
                "legal_significance": self.explain_legal_significance(factor)
            })

        return key_factors

    def explain_legal_significance(self, factor):
        """Explain why factor matters legally"""

        significance_map = {
            "judge_ruling_history": "Judge's historical ruling patterns on similar motions",
            "case_complexity": "Complex cases tend to settle more frequently",
            "damages_amount": "Higher damages correlate with settlement likelihood",
            "motion_history": "Repeated motions may indicate weak case",
            "evidence_quality": "Strong evidence significantly impacts outcomes"
        }

        return significance_map.get(factor['name'], "Relevant case factor")

# Usage
outcome_explainer = CaseOutcomeExplainer()

case = {
    "judge": "Hon. Jane Smith",
    "damages_sought": 5000000,
    "case_complexity": 7,
    "evidence_quality": 8,
    "motion_history": 3
}

prediction = {
    "outcome": "Settlement",
    "confidence": 0.72
}

explanation = outcome_explainer.explain_prediction(case, prediction, model)

print(f"Predicted Outcome: {explanation['predicted_outcome']}")
print(f"Confidence: {explanation['confidence']:.0%}\n")
print("Key Factors:")
for factor in explanation['key_factors']:
    print(f"  - {factor['factor']}: {factor['legal_significance']}")
```

## Documentation and Reporting

### Explainability Report Template

```python
def generate_explainability_report(ai_system, decision, explanation):
    """Generate comprehensive explainability report"""

    report = f"""
LEGAL AI EXPLAINABILITY REPORT
================================

AI System: {ai_system['name']}
Version: {ai_system['version']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DECISION SUMMARY
----------------
Task: {decision['task']}
Result: {decision['result']}
Confidence: {decision['confidence']:.1%}

EXPLANATION
-----------
{explanation['narrative']}

KEY FACTORS
-----------
"""

    for i, factor in enumerate(explanation['key_factors'], 1):
        report += f"{i}. {factor['name']}: {factor['value']}\n"
        report += f"   Impact: {factor['impact']}\n"
        report += f"   Legal Significance: {factor['legal_significance']}\n\n"

    report += """
VALIDATION
----------
"""
    report += f"Human Review Required: {decision['requires_review']}\n"
    report += f"Review Completed: {decision.get('reviewed', False)}\n"
    if decision.get('reviewed'):
        report += f"Reviewer: {decision.get('reviewer')}\n"
        report += f"Review Notes: {decision.get('review_notes', 'N/A')}\n"

    report += """
LIMITATIONS
-----------
- This explanation represents the AI's decision-making process
- It does not constitute legal advice
- Human attorney review is required for all outputs
- Confidence scores are probabilistic, not deterministic

ATTESTATION
-----------
I have reviewed this AI-generated analysis and explanation.

Reviewing Attorney: _______________________
Date: _______________________
Signature: _______________________
"""

    return report
```

## Best Practices

1. **Always Provide Explanations**: Never deploy "black box" legal AI
2. **Multiple Explanation Methods**: Use complementary techniques (SHAP + LIME)
3. **Validate Explanations**: Ensure explanations are accurate and faithful
4. **Tailor to Audience**: Different explanations for attorneys vs. clients vs. judges
5. **Document Limitations**: Be clear about what explanations can and cannot show
6. **Ongoing Monitoring**: Ensure explanations remain accurate as model evolves

---

*Explainable AI is not optional in legal applications - it's a professional and often legal requirement. Invest in robust explainability frameworks from the start.*

"""
Legal Named Entity Recognition (NER)

Extract legal entities from contracts: parties, dates, amounts, jurisdictions, etc.
"""

import spacy
from spacy.training import Example
from spacy.util import minibatch
import random
from pathlib import Path

# Define legal entity types
LEGAL_ENTITIES = [
    "PARTY",  # Contract parties (companies, individuals)
    "DATE",  # Effective dates, deadlines
    "MONEY",  # Payment amounts, liability caps
    "JURISDICTION",  # Governing law jurisdictions
    "CITATION",  # Legal citations
    "TERM",  # Contract term/duration
    "PERCENTAGE",  # Percentages (interest rates, equity, etc.)
]

# Training data
TRAIN_DATA = [
    (
        "This Agreement is entered into on January 15, 2024 between Acme Corporation and Widget Industries.",
        {
            "entities": [
                (41, 57, "DATE"),
                (66, 81, "PARTY"),
                (86, 103, "PARTY")
            ]
        }
    ),
    (
        "The liability cap shall be $1,000,000 under Delaware law.",
        {
            "entities": [
                (27, 37, "MONEY"),
                (44, 56, "JURISDICTION")
            ]
        }
    ),
    (
        "Client shall pay Supplier within 30 days of invoice date.",
        {
            "entities": [
                (0, 6, "PARTY"),
                (17, 25, "PARTY"),
                (33, 40, "TERM")
            ]
        }
    ),
    (
        "The interest rate shall be 5.5% per annum.",
        {
            "entities": [
                (27, 31, "PERCENTAGE")
            ]
        }
    ),
    (
        "As established in Smith v. Jones, 123 F.3d 456, the court held...",
        {
            "entities": [
                (18, 33, "CITATION"),
                (35, 48, "CITATION")
            ]
        }
    )
]

def train_legal_ner(training_data, n_iter=30, output_dir=None):
    """Train a legal NER model"""

    # Create blank English model
    nlp = spacy.blank("en")

    # Add NER pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    # Add entity labels
    for label in LEGAL_ENTITIES:
        ner.add_label(label)

    # Start training
    optimizer = nlp.begin_training()

    print(f"Training for {n_iter} iterations...")

    for itn in range(n_iter):
        random.shuffle(training_data)
        losses = {}

        # Batch training data
        batches = minibatch(training_data, size=8)

        for batch in batches:
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)

            nlp.update(examples, drop=0.5, losses=losses)

        if (itn + 1) % 5 == 0:
            print(f"Iteration {itn + 1}/{n_iter} - Loss: {losses['ner']:.4f}")

    # Save model
    if output_dir:
        output_path = Path(output_dir)
        if not output_path.exists():
            output_path.mkdir()
        nlp.to_disk(output_path)
        print(f"\nModel saved to {output_dir}")

    return nlp

def extract_entities(nlp, text):
    """Extract legal entities from text"""

    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })

    return entities

def analyze_contract(nlp, contract_text):
    """Analyze contract and extract all legal entities"""

    entities = extract_entities(nlp, contract_text)

    # Group by entity type
    entity_groups = {}
    for ent in entities:
        label = ent['label']
        if label not in entity_groups:
            entity_groups[label] = []
        entity_groups[label].append(ent['text'])

    return {
        "all_entities": entities,
        "entity_groups": entity_groups,
        "entity_counts": {label: len(ents) for label, ents in entity_groups.items()}
    }

def validate_extraction(nlp, test_cases):
    """Validate NER extraction accuracy"""

    correct = 0
    total = 0
    false_positives = 0
    false_negatives = 0

    for text, expected in test_cases:
        predicted_ents = extract_entities(nlp, text)
        expected_ents = expected['entities']

        # Convert to sets for comparison
        predicted_set = {(e['start'], e['end'], e['label']) for e in predicted_ents}
        expected_set = {(start, end, label) for start, end, label in expected_ents}

        # Calculate metrics
        correct += len(predicted_set & expected_set)
        total += len(expected_set)
        false_positives += len(predicted_set - expected_set)
        false_negatives += len(expected_set - predicted_set)

    precision = correct / (correct + false_positives) if (correct + false_positives) > 0 else 0
    recall = correct / total if total > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "correct": correct,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }

def main():
    """Main execution"""

    print("Training Legal NER Model...")
    print("=" * 60)

    # Train model
    nlp = train_legal_ner(TRAIN_DATA, n_iter=30, output_dir="./legal_ner_model")

    print("\n" + "=" * 60)
    print("Testing Entity Extraction")
    print("=" * 60)

    # Test contract
    test_contract = """
    MASTER SERVICES AGREEMENT

    This Agreement is entered into as of March 1, 2024, between
    TechCorp Inc. ("Client") and DataSolutions LLC ("Supplier").

    1. PAYMENT TERMS
    Client shall pay Supplier $50,000 per month within 15 days of invoice.
    A late fee of 1.5% per month will apply to overdue amounts.

    2. TERM AND TERMINATION
    The initial term is 2 years from the Effective Date. Either party
    may terminate upon 60 days written notice.

    3. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of California,
    without regard to conflicts of law principles.

    4. LIMITATION OF LIABILITY
    Supplier's total liability shall not exceed $500,000 or the fees paid
    in the 12 months preceding the claim, whichever is greater.
    """

    # Extract entities
    analysis = analyze_contract(nlp, test_contract)

    print("\nExtracted Entities:")
    print("-" * 60)

    for label, entities in analysis['entity_groups'].items():
        print(f"\n{label} ({len(entities)}):")
        for entity in entities:
            print(f"  - {entity}")

    print("\n" + "=" * 60)
    print("Entity Statistics:")
    print("=" * 60)

    for label, count in analysis['entity_counts'].items():
        print(f"{label}: {count}")

    # Validate on test data
    print("\n" + "=" * 60)
    print("Validation Results:")
    print("=" * 60)

    validation = validate_extraction(nlp, TRAIN_DATA)

    print(f"Precision: {validation['precision']:.2%}")
    print(f"Recall: {validation['recall']:.2%}")
    print(f"F1 Score: {validation['f1']:.2%}")
    print(f"\nCorrect: {validation['correct']}")
    print(f"False Positives: {validation['false_positives']}")
    print(f"False Negatives: {validation['false_negatives']}")

    # Example: Extract specific entity types
    print("\n" + "=" * 60)
    print("Focused Extraction Examples:")
    print("=" * 60)

    # Extract only monetary amounts
    money_entities = [e for e in analysis['all_entities'] if e['label'] == 'MONEY']
    print(f"\nMonetary Amounts Found: {len(money_entities)}")
    for ent in money_entities:
        print(f"  ${ent['text']}")

    # Extract parties
    party_entities = [e for e in analysis['all_entities'] if e['label'] == 'PARTY']
    print(f"\nParties Identified: {len(party_entities)}")
    for ent in party_entities:
        print(f"  {ent['text']}")

if __name__ == "__main__":
    main()

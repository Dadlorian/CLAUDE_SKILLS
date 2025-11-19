"""
Metadata Extraction using ML - Named Entity Recognition for contract fields
Uses spaCy NER and custom training
"""

import spacy
from spacy.training import Example
import json
from typing import List, Dict

class MetadataExtractorML:
    """Extract metadata using Named Entity Recognition"""
    
    ENTITY_LABELS = [
        'ORG',      # Organization/Party
        'PERSON',   # Person name
        'DATE',     # Date
        'MONEY',    # Financial amount
        'LOCATION', # Location
        'SERVICE',  # Service description
        'SLA',      # Service Level Agreement
    ]
    
    def __init__(self, model_name="en_core_web_sm"):
        self.nlp = spacy.load(model_name)
    
    def train_custom_ner(self, training_data: List[Dict]):
        """Train custom NER model on contract data"""
        # Example training data format:
        # {
        #   "text": "Acme Inc. agrees to pay $50,000 by 2024-12-31",
        #   "entities": [
        #     (0, 8, "ORG"),
        #     (27, 35, "MONEY"),
        #     (39, 49, "DATE")
        #   ]
        # }
        
        ner = self.nlp.get_pipe("ner")
        
        # Add labels
        for label in self.ENTITY_LABELS:
            ner.add_label(label)
        
        # Convert to spacy Examples
        examples = []
        for entry in training_data:
            doc = self.nlp.make_doc(entry["text"])
            entities = []
            for start, end, label in entry["entities"]:
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    entities.append(span)
            
            docbin = spacy.training.Example.from_dict(
                doc,
                {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in entities]}
            )
            examples.append(docbin)
        
        return examples
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        doc = self.nlp(text)
        
        entities_by_type = {}
        for ent in doc.ents:
            if ent.label_ not in entities_by_type:
                entities_by_type[ent.label_] = []
            entities_by_type[ent.label_].append(ent.text)
        
        return entities_by_type
    
    def extract_metadata(self, text: str) -> Dict:
        """Extract structured metadata from contract text"""
        entities = self.extract_entities(text)
        
        metadata = {
            'parties': list(set(entities.get('ORG', []) + entities.get('PERSON', []))),
            'dates': list(set(entities.get('DATE', []))),
            'amounts': list(set(entities.get('MONEY', []))),
            'locations': list(set(entities.get('LOCATION', []))),
            'services': list(set(entities.get('SERVICE', []))),
            'slas': list(set(entities.get('SLA', []))),
        }
        
        return metadata


# Example usage
if __name__ == "__main__":
    extractor = MetadataExtractorML()
    
    sample_text = """
    This Service Agreement is entered into between ABC Corporation and XYZ Inc.
    Effective Date: January 15, 2024
    Service Location: New York, USA
    Annual Fee: $150,000
    Services: Cloud infrastructure management
    SLA: 99.9% uptime guarantee
    """
    
    metadata = extractor.extract_metadata(sample_text)
    print(json.dumps(metadata, indent=2))

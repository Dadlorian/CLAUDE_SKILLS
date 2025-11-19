"""
Clause Extraction - Extract specific clauses from contracts using NLP
Uses spaCy and regex for clause identification
"""

import re
from typing import List, Dict
import spacy

class ClauseExtractor:
    """Extract and categorize contract clauses"""
    
    CLAUSE_TYPES = {
        'termination': r'(?:termination|terminate|shall\s+terminate)',
        'liability': r'(?:liability|liable|indemnif)',
        'confidentiality': r'(?:confidential|confidentiality|trade\s+secret)',
        'ip_rights': r'(?:intellectual\s+property|copyright|patent|proprietary)',
        'payment': r'(?:payment|compensation|fee|charge)',
        'warranty': r'(?:warrant|guarantee|condition)',
        'force_majeure': r'(?:force\s+majeure|act\s+of\s+god)',
        'governing_law': r'(?:governing\s+law|jurisdiction|applicable\s+law)',
        'dispute_resolution': r'(?:arbitration|mediation|dispute)',
        'assignment': r'(?:assignment|assignee|shall\s+not\s+assign)',
    }
    
    def __init__(self, text: str):
        self.text = text
        self.nlp = spacy.load("en_core_web_sm")
        self.clauses = {}
    
    def extract_clause_by_type(self, clause_type: str) -> List[str]:
        """Extract clauses of specific type"""
        if clause_type not in self.CLAUSE_TYPES:
            return []
        
        pattern = self.CLAUSE_TYPES[clause_type]
        
        # Split text into sentences
        doc = self.nlp(self.text)
        sentences = [sent.text for sent in doc.sents]
        
        # Find matching sentences
        matching_clauses = []
        for i, sentence in enumerate(sentences):
            if re.search(pattern, sentence, re.IGNORECASE):
                # Capture surrounding context (previous and next sentences)
                context_start = max(0, i - 1)
                context_end = min(len(sentences), i + 2)
                context = " ".join(sentences[context_start:context_end])
                matching_clauses.append(context)
        
        return matching_clauses
    
    def extract_all_clauses(self) -> Dict[str, List[str]]:
        """Extract all clause types"""
        for clause_type in self.CLAUSE_TYPES.keys():
            self.clauses[clause_type] = self.extract_clause_by_type(clause_type)
        
        return self.clauses
    
    def extract_defined_terms(self) -> Dict[str, str]:
        """Extract defined terms (words in quotes or after 'means')"""
        defined_terms = {}
        
        # Pattern: "Term" means ...
        pattern = r'["\']([^"\']+)["\']\s+(?:means?|definition|defined\s+as):\s*([^\.]+\.)'
        matches = re.findall(pattern, self.text)
        
        for term, definition in matches:
            defined_terms[term] = definition.strip()
        
        return defined_terms
    
    def get_clause_positions(self, clause_type: str) -> List[Dict]:
        """Get positions of clauses in document"""
        if clause_type not in self.CLAUSE_TYPES:
            return []
        
        pattern = self.CLAUSE_TYPES[clause_type]
        positions = []
        
        for match in re.finditer(pattern, self.text, re.IGNORECASE):
            positions.append({
                'clause_type': clause_type,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'matched_text': match.group()
            })
        
        return positions


# Example usage
if __name__ == "__main__":
    with open("sample_contract.txt", "r") as f:
        contract_text = f.read()
    
    extractor = ClauseExtractor(contract_text)
    clauses = extractor.extract_all_clauses()
    
    for clause_type, extractions in clauses.items():
        print(f"\n{clause_type.upper()}:")
        for clause in extractions:
            print(f"  - {clause[:100]}...")

"""
Drug-Drug Interaction Checker
Production-grade medication interaction checking with First DataBank integration
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import httpx
import asyncio

class Severity(Enum):
    CONTRAINDICATED = "CONTRAINDICATED"
    MAJOR = "MAJOR"
    MODERATE = "MODERATE"
    MINOR = "MINOR"

class Documentation(Enum):
    EXCELLENT = "EXCELLENT"  # Controlled studies
    GOOD = "GOOD"            # Case reports
    FAIR = "FAIR"            # Expert opinion
    POOR = "POOR"            # Theoretical

@dataclass
class Medication:
    rxcui: str
    name: str
    dose: Optional[str] = None
    route: Optional[str] = None

@dataclass
class DrugInteraction:
    drug1: Medication
    drug2: Medication
    severity: Severity
    documentation: Documentation
    description: str
    mechanism: str
    clinical_effect: str
    management: str
    onset: str  # RAPID or DELAYED
    alternatives: List[Medication]

class DrugInteractionChecker:
    def __init__(self, fdb_api_key: str):
        self.fdb_api_key = fdb_api_key
        self.base_url = "https://api.fdb.com/v1"
        self.cache = {}
    
    async def check_interactions(
        self,
        medications: List[Medication],
        severity_filter: List[Severity] = None
    ) -> List[DrugInteraction]:
        """Check for drug-drug interactions"""
        
        if len(medications) < 2:
            return []
        
        # Extract RxCUI codes
        rxcuis = [med.rxcui for med in medications]
        
        # Check cache
        cache_key = "-".join(sorted(rxcuis))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Query FDB API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/interactions",
                json={
                    "medications": rxcuis,
                    "severities": [s.value for s in (severity_filter or [Severity.MAJOR, Severity.CONTRAINDICATED])]
                },
                headers={"Authorization": f"Bearer {self.fdb_api_key}"},
                timeout=5.0
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            interactions = [self._parse_interaction(i, medications) for i in data.get("interactions", [])]
            
            # Cache results
            self.cache[cache_key] = interactions
            
            return interactions
    
    def _parse_interaction(self, fdb_data: Dict, medications: List[Medication]) -> DrugInteraction:
        """Parse FDB response into DrugInteraction object"""
        
        drug1 = next(m for m in medications if m.rxcui == fdb_data["drug1"]["rxcui"])
        drug2 = next(m for m in medications if m.rxcui == fdb_data["drug2"]["rxcui"])
        
        return DrugInteraction(
            drug1=drug1,
            drug2=drug2,
            severity=Severity(fdb_data["severity"]),
            documentation=Documentation(fdb_data["documentation"]),
            description=fdb_data["description"],
            mechanism=fdb_data["mechanism"],
            clinical_effect=fdb_data["clinical_effect"],
            management=fdb_data["management"],
            onset=fdb_data["onset"],
            alternatives=self._parse_alternatives(fdb_data.get("alternatives", []))
        )
    
    def _parse_alternatives(self, alt_list: List[Dict]) -> List[Medication]:
        """Parse alternative medications"""
        return [
            Medication(rxcui=alt["rxcui"], name=alt["name"])
            for alt in alt_list
        ]
    
    def filter_by_context(
        self,
        interactions: List[DrugInteraction],
        patient_setting: str
    ) -> List[DrugInteraction]:
        """Filter interactions based on clinical context"""
        
        filtered = []
        
        for interaction in interactions:
            # Always show contraindicated
            if interaction.severity == Severity.CONTRAINDICATED:
                filtered.append(interaction)
                continue
            
            # Major interactions always shown
            if interaction.severity == Severity.MAJOR:
                # Unless in ICU with acceptable monitoring
                if patient_setting != "ICU":
                    filtered.append(interaction)
                elif interaction.documentation == Documentation.EXCELLENT:
                    filtered.append(interaction)
                continue
            
            # Moderate only in outpatient
            if interaction.severity == Severity.MODERATE and patient_setting == "OUTPATIENT":
                filtered.append(interaction)
        
        return filtered


# Example usage
async def main():
    checker = DrugInteractionChecker(fdb_api_key="YOUR_API_KEY")
    
    medications = [
        Medication(rxcui="855332", name="Warfarin 5mg"),
        Medication(rxcui="1191", name="Aspirin 81mg"),
        Medication(rxcui="42463", name="Clarithromycin 500mg")
    ]
    
    interactions = await checker.check_interactions(medications)
    
    for interaction in interactions:
        print(f"\n{interaction.severity.value} Interaction:")
        print(f"  {interaction.drug1.name} + {interaction.drug2.name}")
        print(f"  Effect: {interaction.clinical_effect}")
        print(f"  Management: {interaction.management}")

if __name__ == "__main__":
    asyncio.run(main())

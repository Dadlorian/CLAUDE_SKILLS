"""
Allergy Checking Service
Checks for drug-allergy interactions before medication administration
"""

from typing import List, Dict, Optional
import requests
from dataclasses import dataclass


@dataclass
class AllergyAlert:
    """Represents an allergy alert"""
    severity: str  # 'critical', 'high', 'moderate'
    allergen: str
    medication: str
    reaction: str
    recommendation: str


class AllergyCheckingService:
    """Service for checking drug-allergy interactions"""

    def __init__(self, drug_database_url: str):
        self.drug_database_url = drug_database_url
        # Crossreactivity mapping (simplified example)
        self.cross_reactivity = {
            'PENICILLIN': ['AMOXICILLIN', 'AMPICILLIN', 'PIPERACILLIN'],
            'SULFA': ['SULFAMETHOXAZOLE', 'SULFASALAZINE']
        }

    async def check_medication_against_allergies(
        self,
        medication: str,
        patient_allergies: List[Dict]
    ) -> List[AllergyAlert]:
        """
        Check if medication is safe given patient's allergies
        
        Args:
            medication: Medication name or RxNorm code
            patient_allergies: List of patient allergy records
            
        Returns:
            List of allergy alerts (empty if safe)
        """
        alerts = []

        for allergy in patient_allergies:
            # Skip inactive allergies
            if allergy.get('status') != 'ACTIVE':
                continue

            allergen = allergy.get('allergen_name', '').upper()
            med_upper = medication.upper()

            # Direct match
            if allergen in med_upper or med_upper in allergen:
                alerts.append(AllergyAlert(
                    severity='critical',
                    allergen=allergy['allergen_name'],
                    medication=medication,
                    reaction=allergy.get('reaction', 'Unknown'),
                    recommendation='DO NOT ADMINISTER - Patient has documented allergy'
                ))
                continue

            # Check cross-reactivity
            for allergen_class, related_drugs in self.cross_reactivity.items():
                if allergen_class in allergen:
                    if any(drug in med_upper for drug in related_drugs):
                        alerts.append(AllergyAlert(
                            severity='high',
                            allergen=allergy['allergen_name'],
                            medication=medication,
                            reaction='Possible cross-reactivity',
                            recommendation=f'Use caution - potential cross-reactivity with {allergen_class}'
                        ))

            # Check ingredient overlap
            overlap = await self.check_ingredient_overlap(medication, allergen)
            if overlap:
                alerts.append(AllergyAlert(
                    severity='high',
                    allergen=allergy['allergen_name'],
                    medication=medication,
                    reaction='Shared ingredients',
                    recommendation='Review ingredients before administration'
                ))

        return alerts

    async def check_ingredient_overlap(self, medication: str, allergen: str) -> bool:
        """
        Check if medication shares ingredients with allergen
        (Would integrate with drug database API in production)
        """
        try:
            # Call drug database API
            response = requests.get(
                f"{self.drug_database_url}/ingredients",
                params={
                    'medication': medication,
                    'allergen': allergen
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('has_overlap', False)

        except Exception as e:
            print(f"Error checking ingredient overlap: {e}")

        return False

    def format_alert_for_display(self, alert: AllergyAlert) -> str:
        """Format allergy alert for clinical display"""
        severity_emoji = {
            'critical': '🚫',
            'high': '⚠️',
            'moderate': '⚡'
        }

        return f"""
{severity_emoji.get(alert.severity, '⚠️')} ALLERGY ALERT - {alert.severity.upper()}

Medication: {alert.medication}
Known Allergy: {alert.allergen}
Potential Reaction: {alert.reaction}

RECOMMENDATION: {alert.recommendation}
        """.strip()


# Example usage
if __name__ == '__main__':
    import asyncio

    async def main():
        service = AllergyCheckingService(
            drug_database_url='https://drugdb.example.com/api'
        )

        # Sample patient allergies
        patient_allergies = [
            {
                'allergen_name': 'Penicillin',
                'status': 'ACTIVE',
                'reaction': 'Anaphylaxis, rash',
                'severity': 'SEVERE'
            },
            {
                'allergen_name': 'Sulfa drugs',
                'status': 'ACTIVE',
                'reaction': 'Rash',
                'severity': 'MODERATE'
            }
        ]

        # Check medication
        alerts = await service.check_medication_against_allergies(
            'Amoxicillin 500mg',
            patient_allergies
        )

        if alerts:
            print("⚠️  ALLERGY ALERTS FOUND:")
            for alert in alerts:
                print("\n" + service.format_alert_for_display(alert))
        else:
            print("✅ No allergy concerns detected")

    asyncio.run(main())

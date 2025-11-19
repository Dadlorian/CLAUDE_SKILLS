"""Investment Recommendation - Recommends portfolio based on inputs"""


class InvestmentRecommender:
    """Recommends investment portfolio"""

    def get_recommendation(self, risk_profile: str, goals: list) -> Dict:
        """Get portfolio recommendation"""
        allocations = {
            'Conservative': {
                'equities': ['VOO', 'VEA'],
                'fixed_income': ['BND', 'VTIP'],
                'alternatives': ['VNQ'],
                'target_weights': {'VOO': 0.15, 'VEA': 0.10, 'BND': 0.50, 'VTIP': 0.20, 'VNQ': 0.05}
            },
            'Moderate': {
                'equities': ['VOO', 'VEA', 'VTV'],
                'fixed_income': ['BND', 'VTIP'],
                'alternatives': ['VNQ'],
                'target_weights': {'VOO': 0.30, 'VEA': 0.15, 'VTV': 0.10, 'BND': 0.30, 'VTIP': 0.10, 'VNQ': 0.05}
            },
            'Aggressive': {
                'equities': ['VOO', 'VEA', 'VTV', 'VBR'],
                'fixed_income': ['BND'],
                'alternatives': ['VNQ'],
                'target_weights': {'VOO': 0.35, 'VEA': 0.20, 'VTV': 0.15, 'VBR': 0.10, 'BND': 0.15, 'VNQ': 0.05}
            }
        }

        return allocations.get(risk_profile, allocations['Moderate'])

    def get_rationale(self, risk_profile: str) -> str:
        """Get allocation rationale"""
        rationales = {
            'Conservative': 'Focus on capital preservation with growth exposure',
            'Moderate': 'Balanced growth and stability',
            'Aggressive': 'Maximum growth for long-term goals'
        }
        return rationales.get(risk_profile, '')

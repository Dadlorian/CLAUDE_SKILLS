"""Asset Allocator - Recommends allocation based on risk profile"""
import numpy as np
from typing import Dict


class AssetAllocator:
    """Recommends target asset allocation"""

    ALLOCATIONS = {
        'Conservative': {'stocks': 0.25, 'bonds': 0.70, 'alternatives': 0.05},
        'Moderate-Conservative': {'stocks': 0.40, 'bonds': 0.50, 'alternatives': 0.10},
        'Moderate': {'stocks': 0.60, 'bonds': 0.30, 'alternatives': 0.10},
        'Moderate-Aggressive': {'stocks': 0.75, 'bonds': 0.15, 'alternatives': 0.10},
        'Aggressive': {'stocks': 0.85, 'bonds': 0.10, 'alternatives': 0.05}
    }

    def get_allocation(self, risk_profile: str) -> Dict:
        """Get asset allocation for risk profile"""
        return self.ALLOCATIONS.get(risk_profile, self.ALLOCATIONS['Moderate'])

    def calculate_glide_path(self, current_age: int, retirement_age: int) -> Dict:
        """Calculate dynamic allocation based on age"""
        years_to_retirement = retirement_age - current_age
        
        if years_to_retirement > 20:
            stock_pct = 0.85
        elif years_to_retirement > 10:
            stock_pct = 0.70 - (20 - years_to_retirement) * 0.02
        elif years_to_retirement > 5:
            stock_pct = 0.40 - (10 - years_to_retirement) * 0.05
        else:
            stock_pct = 0.15
        
        return {
            'stocks': stock_pct,
            'bonds': 1 - stock_pct,
            'alternatives': 0
        }

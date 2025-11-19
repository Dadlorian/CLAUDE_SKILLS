"""Loss ratio analysis and calculation"""
from typing import Dict, List

class LossRatioCalculator:
    def calculate_segment_loss_ratio(self, segment: Dict) -> Dict:
        """Calculate loss ratio for segment"""
        earned_premium = segment.get('earned_premium', 0)
        incurred_losses = segment.get('incurred_losses', 0)
        
        if earned_premium == 0:
            loss_ratio = 0
        else:
            loss_ratio = incurred_losses / earned_premium
        
        return {
            "segment": segment.get('name'),
            "earned_premium": earned_premium,
            "incurred_losses": incurred_losses,
            "loss_ratio": round(loss_ratio, 4),
            "profitable": loss_ratio < 0.65
        }
    
    def project_year_end_loss_ratio(self, ytd_data: Dict) -> float:
        """Project year-end loss ratio"""
        months_elapsed = ytd_data.get('months_elapsed', 12)
        ytd_ratio = ytd_data.get('ytd_ratio', 0.65)
        
        projected = ytd_ratio * (12 / months_elapsed)
        return round(projected, 4)

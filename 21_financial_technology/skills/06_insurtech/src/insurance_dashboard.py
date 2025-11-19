"""Insurance analytics dashboard"""
from typing import Dict, List
from datetime import datetime

class InsuranceDashboard:
    def get_dashboard_metrics(self, data: Dict) -> Dict:
        """Get key dashboard metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_premium": data.get('total_premium', 0),
                "earned_premium": data.get('earned_premium', 0),
                "incurred_losses": data.get('incurred_losses', 0),
                "loss_ratio": data.get('loss_ratio', 0),
                "combined_ratio": data.get('combined_ratio', 0),
                "policies_in_force": data.get('policies_in_force', 0),
                "new_business": data.get('new_business', 0),
                "retention_rate": data.get('retention_rate', 0)
            }
        }
    
    def get_trend_data(self, metrics: List[Dict]) -> Dict:
        """Calculate trend data"""
        if len(metrics) < 2:
            return {}
        
        current = metrics[-1]
        prior = metrics[-2]
        
        return {
            "premium_trend": (current.get('premium', 0) - prior.get('premium', 0)) / prior.get('premium', 1),
            "loss_trend": (current.get('losses', 0) - prior.get('losses', 0)) / prior.get('losses', 1)
        }

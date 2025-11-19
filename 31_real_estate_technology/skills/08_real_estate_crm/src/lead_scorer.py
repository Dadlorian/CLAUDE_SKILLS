"""Lead Scoring Engine"""

class LeadScorer:
    def __init__(self):
        self.source_scores = {
            'website': 25,
            'referral': 30,
            'zillow': 20,
            'facebook': 15,
            'google_ads': 22
        }
        
    def score_lead(self, lead):
        """Calculate lead score (0-100)"""
        score = 0
        
        # Source quality (0-30)
        score += self.source_scores.get(lead.get('source'), 10)
        
        # Contact completeness (0-20)
        if lead.get('phone') and lead.get('email'):
            score += 20
        elif lead.get('phone') or lead.get('email'):
            score += 10
            
        # Financial readiness (0-25)
        if lead.get('pre_approved'):
            score += 25
        elif lead.get('budget'):
            score += 15
            
        # Timeline urgency (0-15)
        timeline_scores = {
            'immediately': 15,
            '30_days': 12,
            '90_days': 8,
            '6_months': 5
        }
        score += timeline_scores.get(lead.get('timeline'), 2)
        
        # Engagement (0-10)
        score += min(lead.get('page_views', 0) * 2, 10)
        
        return min(score, 100)
        
    def prioritize_leads(self, leads):
        """Sort leads by score"""
        scored = []
        for lead in leads:
            lead['score'] = self.score_lead(lead)
            scored.append(lead)
            
        return sorted(scored, key=lambda x: x['score'], reverse=True)

# Lead Sources Reference

## Digital Sources
- **Website**: Contact forms, chat
- **Zillow/Realtor.com**: Portal inquiries
- **Google Ads**: PPC campaigns
- **Facebook/Instagram**: Social ads
- **Email**: Newsletter signups

## Traditional Sources
- **Referrals**: Past clients
- **Open houses**: Walk-ins
- **Direct mail**: Postcards
- **Signage**: For sale signs
- **Networking**: Events, BNI

## Lead Quality by Source
| Source | Conversion Rate | Cost per Lead |
|--------|----------------|---------------|
| Referrals | 30-40% | $0 |
| Website | 15-25% | $50 |
| Zillow | 5-10% | $100 |
| Facebook Ads | 8-15% | $75 |
| Google Ads | 10-20% | $80 |
| Open House | 5-10% | $25 |

## Attribution Tracking
```javascript
// Track lead source
const lead = {
  source: 'google_ads',
  medium: 'cpc',
  campaign: 'spring_buyers',
  utm_source: req.query.utm_source,
  utm_medium: req.query.utm_medium,
  utm_campaign: req.query.utm_campaign
};
```

## See Also
- pipeline_stages.md
- scoring_models.md

# Location Intelligence Reference

## Walk Score API
```python
import requests

def get_walk_score(lat, lon, address):
    response = requests.get(
        'https://api.walkscore.com/score',
        params={
            'format': 'json',
            'lat': lat,
            'lon': lon,
            'address': address,
            'wsapikey': WALK_SCORE_KEY
        }
    )
    return response.json()
```

## School Ratings
- GreatSchools API
- Niche.com ratings
- State test scores
- Student-teacher ratios

## Crime Data
- SpotCrime API
- City police departments
- FBI UCR data

## Demographics
- US Census API
- American Community Survey (ACS)
- Income, education, age distribution

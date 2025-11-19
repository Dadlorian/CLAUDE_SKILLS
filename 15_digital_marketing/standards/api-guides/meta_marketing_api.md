# Meta Marketing API Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Facebook Marketing API](#facebook-marketing-api)
4. [Instagram Graph API](#instagram-graph-api)
5. [Campaign Management](#campaign-management)
6. [Audience Targeting](#audience-targeting)
7. [Creative Management](#creative-management)
8. [Insights & Reporting](#insights--reporting)
9. [Webhooks](#webhooks)
10. [Rate Limits & Best Practices](#rate-limits--best-practices)
11. [Error Handling](#error-handling)
12. [Testing Strategies](#testing-strategies)

---

## Overview

The Meta Marketing API provides programmatic access to Facebook and Instagram advertising platforms, enabling automated campaign management, audience targeting, creative optimization, and performance analytics.

### Use Cases

**Facebook Marketing API:**
- Automated campaign creation and optimization
- Bulk ad operations across multiple ad accounts
- Custom audience management and segmentation
- Dynamic creative optimization
- Real-time performance monitoring
- Budget allocation and bid management

**Instagram Graph API:**
- Content publishing and scheduling
- Story management
- Comment and engagement management
- Shopping tag integration
- Insights and analytics
- Influencer collaboration tracking

### API Versions

- **Current Stable Version**: v19.0 (as of 2024)
- **Version Lifecycle**: 2 years from release
- **Recommendation**: Use the latest stable version

---

## Authentication & Authorization

### Access Token Types

Meta uses different access token types for various use cases:

1. **User Access Token**: Short-lived (1 hour) or long-lived (60 days)
2. **Page Access Token**: Access to manage Facebook Pages
3. **App Access Token**: Server-to-server API calls
4. **System User Access Token**: Permanent tokens for Business Manager

### OAuth 2.0 Flow

#### Step 1: Create Facebook App

```yaml
App Dashboard: https://developers.facebook.com/apps/
1. Create new app
2. Select "Business" as app type
3. Add "Marketing API" product
4. Configure app settings:
   - App Domains
   - Privacy Policy URL
   - Terms of Service URL
```

#### Step 2: Configure OAuth Settings

```yaml
OAuth Redirect URIs: https://yourdomain.com/auth/callback
Valid OAuth Redirect URIs:
  - https://yourdomain.com/auth/callback
  - https://localhost:3000/auth/callback (development)

Required Permissions:
  - ads_management
  - ads_read
  - business_management
  - pages_read_engagement
  - pages_manage_posts
  - instagram_basic
  - instagram_content_publish
```

### Python Authentication Implementation

```python
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

class MetaAuth:
    """Handle Meta API authentication and token management"""

    BASE_URL = 'https://graph.facebook.com/v19.0'
    OAUTH_URL = 'https://www.facebook.com/v19.0/dialog/oauth'
    TOKEN_URL = 'https://graph.facebook.com/v19.0/oauth/access_token'

    def __init__(self, app_id, app_secret, redirect_uri):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, scopes):
        """Generate OAuth authorization URL"""
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(scopes),
            'response_type': 'code',
            'state': self.generate_state_token()
        }

        return f"{self.OAUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        response = requests.get(self.TOKEN_URL, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            'access_token': data['access_token'],
            'token_type': data.get('token_type', 'bearer'),
            'expires_in': data.get('expires_in')
        }

    def extend_short_lived_token(self, short_lived_token):
        """Extend short-lived token to long-lived (60 days)"""
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_lived_token
        }

        response = requests.get(self.TOKEN_URL, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            'access_token': data['access_token'],
            'expires_in': data['expires_in'],
            'expires_at': datetime.now() + timedelta(seconds=data['expires_in'])
        }

    def get_page_access_token(self, user_access_token, page_id):
        """Get long-lived page access token"""
        url = f"{self.BASE_URL}/{page_id}"
        params = {
            'fields': 'access_token',
            'access_token': user_access_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()['access_token']

    def debug_token(self, token):
        """Debug and validate access token"""
        url = f"{self.BASE_URL}/debug_token"
        params = {
            'input_token': token,
            'access_token': f"{self.app_id}|{self.app_secret}"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()['data']

    @staticmethod
    def generate_state_token():
        """Generate CSRF protection state token"""
        import secrets
        return secrets.token_urlsafe(32)

# Usage
auth = MetaAuth(
    app_id='YOUR_APP_ID',
    app_secret='YOUR_APP_SECRET',
    redirect_uri='https://yourdomain.com/auth/callback'
)

# Step 1: Get authorization URL
scopes = ['ads_management', 'ads_read', 'business_management']
auth_url = auth.get_authorization_url(scopes)
print(f"Visit: {auth_url}")

# Step 2: Exchange code for token (after user authorization)
code = 'authorization_code_from_callback'
token_data = auth.exchange_code_for_token(code)

# Step 3: Extend to long-lived token
long_lived = auth.extend_short_lived_token(token_data['access_token'])
print(f"Token expires at: {long_lived['expires_at']}")
```

### JavaScript Authentication Implementation

```javascript
const axios = require('axios');
const crypto = require('crypto');

class MetaAuth {
  constructor(appId, appSecret, redirectUri) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.redirectUri = redirectUri;
    this.baseUrl = 'https://graph.facebook.com/v19.0';
    this.oauthUrl = 'https://www.facebook.com/v19.0/dialog/oauth';
  }

  getAuthorizationUrl(scopes) {
    const params = new URLSearchParams({
      client_id: this.appId,
      redirect_uri: this.redirectUri,
      scope: scopes.join(','),
      response_type: 'code',
      state: this.generateStateToken(),
    });

    return `${this.oauthUrl}?${params.toString()}`;
  }

  async exchangeCodeForToken(code) {
    const params = {
      client_id: this.appId,
      client_secret: this.appSecret,
      redirect_uri: this.redirectUri,
      code: code,
    };

    const response = await axios.get(`${this.baseUrl}/oauth/access_token`, {
      params,
    });

    return {
      access_token: response.data.access_token,
      token_type: response.data.token_type || 'bearer',
      expires_in: response.data.expires_in,
    };
  }

  async extendShortLivedToken(shortLivedToken) {
    const params = {
      grant_type: 'fb_exchange_token',
      client_id: this.appId,
      client_secret: this.appSecret,
      fb_exchange_token: shortLivedToken,
    };

    const response = await axios.get(`${this.baseUrl}/oauth/access_token`, {
      params,
    });

    const expiresIn = response.data.expires_in;
    const expiresAt = new Date(Date.now() + expiresIn * 1000);

    return {
      access_token: response.data.access_token,
      expires_in: expiresIn,
      expires_at: expiresAt,
    };
  }

  async getPageAccessToken(userAccessToken, pageId) {
    const response = await axios.get(`${this.baseUrl}/${pageId}`, {
      params: {
        fields: 'access_token',
        access_token: userAccessToken,
      },
    });

    return response.data.access_token;
  }

  async debugToken(token) {
    const response = await axios.get(`${this.baseUrl}/debug_token`, {
      params: {
        input_token: token,
        access_token: `${this.appId}|${this.appSecret}`,
      },
    });

    return response.data.data;
  }

  generateStateToken() {
    return crypto.randomBytes(32).toString('base64url');
  }
}

module.exports = MetaAuth;
```

---

## Facebook Marketing API

### Campaign Structure

```
Ad Account
  └── Campaign
      └── Ad Set
          └── Ad
              └── Creative
```

### Python Implementation

```python
import requests
from typing import Dict, List, Optional

class FacebookMarketingAPI:
    """Facebook Marketing API client"""

    def __init__(self, access_token, api_version='v19.0'):
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f'https://graph.facebook.com/{api_version}'

    def _make_request(self, method, endpoint, params=None, data=None):
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"

        if params is None:
            params = {}
        params['access_token'] = self.access_token

        response = requests.request(
            method=method,
            url=url,
            params=params if method == 'GET' else None,
            json=data if method in ['POST', 'PUT'] else None
        )

        response.raise_for_status()
        return response.json()

    def get_ad_accounts(self):
        """List all ad accounts accessible to the user"""
        endpoint = 'me/adaccounts'
        params = {
            'fields': 'id,name,account_status,currency,timezone_name,amount_spent'
        }

        return self._make_request('GET', endpoint, params=params)

    def create_campaign(self, ad_account_id, campaign_config):
        """Create a new campaign"""
        endpoint = f"act_{ad_account_id}/campaigns"

        data = {
            'name': campaign_config['name'],
            'objective': campaign_config['objective'],
            'status': campaign_config.get('status', 'PAUSED'),
            'special_ad_categories': campaign_config.get('special_ad_categories', []),
        }

        # Add optional fields
        if 'buying_type' in campaign_config:
            data['buying_type'] = campaign_config['buying_type']

        if 'daily_budget' in campaign_config:
            data['daily_budget'] = campaign_config['daily_budget']

        if 'lifetime_budget' in campaign_config:
            data['lifetime_budget'] = campaign_config['lifetime_budget']

        return self._make_request('POST', endpoint, data=data)

    def create_ad_set(self, ad_account_id, ad_set_config):
        """Create ad set with targeting"""
        endpoint = f"act_{ad_account_id}/adsets"

        data = {
            'name': ad_set_config['name'],
            'campaign_id': ad_set_config['campaign_id'],
            'optimization_goal': ad_set_config['optimization_goal'],
            'billing_event': ad_set_config['billing_event'],
            'bid_amount': ad_set_config.get('bid_amount'),
            'daily_budget': ad_set_config.get('daily_budget'),
            'lifetime_budget': ad_set_config.get('lifetime_budget'),
            'start_time': ad_set_config['start_time'],
            'targeting': ad_set_config['targeting'],
            'status': ad_set_config.get('status', 'PAUSED')
        }

        # Add end time if provided
        if 'end_time' in ad_set_config:
            data['end_time'] = ad_set_config['end_time']

        return self._make_request('POST', endpoint, data=data)

    def create_ad_creative(self, ad_account_id, creative_config):
        """Create ad creative"""
        endpoint = f"act_{ad_account_id}/adcreatives"

        data = {
            'name': creative_config['name'],
            'object_story_spec': creative_config['object_story_spec'],
            'degrees_of_freedom_spec': creative_config.get('degrees_of_freedom_spec')
        }

        return self._make_request('POST', endpoint, data=data)

    def create_ad(self, ad_account_id, ad_config):
        """Create ad"""
        endpoint = f"act_{ad_account_id}/ads"

        data = {
            'name': ad_config['name'],
            'adset_id': ad_config['adset_id'],
            'creative': {'creative_id': ad_config['creative_id']},
            'status': ad_config.get('status', 'PAUSED')
        }

        return self._make_request('POST', endpoint, data=data)

    def get_campaign_insights(self, campaign_id, date_range, metrics):
        """Get campaign performance insights"""
        endpoint = f"{campaign_id}/insights"

        params = {
            'time_range': json.dumps(date_range),
            'fields': ','.join(metrics),
            'level': 'campaign'
        }

        return self._make_request('GET', endpoint, params=params)

    def get_ad_account_insights(self, ad_account_id, params):
        """Get ad account insights with custom parameters"""
        endpoint = f"act_{ad_account_id}/insights"

        return self._make_request('GET', endpoint, params=params)

    def update_campaign_status(self, campaign_id, status):
        """Update campaign status (ACTIVE, PAUSED, ARCHIVED)"""
        endpoint = f"{campaign_id}"
        data = {'status': status}

        return self._make_request('POST', endpoint, data=data)

    def update_ad_set_budget(self, ad_set_id, budget_type, amount):
        """Update ad set budget"""
        endpoint = f"{ad_set_id}"

        data = {
            budget_type: amount  # 'daily_budget' or 'lifetime_budget'
        }

        return self._make_request('POST', endpoint, data=data)

# Usage Examples
api = FacebookMarketingAPI(access_token='YOUR_ACCESS_TOKEN')

# List ad accounts
accounts = api.get_ad_accounts()
print(f"Found {len(accounts['data'])} ad accounts")

# Create campaign
campaign = api.create_campaign(
    ad_account_id='123456789',
    campaign_config={
        'name': 'Summer Sale 2024',
        'objective': 'OUTCOME_SALES',
        'status': 'PAUSED',
        'daily_budget': 10000,  # $100 in cents
        'special_ad_categories': []
    }
)

print(f"Created campaign: {campaign['id']}")
```

### Campaign Objectives Reference

```python
CAMPAIGN_OBJECTIVES = {
    'OUTCOME_AWARENESS': 'Brand awareness',
    'OUTCOME_ENGAGEMENT': 'Engagement (likes, comments, shares)',
    'OUTCOME_TRAFFIC': 'Traffic to website/app',
    'OUTCOME_LEADS': 'Lead generation',
    'OUTCOME_APP_PROMOTION': 'App installs and engagement',
    'OUTCOME_SALES': 'Conversions and sales'
}

# Optimization goals by objective
OPTIMIZATION_GOALS = {
    'OUTCOME_AWARENESS': ['REACH', 'AD_RECALL_LIFT', 'IMPRESSIONS'],
    'OUTCOME_ENGAGEMENT': ['POST_ENGAGEMENT', 'PAGE_LIKES', 'EVENT_RESPONSES'],
    'OUTCOME_TRAFFIC': ['LINK_CLICKS', 'LANDING_PAGE_VIEWS'],
    'OUTCOME_LEADS': ['LEAD_GENERATION', 'QUALITY_LEAD'],
    'OUTCOME_SALES': ['OFFSITE_CONVERSIONS', 'VALUE']
}
```

---

## Instagram Graph API

### Content Publishing

```python
class InstagramAPI:
    """Instagram Graph API client"""

    def __init__(self, access_token, api_version='v19.0'):
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f'https://graph.facebook.com/{api_version}'

    def publish_photo(self, instagram_account_id, image_url, caption, location_id=None):
        """Publish a photo to Instagram"""
        # Step 1: Create media container
        container_endpoint = f"{instagram_account_id}/media"

        container_params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.access_token
        }

        if location_id:
            container_params['location_id'] = location_id

        container_response = requests.post(
            f"{self.base_url}/{container_endpoint}",
            params=container_params
        )
        container_response.raise_for_status()
        container_id = container_response.json()['id']

        # Step 2: Publish media container
        publish_endpoint = f"{instagram_account_id}/media_publish"
        publish_params = {
            'creation_id': container_id,
            'access_token': self.access_token
        }

        publish_response = requests.post(
            f"{self.base_url}/{publish_endpoint}",
            params=publish_params
        )
        publish_response.raise_for_status()

        return publish_response.json()

    def publish_carousel(self, instagram_account_id, children_urls, caption):
        """Publish carousel post (multiple images/videos)"""
        # Step 1: Create containers for each media item
        children_ids = []

        for media_url in children_urls:
            params = {
                'image_url': media_url,
                'is_carousel_item': True,
                'access_token': self.access_token
            }

            response = requests.post(
                f"{self.base_url}/{instagram_account_id}/media",
                params=params
            )
            response.raise_for_status()
            children_ids.append(response.json()['id'])

        # Step 2: Create carousel container
        carousel_params = {
            'media_type': 'CAROUSEL',
            'children': ','.join(children_ids),
            'caption': caption,
            'access_token': self.access_token
        }

        carousel_response = requests.post(
            f"{self.base_url}/{instagram_account_id}/media",
            params=carousel_params
        )
        carousel_response.raise_for_status()
        carousel_id = carousel_response.json()['id']

        # Step 3: Publish carousel
        publish_params = {
            'creation_id': carousel_id,
            'access_token': self.access_token
        }

        publish_response = requests.post(
            f"{self.base_url}/{instagram_account_id}/media_publish",
            params=publish_params
        )
        publish_response.raise_for_status()

        return publish_response.json()

    def publish_story(self, instagram_account_id, media_url, media_type='IMAGE'):
        """Publish Instagram Story"""
        params = {
            'media_type': 'STORIES',
            'access_token': self.access_token
        }

        if media_type == 'IMAGE':
            params['image_url'] = media_url
        else:
            params['video_url'] = media_url

        # Create story container
        container_response = requests.post(
            f"{self.base_url}/{instagram_account_id}/media",
            params=params
        )
        container_response.raise_for_status()
        container_id = container_response.json()['id']

        # Publish story
        publish_params = {
            'creation_id': container_id,
            'access_token': self.access_token
        }

        publish_response = requests.post(
            f"{self.base_url}/{instagram_account_id}/media_publish",
            params=publish_params
        )
        publish_response.raise_for_status()

        return publish_response.json()

    def get_media_insights(self, media_id, metrics):
        """Get insights for a specific media post"""
        endpoint = f"{media_id}/insights"

        params = {
            'metric': ','.join(metrics),
            'access_token': self.access_token
        }

        response = requests.get(
            f"{self.base_url}/{endpoint}",
            params=params
        )
        response.raise_for_status()

        return response.json()

    def get_account_insights(self, instagram_account_id, metrics, period, since, until):
        """Get account-level insights"""
        endpoint = f"{instagram_account_id}/insights"

        params = {
            'metric': ','.join(metrics),
            'period': period,  # 'day', 'week', 'days_28', 'lifetime'
            'since': since,
            'until': until,
            'access_token': self.access_token
        }

        response = requests.get(
            f"{self.base_url}/{endpoint}",
            params=params
        )
        response.raise_for_status()

        return response.json()

    def manage_comments(self, media_id, action='get'):
        """Manage comments on media"""
        endpoint = f"{media_id}/comments"

        if action == 'get':
            params = {
                'fields': 'id,text,username,timestamp',
                'access_token': self.access_token
            }

            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params
            )
        elif action == 'hide':
            # Hide specific comment
            params = {
                'hide': True,
                'access_token': self.access_token
            }

            response = requests.post(
                f"{self.base_url}/{endpoint}",
                params=params
            )

        response.raise_for_status()
        return response.json()

# Usage
instagram = InstagramAPI(access_token='YOUR_ACCESS_TOKEN')

# Publish photo
post = instagram.publish_photo(
    instagram_account_id='17841400001234567',
    image_url='https://example.com/image.jpg',
    caption='Check out our new product! #marketing'
)

# Get insights
insights = instagram.get_media_insights(
    media_id=post['id'],
    metrics=['engagement', 'impressions', 'reach', 'saved']
)
```

---

## Audience Targeting

### Custom Audiences

```python
class AudienceManager:
    """Manage Facebook custom audiences"""

    def __init__(self, api_client):
        self.api = api_client

    def create_custom_audience(self, ad_account_id, audience_config):
        """Create custom audience"""
        endpoint = f"act_{ad_account_id}/customaudiences"

        data = {
            'name': audience_config['name'],
            'subtype': audience_config['subtype'],
            'description': audience_config.get('description', ''),
            'customer_file_source': 'USER_PROVIDED_ONLY'
        }

        return self.api._make_request('POST', endpoint, data=data)

    def add_users_to_audience(self, audience_id, users, schema):
        """Add users to custom audience"""
        endpoint = f"{audience_id}/users"

        # Hash user data (emails, phone numbers, etc.)
        import hashlib

        hashed_users = []
        for user in users:
            if schema == 'EMAIL_SHA256':
                hashed = hashlib.sha256(user.lower().encode()).hexdigest()
            elif schema == 'PHONE_SHA256':
                # Remove non-numeric characters
                cleaned = ''.join(filter(str.isdigit, user))
                hashed = hashlib.sha256(cleaned.encode()).hexdigest()
            else:
                hashed = user

            hashed_users.append(hashed)

        data = {
            'payload': {
                'schema': [schema],
                'data': [[h] for h in hashed_users]
            }
        }

        return self.api._make_request('POST', endpoint, data=data)

    def create_lookalike_audience(self, ad_account_id, source_audience_id, target_country, ratio):
        """Create lookalike audience from source audience"""
        endpoint = f"act_{ad_account_id}/customaudiences"

        data = {
            'name': f'Lookalike - {ratio}%',
            'subtype': 'LOOKALIKE',
            'origin_audience_id': source_audience_id,
            'lookalike_spec': {
                'type': 'similarity',
                'country': target_country,
                'ratio': ratio  # 0.01 to 0.20 (1% to 20%)
            }
        }

        return self.api._make_request('POST', endpoint, data=data)

    def create_website_custom_audience(self, ad_account_id, pixel_id, retention_days):
        """Create website custom audience based on pixel events"""
        endpoint = f"act_{ad_account_id}/customaudiences"

        data = {
            'name': 'Website Visitors',
            'subtype': 'WEBSITE',
            'retention_days': retention_days,
            'rule': {
                'inclusions': {
                    'operator': 'or',
                    'rules': [
                        {
                            'event_sources': [{'id': pixel_id, 'type': 'pixel'}],
                            'retention_seconds': retention_days * 86400,
                            'filter': {
                                'operator': 'and',
                                'filters': [
                                    {
                                        'field': 'url',
                                        'operator': 'i_contains',
                                        'value': 'product'
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        return self.api._make_request('POST', endpoint, data=data)

# Targeting specification examples
TARGETING_EXAMPLES = {
    'location_and_demographics': {
        'geo_locations': {
            'countries': ['US'],
            'regions': [{'key': '3847'}],  # California
            'cities': [{'key': '2418779', 'radius': 10, 'distance_unit': 'mile'}]
        },
        'age_min': 25,
        'age_max': 45,
        'genders': [1],  # 1: male, 2: female
        'locales': [6]  # English (US)
    },

    'interests_and_behaviors': {
        'interests': [
            {'id': '6003139266461', 'name': 'Online shopping'},
            {'id': '6003107902433', 'name': 'Technology'}
        ],
        'behaviors': [
            {'id': '6002714895372', 'name': 'Frequent travelers'}
        ]
    },

    'detailed_targeting': {
        'flexible_spec': [
            {
                'interests': [{'id': '6003139266461'}],
                'behaviors': [{'id': '6002714895372'}]
            }
        ],
        'exclusions': {
            'interests': [{'id': '6003139266461'}]
        }
    }
}
```

---

## Creative Management

### Dynamic Creative Optimization

```python
class CreativeManager:
    """Manage ad creatives and dynamic creative optimization"""

    def __init__(self, api_client):
        self.api = api_client

    def create_dynamic_creative(self, ad_account_id, creative_config):
        """Create dynamic creative with multiple variations"""
        endpoint = f"act_{ad_account_id}/adcreatives"

        # Dynamic creative allows testing multiple combinations
        data = {
            'name': creative_config['name'],
            'object_story_spec': {
                'page_id': creative_config['page_id'],
                'link_data': {
                    'link': creative_config['link'],
                    'message': creative_config['messages'],  # Array of messages
                    'name': creative_config['headlines'],     # Array of headlines
                    'description': creative_config['descriptions'],  # Array
                    'call_to_action': {
                        'type': creative_config['cta_type'],
                        'value': {'link': creative_config['link']}
                    },
                    'image_hash': creative_config['image_hashes']  # Array
                },
                'multi_share_optimized': True
            },
            'degrees_of_freedom_spec': {
                'creative_features_spec': {
                    'standard_enhancements': {
                        'enroll_status': 'OPT_IN'
                    }
                }
            }
        }

        return self.api._make_request('POST', endpoint, data=data)

    def upload_image(self, ad_account_id, image_path):
        """Upload image and get image hash"""
        endpoint = f"act_{ad_account_id}/adimages"

        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            params = {'access_token': self.api.access_token}

            response = requests.post(
                f"{self.api.base_url}/{endpoint}",
                params=params,
                files=files
            )

        response.raise_for_status()
        return response.json()['images'].values()[0]['hash']

    def upload_video(self, ad_account_id, video_path):
        """Upload video for ad creative"""
        endpoint = f"act_{ad_account_id}/advideos"

        with open(video_path, 'rb') as video_file:
            files = {'file': video_file}
            params = {'access_token': self.api.access_token}

            response = requests.post(
                f"{self.api.base_url}/{endpoint}",
                params=params,
                files=files
            )

        response.raise_for_status()
        return response.json()['id']

    def create_carousel_creative(self, ad_account_id, carousel_config):
        """Create carousel ad creative"""
        endpoint = f"act_{ad_account_id}/adcreatives"

        child_attachments = []
        for item in carousel_config['items']:
            child_attachments.append({
                'name': item['headline'],
                'description': item['description'],
                'link': item['link'],
                'image_hash': item['image_hash'],
                'call_to_action': {
                    'type': item.get('cta_type', 'LEARN_MORE')
                }
            })

        data = {
            'name': carousel_config['name'],
            'object_story_spec': {
                'page_id': carousel_config['page_id'],
                'link_data': {
                    'link': carousel_config['link'],
                    'message': carousel_config['message'],
                    'child_attachments': child_attachments,
                    'multi_share_optimized': True
                }
            }
        }

        return self.api._make_request('POST', endpoint, data=data)

# Usage
creative_mgr = CreativeManager(api)

# Upload images
image_hash_1 = creative_mgr.upload_image('123456789', 'path/to/image1.jpg')
image_hash_2 = creative_mgr.upload_image('123456789', 'path/to/image2.jpg')

# Create dynamic creative
dynamic_creative = creative_mgr.create_dynamic_creative(
    ad_account_id='123456789',
    creative_config={
        'name': 'Dynamic Product Ad',
        'page_id': '987654321',
        'link': 'https://example.com/product',
        'messages': [
            'Get 20% off today!',
            'Limited time offer!',
            'Shop now and save!'
        ],
        'headlines': [
            'Best Products',
            'Top Quality',
            'Customer Favorite'
        ],
        'descriptions': [
            'Premium quality products',
            'Fast shipping available'
        ],
        'cta_type': 'SHOP_NOW',
        'image_hashes': [image_hash_1, image_hash_2]
    }
)
```

---

## Insights & Reporting

### Comprehensive Reporting

```python
class InsightsReporter:
    """Advanced reporting and analytics"""

    def __init__(self, api_client):
        self.api = api_client

    def get_campaign_breakdown(self, ad_account_id, date_range, breakdowns):
        """Get campaign insights with breakdowns"""
        endpoint = f"act_{ad_account_id}/insights"

        params = {
            'level': 'campaign',
            'time_range': json.dumps(date_range),
            'breakdowns': ','.join(breakdowns),
            'fields': ','.join([
                'campaign_name',
                'impressions',
                'clicks',
                'spend',
                'ctr',
                'cpc',
                'cpp',
                'cpm',
                'reach',
                'frequency',
                'actions',
                'cost_per_action_type',
                'conversion_values',
                'video_avg_time_watched_actions',
                'video_p25_watched_actions',
                'video_p50_watched_actions',
                'video_p75_watched_actions',
                'video_p100_watched_actions'
            ])
        }

        return self.api._make_request('GET', endpoint, params=params)

    def get_attribution_insights(self, ad_account_id, date_range, attribution_windows):
        """Get insights with different attribution windows"""
        endpoint = f"act_{ad_account_id}/insights"

        params = {
            'level': 'campaign',
            'time_range': json.dumps(date_range),
            'action_attribution_windows': json.dumps(attribution_windows),
            'fields': 'campaign_name,actions,action_values,cost_per_action_type'
        }

        return self.api._make_request('GET', endpoint, params=params)

    def generate_performance_report(self, ad_account_id, start_date, end_date):
        """Generate comprehensive performance report"""
        date_range = {
            'since': start_date,
            'until': end_date
        }

        # Get overall metrics
        overall = self.get_campaign_breakdown(
            ad_account_id=ad_account_id,
            date_range=date_range,
            breakdowns=[]
        )

        # Get device breakdown
        device = self.get_campaign_breakdown(
            ad_account_id=ad_account_id,
            date_range=date_range,
            breakdowns=['device_platform']
        )

        # Get demographic breakdown
        demographic = self.get_campaign_breakdown(
            ad_account_id=ad_account_id,
            date_range=date_range,
            breakdowns=['age', 'gender']
        )

        # Get placement breakdown
        placement = self.get_campaign_breakdown(
            ad_account_id=ad_account_id,
            date_range=date_range,
            breakdowns=['publisher_platform', 'platform_position']
        )

        return {
            'overall': overall,
            'by_device': device,
            'by_demographic': demographic,
            'by_placement': placement,
            'generated_at': datetime.utcnow().isoformat()
        }

# Breakdown options
BREAKDOWN_OPTIONS = {
    'time': ['hourly_stats_aggregated_by_advertiser_time_zone'],
    'delivery': ['device_platform', 'publisher_platform', 'platform_position'],
    'action': ['action_type', 'action_destination'],
    'demographic': ['age', 'gender', 'country'],
    'placement': ['impression_device', 'product_id']
}
```

---

## Webhooks

### Webhook Setup

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

class MetaWebhooks:
    """Handle Meta webhook events"""

    def __init__(self, app_secret, verify_token):
        self.app_secret = app_secret
        self.verify_token = verify_token

    def verify_signature(self, payload, signature):
        """Verify webhook signature"""
        expected_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(
            f"sha256={expected_signature}",
            signature
        )

    def handle_verification(self, params):
        """Handle webhook verification challenge"""
        mode = params.get('hub.mode')
        token = params.get('hub.verify_token')
        challenge = params.get('hub.challenge')

        if mode == 'subscribe' and token == self.verify_token:
            return challenge
        return None

@app.route('/webhooks', methods=['GET', 'POST'])
def webhook():
    webhooks = MetaWebhooks(
        app_secret='YOUR_APP_SECRET',
        verify_token='YOUR_VERIFY_TOKEN'
    )

    if request.method == 'GET':
        # Handle verification
        challenge = webhooks.handle_verification(request.args)
        if challenge:
            return challenge, 200
        return 'Verification failed', 403

    if request.method == 'POST':
        # Verify signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not webhooks.verify_signature(request.get_data(), signature):
            return 'Invalid signature', 403

        # Process webhook event
        data = request.json

        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                field = change['field']
                value = change['value']

                # Handle different webhook types
                if field == 'leadgen':
                    handle_lead_event(value)
                elif field == 'page':
                    handle_page_event(value)
                elif field == 'instagram':
                    handle_instagram_event(value)

        return 'OK', 200

def handle_lead_event(value):
    """Handle lead generation webhook"""
    leadgen_id = value.get('leadgen_id')
    page_id = value.get('page_id')
    ad_id = value.get('ad_id')

    # Fetch lead data
    # Process and store lead
    print(f"New lead: {leadgen_id} from ad: {ad_id}")

def handle_page_event(value):
    """Handle page webhook event"""
    pass

def handle_instagram_event(value):
    """Handle Instagram webhook event"""
    pass
```

---

## Rate Limits & Best Practices

### Rate Limits

```python
# Marketing API Rate Limits (per hour)
RATE_LIMITS = {
    'ads_management': {
        'calls_per_hour': 200,
        'calls_per_user_per_hour': 200
    },
    'insights': {
        'calls_per_hour': 200,
        'concurrent_requests': 5
    },
    'graph_api': {
        'calls_per_hour': 200,
        'calls_per_user': 200
    }
}

class RateLimiter:
    """Implement rate limiting for API calls"""

    def __init__(self, max_calls_per_hour=200):
        self.max_calls = max_calls_per_hour
        self.calls = []

    def can_make_call(self):
        """Check if we can make another API call"""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        # Remove old calls
        self.calls = [call_time for call_time in self.calls if call_time > one_hour_ago]

        return len(self.calls) < self.max_calls

    def record_call(self):
        """Record an API call"""
        self.calls.append(datetime.utcnow())

    def wait_if_needed(self):
        """Wait if rate limit is reached"""
        while not self.can_make_call():
            sleep_time = 60  # Wait 1 minute
            print(f"Rate limit reached. Waiting {sleep_time} seconds...")
            time.sleep(sleep_time)
```

### Best Practices

1. **Batch Operations**: Use batch requests for multiple operations
2. **Async Insights**: Use async insights for large date ranges
3. **Field Selection**: Only request fields you need
4. **Pagination**: Handle pagination for large result sets
5. **Error Retry**: Implement exponential backoff for retries
6. **Webhook Events**: Use webhooks instead of polling
7. **Token Management**: Refresh tokens before expiration

---

## Error Handling

```python
class MetaAPIError(Exception):
    """Base exception for Meta API errors"""
    pass

class MetaErrorHandler:
    """Centralized error handling for Meta APIs"""

    ERROR_CODES = {
        1: 'Unknown error',
        2: 'Service temporarily unavailable',
        4: 'API too many calls',
        17: 'User request limit reached',
        32: 'Page request limit reached',
        80001: 'There have been too many calls from this ad account',
        190: 'Access token has expired',
        102: 'API session limit reached'
    }

    @staticmethod
    def handle_error(response):
        """Handle API error response"""
        if response.status_code == 200:
            return response.json()

        error_data = response.json().get('error', {})
        error_code = error_data.get('code')
        error_message = error_data.get('message')
        error_type = error_data.get('type')

        # Log error
        print(f"Meta API Error {error_code}: {error_message}")

        # Handle specific errors
        if error_code in [4, 17, 32, 80001]:
            # Rate limit errors - retry with backoff
            return 'rate_limit'

        elif error_code == 190:
            # Token expired - refresh token
            return 'token_expired'

        elif error_code in [1, 2]:
            # Temporary errors - retry
            return 'retry'

        else:
            # Unrecoverable error
            raise MetaAPIError(f"{error_code}: {error_message}")
```

---

## Testing Strategies

```python
import unittest
from unittest.mock import Mock, patch
import responses

class TestFacebookMarketingAPI(unittest.TestCase):
    """Test Facebook Marketing API integration"""

    def setUp(self):
        self.api = FacebookMarketingAPI(access_token='test_token')

    @responses.activate
    def test_get_ad_accounts(self):
        """Test retrieving ad accounts"""
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v19.0/me/adaccounts',
            json={
                'data': [
                    {'id': 'act_123', 'name': 'Test Account'}
                ]
            },
            status=200
        )

        accounts = self.api.get_ad_accounts()

        self.assertEqual(len(accounts['data']), 1)
        self.assertEqual(accounts['data'][0]['name'], 'Test Account')

    @responses.activate
    def test_create_campaign(self):
        """Test campaign creation"""
        responses.add(
            responses.POST,
            'https://graph.facebook.com/v19.0/act_123/campaigns',
            json={'id': 'campaign_456'},
            status=200
        )

        campaign = self.api.create_campaign(
            ad_account_id='123',
            campaign_config={
                'name': 'Test Campaign',
                'objective': 'OUTCOME_SALES',
                'status': 'PAUSED'
            }
        )

        self.assertEqual(campaign['id'], 'campaign_456')

if __name__ == '__main__':
    unittest.main()
```

---

## Real-World Integration Patterns

### Pattern 1: Automated Campaign Manager

```python
class AutomatedCampaignManager:
    """Automated campaign management with optimization"""

    def __init__(self, api_client):
        self.api = api_client
        self.thresholds = {
            'min_ctr': 0.01,
            'max_cpa': 50,
            'min_roas': 2.0
        }

    def optimize_campaigns(self, ad_account_id):
        """Automatically optimize campaigns based on performance"""
        # Get campaign insights
        insights = self.api.get_ad_account_insights(
            ad_account_id=ad_account_id,
            params={
                'level': 'campaign',
                'fields': 'campaign_id,ctr,cpc,actions,spend',
                'time_range': json.dumps({
                    'since': '7days',
                    'until': 'today'
                })
            }
        )

        actions = []

        for campaign in insights['data']:
            ctr = float(campaign.get('ctr', 0))
            spend = float(campaign.get('spend', 0))

            # Get conversion data
            conversions = 0
            for action in campaign.get('actions', []):
                if action['action_type'] == 'purchase':
                    conversions = int(action['value'])

            cpa = spend / conversions if conversions > 0 else float('inf')

            # Optimization decisions
            if ctr < self.thresholds['min_ctr']:
                # Pause low CTR campaigns
                self.api.update_campaign_status(campaign['campaign_id'], 'PAUSED')
                actions.append({
                    'campaign_id': campaign['campaign_id'],
                    'action': 'paused',
                    'reason': f'Low CTR: {ctr}'
                })

            elif cpa > self.thresholds['max_cpa']:
                # Reduce budget for high CPA campaigns
                actions.append({
                    'campaign_id': campaign['campaign_id'],
                    'action': 'budget_reduced',
                    'reason': f'High CPA: {cpa}'
                })

        return actions
```

### Pattern 2: Multi-Platform Content Publisher

```python
class MultiPlatformPublisher:
    """Publish content across Facebook and Instagram"""

    def __init__(self, fb_api, ig_api):
        self.fb_api = fb_api
        self.ig_api = ig_api

    def publish_everywhere(self, content):
        """Publish content to both platforms"""
        results = {}

        # Publish to Facebook Page
        if content.get('publish_to_facebook'):
            fb_result = self.publish_to_facebook(content)
            results['facebook'] = fb_result

        # Publish to Instagram
        if content.get('publish_to_instagram'):
            ig_result = self.publish_to_instagram(content)
            results['instagram'] = ig_result

        return results

    def publish_to_facebook(self, content):
        """Publish to Facebook Page"""
        # Implementation
        pass

    def publish_to_instagram(self, content):
        """Publish to Instagram"""
        return self.ig_api.publish_photo(
            instagram_account_id=content['ig_account_id'],
            image_url=content['image_url'],
            caption=content['caption']
        )
```

---

## Conclusion

This guide covers comprehensive Meta Marketing API integration for Facebook and Instagram advertising platforms. For production implementations:

1. Implement proper OAuth 2.0 flow with token refresh
2. Use system users for long-term access tokens
3. Implement comprehensive error handling and retry logic
4. Monitor API rate limits and implement queuing
5. Use webhooks for real-time event processing
6. Test thoroughly in sandbox environments
7. Follow Meta's advertising policies and guidelines
8. Implement proper logging and monitoring

For the latest documentation:
- [Meta Marketing API](https://developers.facebook.com/docs/marketing-apis)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Meta Business SDK](https://github.com/facebook/facebook-python-business-sdk)

# Research Collaboration Platform APIs
## ORCID, protocols.io, Zotero, OSF

### ORCID API

**Purpose**: Unique researcher identifiers, publication management

**OAuth2 Authentication**:
```python
import requests

client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
redirect_uri = 'https://yourapp.com/callback'

# Get authorization code (user redirects to this URL)
auth_url = f'https://orcid.org/oauth/authorize?client_id={client_id}&response_type=code&scope=/read-limited&redirect_uri={redirect_uri}'

# Exchange authorization code for access token
token_url = 'https://orcid.org/oauth/token'
data = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'authorization_code',
    'code': 'AUTH_CODE',
    'redirect_uri': redirect_uri
}
response = requests.post(token_url, data=data)
access_token = response.json()['access_token']
orcid = response.json()['orcid']
```

**Fetch Public Profile**:
```python
orcid_id = '0000-0002-1825-0097'
headers = {'Accept': 'application/json'}
url = f'https://pub.orcid.org/v3.0/{orcid_id}/person'

response = requests.get(url, headers=headers)
profile = response.json()

print(f"Name: {profile['name']['given-names']['value']} {profile['name']['family-name']['value']}")
```

**Add Publication to ORCID** (requires member API):
```python
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/vnd.orcid+json'
}

work = {
    'title': {'title': {'value': 'My Research Paper'}},
    'type': 'journal-article',
    'external-ids': {
        'external-id': [{
            'external-id-type': 'doi',
            'external-id-value': '10.1234/example',
            'external-id-relationship': 'self'
        }]
    }
}

url = f'https://api.orcid.org/v3.0/{orcid}/work'
response = requests.post(url, headers=headers, json=work)
```

### protocols.io API

**Purpose**: Protocol sharing and versioning

**Search Protocols**:
```python
import requests

# Public search (no auth required)
query = 'CRISPR'
url = f'https://www.protocols.io/api/v3/protocols?filter=public&key={query}'

response = requests.get(url)
protocols = response.json()['items']

for protocol in protocols:
    print(f"Title: {protocol['title']}")
    print(f"DOI: {protocol['doi']}")
    print(f"URL: {protocol['uri']}")
```

**Get Protocol Details**:
```python
protocol_id = 12345
url = f'https://www.protocols.io/api/v3/protocols/{protocol_id}'

response = requests.get(url)
protocol = response.json()['protocol']

print(f"Steps: {len(protocol['steps'])}")
for step in protocol['steps']:
    print(f"- {step['title']}: {step['description']}")
```

**Create Protocol** (requires authentication):
```python
api_token = 'YOUR_PROTOCOLS_IO_TOKEN'
headers = {'Authorization': f'Bearer {api_token}', 'Content-Type': 'application/json'}

protocol_data = {
    'title': 'My New Protocol',
    'description': 'Protocol description',
    'steps': [
        {'title': 'Step 1', 'description': 'Do this'},
        {'title': 'Step 2', 'description': 'Then do that'}
    ]
}

url = 'https://www.protocols.io/api/v3/protocols'
response = requests.post(url, headers=headers, json=protocol_data)
```

### Zotero API

**Purpose**: Reference management, bibliographies

**Get Library Items**:
```python
import requests

user_id = 'YOUR_USER_ID'  # or group_id for groups
api_key = 'YOUR_ZOTERO_API_KEY'
headers = {'Zotero-API-Key': api_key}

# Get all items
url = f'https://api.zotero.org/users/{user_id}/items'
response = requests.get(url, headers=headers)
items = response.json()

for item in items:
    data = item['data']
    print(f"Title: {data.get('title', 'No title')}")
    print(f"Type: {data['itemType']}")
    print(f"Year: {data.get('date', 'No date')}")
```

**Search Items**:
```python
# Search by title
query = 'machine learning'
url = f'https://api.zotero.org/users/{user_id}/items?q={query}'
response = requests.get(url, headers=headers)
```

**Add Item to Library**:
```python
headers.update({'Content-Type': 'application/json'})

new_item = {
    'itemType': 'journalArticle',
    'title': 'A Research Paper',
    'creators': [
        {'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'}
    ],
    'publicationTitle': 'Nature',
    'volume': '600',
    'pages': '1-10',
    'date': '2024',
    'DOI': '10.1038/example'
}

url = f'https://api.zotero.org/users/{user_id}/items'
response = requests.post(url, headers=headers, json=[new_item])
```

**Export Bibliography**:
```python
# Get items in BibTeX format
url = f'https://api.zotero.org/users/{user_id}/items?format=bibtex'
bibtex = requests.get(url, headers=headers).text

# Or specific citation style
url = f'https://api.zotero.org/users/{user_id}/items?format=bib&style=apa'
bibliography = requests.get(url, headers=headers).text
```

### Open Science Framework (OSF) API

**Purpose**: Project management, preregistration, data sharing

**List Projects**:
```python
import requests

token = 'YOUR_OSF_TOKEN'
headers = {'Authorization': f'Bearer {token}'}

url = 'https://api.osf.io/v2/users/me/nodes/'
response = requests.get(url, headers=headers)

for project in response.json()['data']:
    print(f"Title: {project['attributes']['title']}")
    print(f"Public: {project['attributes']['public']}")
    print(f"Category: {project['attributes']['category']}")
    print(f"URL: {project['links']['html']}")
```

**Create Preregistration**:
```python
# Create a registration (preregistration)
project_id = 'YOUR_PROJECT_ID'
registration_data = {
    'data': {
        'type': 'registrations',
        'attributes': {
            'draft_registration': 'DRAFT_ID',
            'registration_choice': 'immediate'
        }
    }
}

url = f'https://api.osf.io/v2/nodes/{project_id}/registrations/'
response = requests.post(url, headers=headers, json=registration_data)
```

**Upload File**:
```python
# Get upload URL
url = f'https://api.osf.io/v2/nodes/{project_id}/files/osfstorage/'
response = requests.get(url, headers=headers)
upload_url = response.json()['data'][0]['relationships']['upload']['links']['related']['href']

# Upload
with open('manuscript.pdf', 'rb') as f:
    params = {'kind': 'file', 'name': 'manuscript.pdf'}
    response = requests.put(upload_url, headers=headers, params=params, data=f)
```

### GitHub API (for research code)

**Create Repository**:
```python
import requests

token = 'YOUR_GITHUB_TOKEN'
headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

repo_data = {
    'name': 'my-research-project',
    'description': 'Research code for paper X',
    'private': False,
    'has_wiki': True,
    'has_issues': True
}

url = 'https://api.github.com/user/repos'
response = requests.post(url, headers=headers, json=repo_data)
repo_url = response.json()['html_url']
```

**Create Release** (for code archiving):
```python
owner = 'username'
repo = 'my-research-project'

release_data = {
    'tag_name': 'v1.0.0',
    'name': 'Release 1.0.0',
    'body': 'Code accompanying publication in Nature\n\nDOI: 10.1234/example',
    'draft': False,
    'prerelease': False
}

url = f'https://api.github.com/repos/{owner}/{repo}/releases'
response = requests.post(url, headers=headers, json=release_data)
```

**Zenodo-GitHub Integration**:
- Link GitHub repo to Zenodo (zenodo.org/account/settings/github/)
- Create GitHub release
- Zenodo automatically creates DOI
- Citation appears in GitHub README

### Slack API (for team communication)

**Post Message to Channel**:
```python
import requests

webhook_url = 'YOUR_SLACK_WEBHOOK_URL'
message = {
    'text': 'New preprint posted!',
    'attachments': [{
        'title': 'Paper Title',
        'title_link': 'https://arxiv.org/abs/2024.12345',
        'text': 'Our latest results on X',
        'color': 'good'
    }]
}

requests.post(webhook_url, json=message)
```

### Best Practices

**API Keys Security**:
- Store in environment variables, not code
- Use `.env` files (add to `.gitignore`)
- Rotate keys periodically

**Rate Limiting**:
- ORCID: 24 requests/second (public API)
- Zotero: 120 requests/user/hour (authenticated)
- GitHub: 5000 requests/hour (authenticated)
- Implement exponential backoff

**Error Handling**:
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def requests_retry_session(retries=3, backoff_factor=0.3):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Usage
response = requests_retry_session().get('https://api.example.com/data')
```

**Pagination**:
```python
def fetch_all_items(url, headers):
    """Fetch all items across multiple pages."""
    items = []
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        items.extend(data['data'])

        # Next page (OSF, GitHub use 'links.next')
        url = data.get('links', {}).get('next')

    return items
```

### References
- ORCID API: info.orcid.org/documentation/api-tutorials/
- protocols.io API: protocols.io/developers
- Zotero Web API: zotero.org/support/dev/web_api/v3/start
- OSF API: developer.osf.io
- GitHub API: docs.github.com/en/rest

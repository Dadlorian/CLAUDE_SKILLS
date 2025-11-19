# Research Data Repository APIs
## Zenodo, Dryad, Figshare, OSF Integration

### Zenodo API (CERN)

**Authentication**: Personal access token (Settings → Applications → Personal access tokens)

**Create Deposition**:
```python
import requests

access_token = 'YOUR_ACCESS_TOKEN'
headers = {'Content-Type': 'application/json'}
params = {'access_token': access_token}

# Create empty deposition
r = requests.post(
    'https://zenodo.org/api/deposit/depositions',
    params=params,
    headers=headers,
    json={}
)
deposition_id = r.json()['id']
bucket_url = r.json()['links']['bucket']
```

**Upload File**:
```python
filename = 'data.csv'
with open(filename, 'rb') as fp:
    r = requests.put(
        f'{bucket_url}/{filename}',
        data=fp,
        params=params
    )
```

**Add Metadata**:
```python
metadata = {
    'metadata': {
        'title': 'Research Dataset Title',
        'upload_type': 'dataset',
        'description': 'Dataset description',
        'creators': [
            {'name': 'Doe, John', 'orcid': '0000-0002-1234-5678'}
        ],
        'keywords': ['neuroscience', 'fMRI'],
        'license': 'cc-zero',
        'access_right': 'open'
    }
}
r = requests.put(
    f'https://zenodo.org/api/deposit/depositions/{deposition_id}',
    params=params,
    headers=headers,
    json=metadata
)
```

**Publish**:
```python
r = requests.post(
    f'https://zenodo.org/api/deposit/depositions/{deposition_id}/actions/publish',
    params=params
)
doi = r.json()['doi']  # DOI assigned upon publication
```

### Figshare API

**Create Article**:
```python
import requests

token = 'YOUR_FIGSHARE_TOKEN'
headers = {'Authorization': f'token {token}', 'Content-Type': 'application/json'}

article = {
    'title': 'My Research Data',
    'description': 'Description',
    'keywords': ['keyword1', 'keyword2'],
    'categories': [123],  # Figshare category ID
    'defined_type': 'dataset'
}
r = requests.post(
    'https://api.figshare.com/v2/account/articles',
    headers=headers,
    json=article
)
article_id = r.json()['entity_id']
```

**Upload File**:
```python
# Initiate upload
file_info = {'name': 'data.csv', 'size': os.path.getsize('data.csv')}
r = requests.post(
    f'https://api.figshare.com/v2/account/articles/{article_id}/files',
    headers=headers,
    json=file_info
)
upload_url = r.json()['upload_url']

# Upload file
with open('data.csv', 'rb') as f:
    requests.put(upload_url, data=f)

# Complete upload
r = requests.post(f'https://api.figshare.com/v2/account/articles/{article_id}/publish', headers=headers)
```

### Open Science Framework (OSF) API

**Create Project**:
```python
import requests

token = 'YOUR_OSF_TOKEN'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/vnd.api+json'}

project_data = {
    'data': {
        'type': 'nodes',
        'attributes': {
            'title': 'My Research Project',
            'category': 'project',
            'description': 'Project description',
            'public': False
        }
    }
}
r = requests.post('https://api.osf.io/v2/nodes/', headers=headers, json=project_data)
project_id = r.json()['data']['id']
```

**Upload File**:
```python
# Get storage provider
r = requests.get(f'https://api.osf.io/v2/nodes/{project_id}/files/', headers=headers)
storage_url = r.json()['data'][0]['relationships']['upload']['links']['related']['href']

# Upload
with open('data.csv', 'rb') as f:
    r = requests.put(
        f'{storage_url}?kind=file&name=data.csv',
        headers={'Authorization': f'Bearer {token}'},
        data=f
    )
```

### Dryad API

**Create Dataset** (requires institutional membership):
```python
import requests

token = 'YOUR_DRYAD_TOKEN'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

dataset = {
    'title': 'Dataset Title',
    'authors': [
        {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@university.edu',
            'affiliation': 'University Name'
        }
    ],
    'abstract': 'Dataset description',
    'keywords': ['keyword1', 'keyword2']
}
r = requests.post('https://datadryad.org/api/v2/datasets', headers=headers, json=dataset)
dataset_doi = r.json()['identifier']
```

### Best Practices

**Rate Limiting**:
- Zenodo: No strict limit, but be reasonable
- Figshare: 1000 requests/hour
- OSF: 10,000 requests/day
- Implement exponential backoff for 429 (Too Many Requests)

**Large Files**:
- Use chunked uploads (>100 MB)
- Calculate MD5 checksums for verification
- Resume uploads on failure

**Metadata Quality**:
- Always include ORCID for authors
- Use controlled vocabularies for keywords
- Specify clear license (CC0, CC-BY)

**Version Control**:
- Create new version rather than editing published datasets
- Link versions via related identifiers (IsVersionOf, IsPreviousVersionOf)

**Example: Automated Deposition Pipeline**
```python
def deposit_to_zenodo(data_path, metadata):
    """Automated Zenodo deposition."""
    # Create deposition
    deposition = create_deposition()

    # Upload files
    for file in os.listdir(data_path):
        upload_file(deposition['bucket_url'], os.path.join(data_path, file))

    # Add metadata
    update_metadata(deposition['id'], metadata)

    # Publish
    doi = publish_deposition(deposition['id'])

    return doi
```

### References
- Zenodo Developers: developers.zenodo.org
- Figshare API Docs: docs.figshare.com
- OSF API: developer.osf.io
- Dryad API: datadryad.org/stash/api_documentation

# Scientific Database APIs
## PubMed, arXiv, Scopus, Web of Science, Protein Data Bank

### PubMed/NCBI E-utilities

**API Key**: Register at NCBI for 10 requests/second (vs 3/second without)

**Search PubMed**:
```python
from Bio import Entrez
import requests

Entrez.email = 'your_email@example.com'
Entrez.api_key = 'YOUR_API_KEY'

# Search
handle = Entrez.esearch(db='pubmed', term='CRISPR gene editing', retmax=100)
record = Entrez.read(handle)
id_list = record['IdList']  # PMIDs

# Fetch details
handle = Entrez.efetch(db='pubmed', id=id_list, rettype='medline', retmode='text')
records = Medline.parse(handle)
for record in records:
    print(record.get('TI', 'No title'))  # Title
    print(record.get('AB', 'No abstract'))  # Abstract
```

**Batch Download**:
```python
# For large queries, use EPost + EFetch
search_handle = Entrez.esearch(db='pubmed', term='cancer[ti] AND 2023[pdat]', retmax=10000, usehistory='y')
search_results = Entrez.read(search_handle)
webenv = search_results['WebEnv']
query_key = search_results['QueryKey']

# Fetch in batches
batch_size = 500
for start in range(0, int(search_results['Count']), batch_size):
    handle = Entrez.efetch(db='pubmed', webenv=webenv, query_key=query_key,
                          retstart=start, retmax=batch_size, rettype='medline')
    records = Medline.parse(handle)
    # Process records
```

### arXiv API

**Query arXiv**:
```python
import urllib.request as libreq
import feedparser

# Search query
query = 'cat:cs.AI AND ti:transformers'
url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=10'

# Fetch and parse
data = libreq.urlopen(url).read()
feed = feedparser.parse(data)

for entry in feed.entries:
    print(f"Title: {entry.title}")
    print(f"Authors: {', '.join(author.name for author in entry.authors)}")
    print(f"Published: {entry.published}")
    print(f"PDF: {entry.id.replace('/abs/', '/pdf/')}.pdf")
    print(f"Abstract: {entry.summary}")
    print('---')
```

**Categories**:
- Physics: `physics.*`, `astro-ph`, `cond-mat`, `gr-qc`, `hep-*`, `quant-ph`
- Math: `math.*`
- CS: `cs.AI`, `cs.LG`, `cs.CV`, `cs.CL`, etc.
- Quantitative Biology: `q-bio.*`
- Statistics: `stat.*`

### Scopus API (Elsevier)

**Requires**: Institutional subscription, API key

**Search Scopus**:
```python
import requests

api_key = 'YOUR_SCOPUS_API_KEY'
headers = {'X-ELS-APIKey': api_key, 'Accept': 'application/json'}

# Search by keywords
query = 'TITLE-ABS-KEY(machine AND learning AND healthcare)'
url = f'https://api.elsevier.com/content/search/scopus?query={query}&count=25'

response = requests.get(url, headers=headers)
results = response.json()

for entry in results['search-results']['entry']:
    print(f"Title: {entry.get('dc:title')}")
    print(f"Authors: {entry.get('dc:creator')}")
    print(f"Journal: {entry.get('prism:publicationName')}")
    print(f"DOI: {entry.get('prism:doi')}")
    print(f"Citations: {entry.get('citedby-count')}")
```

**Get Citation Count**:
```python
# By DOI
doi = '10.1038/s41586-021-03819-2'
url = f'https://api.elsevier.com/content/search/scopus?query=DOI({doi})'
response = requests.get(url, headers=headers)
citations = response.json()['search-results']['entry'][0]['citedby-count']
```

### Web of Science API (Clarivate)

**Requires**: Institutional subscription

**Search WoS**:
```python
import requests

api_key = 'YOUR_WOS_API_KEY'
headers = {'X-ApiKey': api_key}

query = {
    'databaseId': 'WOS',
    'userQuery': 'TS=(artificial intelligence)',
    'count': 10,
    'firstRecord': 1
}

url = 'https://api.clarivate.com/api/wos'
response = requests.post(f'{url}?databaseId=WOS&lang=en&edition=SCI', headers=headers, json=query)
results = response.json()
```

### Protein Data Bank (PDB) API

**Search Structures**:
```python
import requests

# Text search
query = {
    'query': {
        'type': 'terminal',
        'service': 'text',
        'parameters': {
            'value': 'hemoglobin'
        }
    },
    'return_type': 'entry'
}

url = 'https://search.rcsb.org/rcsbsearch/v2/query'
response = requests.post(url, json=query)
pdb_ids = [entry['identifier'] for entry in response.json()['result_set']]

# Download PDB file
pdb_id = '1HHO'  # Hemoglobin
pdb_url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
pdb_file = requests.get(pdb_url).text
```

**Advanced Query** (sequence similarity):
```python
query = {
    'query': {
        'type': 'terminal',
        'service': 'sequence',
        'parameters': {
            'evalue_cutoff': 1,
            'identity_cutoff': 0.9,
            'sequence_type': 'protein',
            'value': 'MKALIVLGLVLLSVTVQGKVFERCELARTLKRLGMDGYRGILANWMCLATKAS'
        }
    },
    'return_type': 'polymer_entity'
}
response = requests.post('https://search.rcsb.org/rcsbsearch/v2/query', json=query)
```

### GenBank/NCBI Sequence Databases

**Fetch Sequence**:
```python
from Bio import Entrez, SeqIO

Entrez.email = 'your_email@example.com'

# Fetch GenBank record
handle = Entrez.efetch(db='nucleotide', id='NM_000518', rettype='gb', retmode='text')
record = SeqIO.read(handle, 'genbank')

print(f"ID: {record.id}")
print(f"Description: {record.description}")
print(f"Sequence length: {len(record.seq)}")
print(f"Features: {len(record.features)}")
```

**BLAST Search** (programmatically):
```python
from Bio.Blast import NCBIWWW, NCBIXML

# Run BLAST
sequence = 'ATGGCGATG...'  # Your sequence
result_handle = NCBIWWW.qblast('blastn', 'nt', sequence)

# Parse results
blast_records = NCBIXML.parse(result_handle)
for blast_record in blast_records:
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            if hsp.expect < 0.001:
                print(f"Hit: {alignment.title}")
                print(f"E-value: {hsp.expect}")
                print(f"Identity: {hsp.identities}/{hsp.align_length}")
```

### CrossRef API (DOI Metadata)

**Get Publication Metadata**:
```python
import requests

doi = '10.1038/nature12373'
url = f'https://api.crossref.org/works/{doi}'
headers = {'User-Agent': 'MyResearchTool/1.0 (mailto:email@example.com)'}

response = requests.get(url, headers=headers)
metadata = response.json()['message']

print(f"Title: {metadata['title'][0]}")
print(f"Authors: {', '.join([f\"{a['given']} {a['family']}\" for a in metadata['author']])}")
print(f"Published: {metadata['published-print']['date-parts'][0]}")
print(f"Journal: {metadata['container-title'][0]}")
print(f"Citations: {metadata.get('is-referenced-by-count', 0)}")
```

### Rate Limiting Best Practices

**NCBI**: 10 requests/second with API key, 3/second without
- Use `time.sleep(0.34)` between requests (3/second)
- Use EPost for large batches

**arXiv**: 1 request every 3 seconds
- `time.sleep(3)` between requests

**Scopus/Web of Science**: Varies by subscription
- Check response headers for rate limit info
- Implement exponential backoff

**Example: Rate Limiter**
```python
import time
from functools import wraps

def rate_limit(calls_per_second=3):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=3)
def fetch_pubmed(pmid):
    # API call
    pass
```

### References
- NCBI E-utilities: ncbi.nlm.nih.gov/books/NBK25501/
- arXiv API: arxiv.org/help/api
- Scopus APIs: dev.elsevier.com
- Web of Science: developer.clarivate.com/apis/wos
- PDB Search API: search.rcsb.org
- CrossRef REST API: github.com/CrossRef/rest-api-doc

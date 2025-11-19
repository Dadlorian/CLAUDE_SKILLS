# LIMS API Integration Guide
## Laboratory Information Management System APIs

### Overview
Integration patterns for major LIMS platforms: LabWare, STARLIMS, Thermo SampleManager, Benchling

### REST API Standards

**Authentication**: OAuth2, API keys
**Endpoints**: RESTful design (GET, POST, PUT, DELETE)
**Response Format**: JSON, pagination for large datasets
**Rate Limiting**: 100-1000 requests/minute

### Sample LIMS Operations

#### Sample Registration
```python
import requests

# LabWare LIMS API
headers = {'Authorization': f'Bearer {api_token}'}
sample_data = {
    'sample_id': 'SAMP-2024-001',
    'sample_type': 'blood_serum',
    'collection_date': '2024-11-19',
    'patient_id': 'PT-12345',
    'tests_requested': ['CBC', 'metabolic_panel']
}
response = requests.post(
    'https://lims.lab.org/api/v1/samples',
    headers=headers,
    json=sample_data
)
```

#### Result Entry
```python
result_data = {
    'sample_id': 'SAMP-2024-001',
    'test': 'glucose',
    'value': 95.2,
    'units': 'mg/dL',
    'timestamp': '2024-11-19T14:30:00Z',
    'analyst': 'analyst_id',
    'instrument': 'INST-001'
}
requests.post('https://lims.lab.org/api/v1/results', headers=headers, json=result_data)
```

### Instrument Integration
- **Middleware**: LabVIEW, Python (PyVISA)
- **Protocols**: TCP/IP, RS-232, USB
- **Data formats**: CSV, XML, ASTM E1381

### Best Practices
- Validate data before submission
- Handle transient failures (retry with exponential backoff)
- Log all API calls for audit trail
- Use webhooks for real-time updates

### Compliance
- **21 CFR Part 11**: Electronic signatures, audit trails
- **ISO 17025**: Laboratory quality management
- **HIPAA**: De-identify patient data in test environments

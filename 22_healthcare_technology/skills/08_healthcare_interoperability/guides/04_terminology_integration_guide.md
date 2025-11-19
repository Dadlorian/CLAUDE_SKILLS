# Terminology Integration Guide (SNOMED CT, LOINC, RxNorm)

## Step 1: Set Up Terminology Server

### Option 1: Use Public APIs

#### SNOMED CT Browser API
```python
import requests

class SNOMEDClient:
    def __init__(self):
        self.base_url = "https://browser.ihtsdotools.org/snowstorm/snomed-ct"

    def lookup_concept(self, code, language="en"):
        """Look up SNOMED concept"""
        url = f"{self.base_url}/browser/concepts/{code}"
        params = {"language": language}

        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None

    def search_concepts(self, term, language="en"):
        """Search for SNOMED concepts"""
        url = f"{self.base_url}/browser/concepts"
        params = {
            "term": term,
            "language": language,
            "returnLimit": 50
        }

        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None

# Usage
snomed = SNOMEDClient()

# Look up diabetes
concept = snomed.lookup_concept("250171008")
print(f"Concept: {concept['pt']['term']}")

# Search for pneumonia
results = snomed.search_concepts("pneumonia")
for item in results.get("items", []):
    print(f"{item['id']}: {item['term']}")
```

#### LOINC API
```python
class LOINCClient:
    def __init__(self, api_key):
        self.base_url = "https://loinc.org/api/search"
        self.api_key = api_key

    def search_loinc(self, search_term):
        """Search for LOINC codes"""
        params = {
            "q": search_term,
            "api_key": self.api_key
        }

        response = requests.get(self.base_url, params=params)
        return response.json() if response.status_code == 200 else None

    def get_loinc_details(self, loinc_code):
        """Get LOINC code details"""
        url = f"https://loinc.org/api/{loinc_code}"

        response = requests.get(url, params={"api_key": self.api_key})
        return response.json() if response.status_code == 200 else None

# Usage
loinc = LOINCClient(api_key="your_api_key")

# Search for glucose
results = loinc.search_loinc("glucose")
for item in results.get("documents", []):
    print(f"{item['loinc_num']}: {item['display_name']}")

# Get details for 2345-7
details = loinc.get_loinc_details("2345-7")
print(details)
```

#### RxNorm API
```python
class RxNormClient:
    def __init__(self):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"

    def search_by_name(self, drug_name):
        """Search for drug by name"""
        url = f"{self.base_url}/rxcui"
        params = {"name": drug_name}

        response = requests.get(url, params=params)
        data = response.json()

        if "idGroup" in data and data["idGroup"]["rxUris"]:
            return [uri.split("/")[-1] for uri in data["idGroup"]["rxUris"]]

        return []

    def get_drug_info(self, rxcui):
        """Get drug information"""
        url = f"{self.base_url}/rxcui/{rxcui}/properties"

        response = requests.get(url)
        return response.json().get("properties", {})

    def find_alternatives(self, rxcui):
        """Find alternative medications"""
        url = f"{self.base_url}/rxcui/{rxcui}/allrelatives"

        response = requests.get(url)
        return response.json()

    def check_interactions(self, rxcui_list):
        """Check drug interactions"""
        url = f"{self.base_url}/interaction"
        params = {"rxcuis": "+".join(rxcui_list)}

        response = requests.get(url, params=params)
        return response.json()

# Usage
rxnorm = RxNormClient()

# Search for metformin
cuis = rxnorm.search_by_name("metformin")
print(f"Metformin RxCUI: {cuis}")

# Get drug info
if cuis:
    info = rxnorm.get_drug_info(cuis[0])
    print(f"Drug Info: {info}")

# Check interactions
interactions = rxnorm.check_interactions(["860220", "314076"])
print(f"Interactions: {interactions}")
```

### Option 2: Self-Hosted Terminology Server (Snowstorm)

#### Docker Setup
```yaml
version: '3.8'

services:
  snowstorm:
    image: snomedinternational/snowstorm:latest
    ports:
      - "8080:8080"
    environment:
      SNOMED_VERSION: "20240401"
      JAVA_OPTS: "-Xmx4g"
    volumes:
      - snowstorm_data:/data

volumes:
  snowstorm_data:
```

#### Snowstorm API Usage
```python
class SnowstormClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url

    def lookup_concept(self, code):
        """Look up concept via FHIR"""
        url = f"{self.base_url}/fhir/CodeSystem/$lookup"
        params = {
            "system": "http://snomed.info/sct",
            "code": code
        }

        response = requests.get(url, params=params)
        return response.json()

    def expand_value_set(self, value_set_url):
        """Expand value set"""
        url = f"{self.base_url}/fhir/ValueSet/$expand"
        params = {"url": value_set_url}

        response = requests.get(url, params=params)
        return response.json()

    def translate_concept(self, code, target_system):
        """Translate concept to target system"""
        url = f"{self.base_url}/fhir/ConceptMap/$translate"
        params = {
            "system": "http://snomed.info/sct",
            "code": code,
            "target": target_system
        }

        response = requests.get(url, params=params)
        return response.json()

# Usage
snowstorm = SnowstormClient()

# Lookup concept
result = snowstorm.lookup_concept("80891009")
print(f"Display: {result['expansion']['contains'][0]['display']}")
```

## Step 2: Build Code Mapping Table

### Database Schema
```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CodeMapping(Base):
    __tablename__ = "code_mappings"

    id = Column(Integer, primary_key=True)
    source_system = Column(String)  # e.g., "local", "icd10"
    source_code = Column(String)
    target_system = Column(String)  # e.g., "snomed", "loinc"
    target_code = Column(String)
    target_display = Column(String)
    accuracy = Column(Integer)  # 1-5 confidence rating
    notes = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

# Example mappings
mappings = [
    {
        "source_system": "local",
        "source_code": "DM2",
        "target_system": "snomed",
        "target_code": "44054006",
        "target_display": "Diabetes mellitus type 2"
    },
    {
        "source_system": "local",
        "source_code": "HTN",
        "target_system": "snomed",
        "target_code": "38341003",
        "target_display": "Hypertension"
    },
]
```

### Mapping Service
```python
class CodeMappingService:
    def __init__(self, db_session):
        self.db = db_session
        self.terminology_client = SnowstormClient()

    def map_code(self, source_code, source_system, target_system):
        """Map code to target system"""
        # Check mapping table
        mapping = self.db.query(CodeMapping).filter(
            CodeMapping.source_system == source_system,
            CodeMapping.source_code == source_code,
            CodeMapping.target_system == target_system,
            CodeMapping.is_active == True
        ).first()

        if mapping:
            return {
                "code": mapping.target_code,
                "display": mapping.target_display,
                "source": "cached"
            }

        # If not cached, attempt dynamic mapping
        if target_system == "snomed":
            result = self.search_snomed_equivalent(source_code)
            if result:
                return result

        return {
            "code": None,
            "display": None,
            "error": "No mapping found"
        }

    def search_snomed_equivalent(self, term):
        """Search SNOMED for equivalent concept"""
        snomed = SNOMEDClient()
        results = snomed.search_concepts(term)

        if results and results.get("items"):
            item = results["items"][0]
            return {
                "code": item["id"],
                "display": item["term"],
                "source": "snomed_search"
            }

        return None

    def validate_code(self, code, system):
        """Validate code against terminology system"""
        if system == "snomed":
            return self.validate_snomed_code(code)
        elif system == "loinc":
            return self.validate_loinc_code(code)
        elif system == "rxnorm":
            return self.validate_rxnorm_code(code)

        return False

    def validate_snomed_code(self, code):
        """Validate SNOMED code"""
        snomed = SNOMEDClient()
        result = snomed.lookup_concept(code)
        return result is not None

    def validate_loinc_code(self, code):
        """Validate LOINC code"""
        loinc = LOINCClient(api_key="your_api_key")
        result = loinc.get_loinc_details(code)
        return result is not None

    def validate_rxnorm_code(self, code):
        """Validate RxNorm code"""
        rxnorm = RxNormClient()
        info = rxnorm.get_drug_info(code)
        return info is not None
```

## Step 3: Terminology Validation in FHIR

```python
class FHIRTerminologyValidator:
    def __init__(self, mapping_service):
        self.mapping = mapping_service

    def validate_observation(self, observation):
        """Validate observation codes"""
        errors = []

        # Check LOINC code
        if "code" in observation:
            code = observation["code"]["coding"][0]["code"]
            system = observation["code"]["coding"][0]["system"]

            if system == "http://loinc.org":
                if not self.mapping.validate_code(code, "loinc"):
                    errors.append(f"Invalid LOINC code: {code}")

        # Validate value if present
        if "valueQuantity" in observation:
            value = observation["valueQuantity"]["value"]
            unit = observation["valueQuantity"]["unit"]

            if not self.is_valid_unit(unit):
                errors.append(f"Invalid unit: {unit}")

        return len(errors) == 0, errors

    def validate_medication_request(self, med_request):
        """Validate medication codes"""
        errors = []

        # Check RxNorm code
        coding = med_request["medicationCodeableConcept"]["coding"][0]
        code = coding["code"]
        system = coding["system"]

        if system == "http://www.nlm.nih.gov/research/umls/rxnorm":
            if not self.mapping.validate_code(code, "rxnorm"):
                errors.append(f"Invalid RxNorm code: {code}")

        return len(errors) == 0, errors

    def validate_condition(self, condition):
        """Validate condition codes"""
        errors = []

        # Check SNOMED code
        coding = condition["code"]["coding"][0]
        code = coding["code"]
        system = coding["system"]

        if system == "http://snomed.info/sct":
            if not self.mapping.validate_code(code, "snomed"):
                errors.append(f"Invalid SNOMED code: {code}")

        return len(errors) == 0, errors

    def is_valid_unit(self, unit):
        """Check if unit of measure is valid"""
        valid_units = {
            "mg/dL": "mg/dL",
            "mmol/L": "mmol/L",
            "mg": "mg",
            "mL": "mL",
            "%": "%",
        }
        return unit in valid_units
```

## Step 4: Value Set Creation

### FHIR Value Set Example
```json
{
  "resourceType": "ValueSet",
  "id": "diabetes-conditions",
  "title": "Diabetes Mellitus Codes",
  "url": "http://hospital.example.com/ValueSet/diabetes-conditions",
  "compose": {
    "include": [
      {
        "system": "http://snomed.info/sct",
        "filter": [
          {
            "property": "concept",
            "op": "is-a",
            "value": "73211009"
          }
        ]
      }
    ]
  }
}
```

### Value Set Service
```python
class ValueSetService:
    def __init__(self, terminology_client):
        self.terminology = terminology_client

    def expand_value_set(self, valueset_url):
        """Expand value set to get all codes"""
        result = self.terminology.expand_value_set(valueset_url)

        codes = []
        for item in result.get("expansion", {}).get("contains", []):
            codes.append({
                "code": item["code"],
                "display": item["display"],
                "system": item["system"]
            })

        return codes

    def validate_code_in_valueset(self, code, valueset_url):
        """Check if code is in value set"""
        codes = self.expand_value_set(valueset_url)
        return any(c["code"] == code for c in codes)
```

## Step 5: Caching Strategy

```python
from redis import Redis
import json

class CachedTerminologyService:
    def __init__(self, terminology_client, cache_ttl=86400):
        self.terminology = terminology_client
        self.cache = Redis(host='localhost', port=6379)
        self.ttl = cache_ttl

    def lookup_concept(self, code, system="snomed"):
        """Look up concept with caching"""
        cache_key = f"concept:{system}:{code}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fetch from terminology server
        result = self.terminology.lookup_concept(code)

        if result:
            # Cache result
            self.cache.setex(cache_key, self.ttl, json.dumps(result))

        return result

    def search_concepts(self, term, system="snomed"):
        """Search with caching"""
        cache_key = f"search:{system}:{term}"

        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        result = self.terminology.search_concepts(term)

        if result:
            self.cache.setex(cache_key, self.ttl, json.dumps(result))

        return result
```

## Testing Terminology Integration

```python
import unittest

class TestTerminologyIntegration(unittest.TestCase):
    def setUp(self):
        self.mapping = CodeMappingService(db_session)
        self.validator = FHIRTerminologyValidator(self.mapping)

    def test_map_code(self):
        """Test code mapping"""
        result = self.mapping.map_code("DM2", "local", "snomed")
        self.assertIsNotNone(result["code"])
        self.assertEqual(result["code"], "44054006")

    def test_validate_snomed_code(self):
        """Test SNOMED code validation"""
        valid = self.mapping.validate_code("80891009", "snomed")
        self.assertTrue(valid)

    def test_validate_loinc_code(self):
        """Test LOINC code validation"""
        valid = self.mapping.validate_code("2345-7", "loinc")
        self.assertTrue(valid)

    def test_fhir_observation_validation(self):
        """Test FHIR observation validation"""
        obs = {
            "code": {
                "coding": [{"system": "http://loinc.org", "code": "2345-7"}]
            },
            "valueQuantity": {"value": 95, "unit": "mg/dL"}
        }

        valid, errors = self.validator.validate_observation(obs)
        self.assertTrue(valid)

if __name__ == '__main__':
    unittest.main()
```

## Next Steps

1. Set up terminology server in your environment
2. Create comprehensive code mappings
3. Implement caching for performance
4. Set up regular terminology updates
5. Train staff on terminology usage

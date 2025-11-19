# FHIR R4 API Setup & Implementation Guide

## Step 1: Choose a FHIR Server

### Option 1: HAPI FHIR (Java)

#### Installation
```bash
# Clone repository
git clone https://github.com/hapifhir/hapi-fhir-jpaserver-starter.git
cd hapi-fhir-jpaserver-starter

# Build
mvn clean install -DskipTests

# Run
java -jar target/ROOT.war
```

#### Configuration (application.yaml)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/hapi_fhir
    username: hapi_fhir
    password: hapi_password
    driverClassName: org.postgresql.Driver

  jpa:
    hibernate:
      ddl-auto: update
    database-platform: org.hibernate.dialect.PostgreSQL10Dialect

hapi:
  fhir:
    version: R4
    server_address: http://localhost:8080/fhir/
    rest_server_address: http://localhost:8080/fhir/
    validation:
      enabled: true
```

### Option 2: Python FastAPI

```bash
pip install fastapi
pip install fhirclient
pip install python-multipart
```

#### Basic Server
```python
from fastapi import FastAPI, HTTPException
from fhirclient.models.patient import Patient
import json

app = FastAPI()

# In-memory storage (replace with database)
patients_db = {}

@app.get("/fhir/Patient/{patient_id}")
async def get_patient(patient_id: str):
    """Get patient by ID"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patients_db[patient_id]

@app.post("/fhir/Patient")
async def create_patient(patient: dict):
    """Create new patient"""
    patient_id = str(len(patients_db) + 1)
    patient["id"] = patient_id
    patients_db[patient_id] = patient
    return {"id": patient_id}

@app.get("/fhir/Patient")
async def search_patients(family: str = None, given: str = None):
    """Search patients"""
    results = []
    for patient_id, patient in patients_db.items():
        if family and family.lower() not in patient.get("name", [{}])[0].get("family", "").lower():
            continue
        results.append(patient)
    return {"resourceType": "Bundle", "entry": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 2: Set Up Patient Resource Endpoint

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class HumanName(BaseModel):
    use: Optional[str] = None
    family: str
    given: List[str] = []

class Address(BaseModel):
    use: Optional[str] = None
    type: Optional[str] = None
    text: Optional[str] = None
    line: List[str] = []
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None

class Identifier(BaseModel):
    system: str
    value: str
    type: Optional[str] = None

class Patient(BaseModel):
    resourceType: str = "Patient"
    id: Optional[str] = None
    identifier: List[Identifier] = []
    name: List[HumanName] = []
    telecom: Optional[List[dict]] = None
    gender: Optional[str] = None  # male, female, other, unknown
    birthDate: Optional[date] = None
    address: List[Address] = []
    maritalStatus: Optional[dict] = None
    contact: Optional[List[dict]] = None
    generalPractitioner: Optional[List[dict]] = None

# Store implementation
from sqlalchemy import Column, String, Date, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True)
    mrn = Column(String, unique=True)
    family_name = Column(String)
    given_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    json_data = Column(String)  # Full FHIR JSON
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Endpoints
@app.post("/fhir/Patient")
async def create_patient(patient: Patient, db: Session = Depends(get_db)):
    """Create patient - POST /fhir/Patient"""
    import uuid
    from datetime import datetime

    patient_id = str(uuid.uuid4())
    patient.id = patient_id

    db_patient = PatientDB(
        id=patient_id,
        mrn=patient.identifier[0].value if patient.identifier else None,
        family_name=patient.name[0].family if patient.name else None,
        given_name=patient.name[0].given[0] if patient.name and patient.name[0].given else None,
        dob=patient.birthDate,
        gender=patient.gender,
        json_data=patient.json(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(db_patient)
    db.commit()

    return {"resourceType": "Patient", "id": patient_id}

@app.get("/fhir/Patient/{patient_id}")
async def read_patient(patient_id: str, db: Session = Depends(get_db)):
    """Read patient - GET /fhir/Patient/[id]"""
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return json.loads(patient.json_data)

@app.put("/fhir/Patient/{patient_id}")
async def update_patient(patient_id: str, patient: Patient, db: Session = Depends(get_db)):
    """Update patient - PUT /fhir/Patient/[id]"""
    from datetime import datetime

    db_patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Update fields
    db_patient.json_data = patient.json()
    db_patient.updated_at = datetime.utcnow()

    db.commit()

    return {"resourceType": "Patient", "id": patient_id}

@app.delete("/fhir/Patient/{patient_id}")
async def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    """Delete patient - DELETE /fhir/Patient/[id]"""
    db_patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(db_patient)
    db.commit()

    return {"status": "deleted"}

@app.get("/fhir/Patient")
async def search_patients(
    family: Optional[str] = None,
    given: Optional[str] = None,
    birthdate: Optional[str] = None,
    _count: int = 50,
    _offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search patients - GET /fhir/Patient?search=criteria"""
    query = db.query(PatientDB)

    if family:
        query = query.filter(PatientDB.family_name.ilike(f"%{family}%"))

    if given:
        query = query.filter(PatientDB.given_name.ilike(f"%{given}%"))

    if birthdate:
        from datetime import datetime
        bd = datetime.strptime(birthdate, "%Y-%m-%d").date()
        query = query.filter(PatientDB.dob == bd)

    total = query.count()
    patients = query.offset(_offset).limit(_count).all()

    entries = [json.loads(p.json_data) for p in patients]

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": total,
        "entry": entries
    }
```

## Step 3: Add Observation Resource

```python
class Observation(BaseModel):
    resourceType: str = "Observation"
    id: Optional[str] = None
    status: str  # registered, preliminary, final, amended
    code: dict  # LOINC code
    subject: dict  # Reference to Patient
    effectiveDateTime: Optional[str] = None
    issued: Optional[str] = None
    performer: Optional[List[dict]] = None
    valueQuantity: Optional[dict] = None
    valueCodeableConcept: Optional[dict] = None
    dataAbsentReason: Optional[dict] = None
    interpretation: Optional[dict] = None
    referenceRange: Optional[List[dict]] = None

class ObservationDB(Base):
    __tablename__ = "observations"

    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    code = Column(String)  # LOINC code
    value = Column(String)
    unit = Column(String)
    json_data = Column(String)
    created_at = Column(DateTime)

@app.post("/fhir/Observation")
async def create_observation(obs: Observation, db: Session = Depends(get_db)):
    """Create observation"""
    import uuid
    from datetime import datetime

    obs_id = str(uuid.uuid4())
    obs.id = obs_id

    db_obs = ObservationDB(
        id=obs_id,
        patient_id=obs.subject.get("reference", "").split("/")[-1],
        code=obs.code.get("coding", [{}])[0].get("code"),
        value=str(obs.valueQuantity.get("value")) if obs.valueQuantity else None,
        unit=obs.valueQuantity.get("unit") if obs.valueQuantity else None,
        json_data=obs.json(),
        created_at=datetime.utcnow()
    )

    db.add(db_obs)
    db.commit()

    return {"resourceType": "Observation", "id": obs_id}

@app.get("/fhir/Observation")
async def search_observations(
    patient: str = None,
    code: str = None,
    date: str = None,
    _count: int = 50,
    db: Session = Depends(get_db)
):
    """Search observations"""
    query = db.query(ObservationDB)

    if patient:
        query = query.filter(ObservationDB.patient_id == patient)

    if code:
        query = query.filter(ObservationDB.code == code)

    if date:
        from datetime import datetime
        d = datetime.strptime(date, "%Y-%m-%d").date()
        query = query.filter(db.func.date(ObservationDB.created_at) == d)

    observations = query.limit(_count).all()

    entries = [json.loads(o.json_data) for o in observations]

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries
    }
```

## Step 4: Testing Your FHIR API

```python
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_patient():
    """Test patient creation"""
    patient_data = {
        "resourceType": "Patient",
        "name": [{"family": "Doe", "given": ["John"]}],
        "birthDate": "1970-01-01",
        "gender": "male",
        "identifier": [{"system": "http://hospital/mrn", "value": "12345"}]
    }

    response = client.post("/fhir/Patient", json=patient_data)
    assert response.status_code == 200
    assert "id" in response.json()

def test_read_patient():
    """Test patient read"""
    response = client.get("/fhir/Patient/123")
    assert response.status_code in [200, 404]

def test_search_patients():
    """Test patient search"""
    response = client.get("/fhir/Patient?family=Doe")
    assert response.status_code == 200
    assert response.json()["resourceType"] == "Bundle"

def test_create_observation():
    """Test observation creation"""
    obs_data = {
        "resourceType": "Observation",
        "status": "final",
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "2345-7"}]
        },
        "subject": {"reference": "Patient/123"},
        "valueQuantity": {"value": 95, "unit": "mg/dL"}
    }

    response = client.post("/fhir/Observation", json=obs_data)
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
```

## Step 5: Deploy to Production

### Docker Setup
```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  fhir-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/fhir
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: fhir
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Deploy
```bash
docker-compose up -d
```

## Next Steps

1. Configure authentication (OAuth2, API Key)
2. Add conformance statement
3. Implement bulk operations
4. Set up monitoring and logging
5. Add API documentation (Swagger)

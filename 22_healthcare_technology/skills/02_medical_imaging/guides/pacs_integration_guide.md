# PACS Integration Guide

## Overview
This guide covers integrating applications with PACS systems using DICOM, DICOMweb, and other standards.

## DICOM Network Integration

### Configuring DICOM Nodes
```yaml
# dicom_config.yaml
ae_title: MY_APP
port: 11112
max_pdu_size: 16384

remote_nodes:
  - name: MAIN_PACS
    ae_title: PACS_SCP
    host: 192.168.1.100
    port: 104
    
  - name: BACKUP_PACS
    ae_title: BACKUP_SCP
    host: 192.168.1.101
    port: 104
```

### Send Images to PACS
```python
from pynetdicom import AE, StoragePresentationContexts
import pydicom
import yaml

# Load config
with open('dicom_config.yaml') as f:
    config = yaml.safe_load(f)

# Create AE
ae = AE(ae_title=config['ae_title'])
ae.requested_contexts = StoragePresentationContexts

# Send study to PACS
def send_study_to_pacs(dicom_files, pacs_name='MAIN_PACS'):
    pacs = next(n for n in config['remote_nodes'] if n['name'] == pacs_name)
    
    assoc = ae.associate(pacs['host'], pacs['port'], ae_title=pacs['ae_title'])
    
    if assoc.is_established:
        for dcm_file in dicom_files:
            ds = pydicom.dcmread(dcm_file)
            status = assoc.send_c_store(ds)
            if status and status.Status == 0x0000:
                print(f"Sent {dcm_file}")
            else:
                print(f"Failed: {dcm_file}")
        
        assoc.release()
```

### Query PACS for Studies
```python
from pynetdicom import AE
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
from pydicom.dataset import Dataset

def query_pacs_studies(patient_id=None, study_date=None, modality=None):
    ae = AE(ae_title='QUERY_SCU')
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
    
    # Build query
    ds = Dataset()
    ds.QueryRetrieveLevel = 'STUDY'
    ds.PatientID = patient_id or ''
    ds.StudyDate = study_date or ''
    ds.ModalitiesInStudy = modality or ''
    
    # Return keys
    ds.PatientName = ''
    ds.StudyInstanceUID = ''
    ds.StudyDescription = ''
    ds.AccessionNumber = ''
    ds.StudyDate = ''
    ds.NumberOfStudyRelatedInstances = ''
    
    assoc = ae.associate('192.168.1.100', 104, ae_title='PACS_SCP')
    
    results = []
    if assoc.is_established:
        responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        
        for (status, identifier) in responses:
            if status and status.Status in (0xFF00, 0xFF01):
                results.append({
                    'patient_name': str(identifier.PatientName),
                    'patient_id': str(identifier.PatientID),
                    'study_uid': str(identifier.StudyInstanceUID),
                    'study_date': str(identifier.StudyDate),
                    'study_description': str(identifier.StudyDescription),
                    'num_images': int(identifier.NumberOfStudyRelatedInstances)
                })
        
        assoc.release()
    
    return results
```

## DICOMweb Integration

### RESTful Image Access
```python
import requests
from requests.auth import HTTPBasicAuth

class DICOMwebClient:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password) if username else None
    
    def search_studies(self, patient_id=None, study_date=None):
        """QIDO-RS: Query for studies"""
        url = f"{self.base_url}/studies"
        params = {}
        if patient_id:
            params['PatientID'] = patient_id
        if study_date:
            params['StudyDate'] = study_date
        
        response = requests.get(url, params=params, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def retrieve_study(self, study_uid, output_dir):
        """WADO-RS: Retrieve entire study"""
        url = f"{self.base_url}/studies/{study_uid}"
        headers = {'Accept': 'multipart/related; type=application/dicom'}
        
        response = requests.get(url, headers=headers, auth=self.auth, stream=True)
        response.raise_for_status()
        
        # Parse multipart response and save instances
        # (Implementation depends on multipart library)
        return output_dir
    
    def retrieve_metadata(self, study_uid, series_uid=None):
        """Retrieve DICOM metadata as JSON"""
        if series_uid:
            url = f"{self.base_url}/studies/{study_uid}/series/{series_uid}/metadata"
        else:
            url = f"{self.base_url}/studies/{study_uid}/metadata"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def store_instances(self, dicom_files, study_uid=None):
        """STOW-RS: Store DICOM instances"""
        url = f"{self.base_url}/studies"
        if study_uid:
            url += f"/{study_uid}"
        
        # Build multipart request
        files = []
        for dcm_file in dicom_files:
            with open(dcm_file, 'rb') as f:
                files.append(('file', (dcm_file, f.read(), 'application/dicom')))
        
        headers = {'Accept': 'application/dicom+xml'}
        response = requests.post(url, files=files, headers=headers, auth=self.auth)
        response.raise_for_status()
        return response.text

# Usage
client = DICOMwebClient('http://pacs.hospital.org:8080/dcm4chee-arc/aets/DCM4CHEE')
studies = client.search_studies(patient_id='12345')
metadata = client.retrieve_metadata(studies[0]['0020000D']['Value'][0])
```

## Database Integration

### Store DICOM Metadata
```python
import sqlite3
import pydicom
from pathlib import Path

class DICOMDatabase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                patient_name TEXT,
                birth_date TEXT,
                sex TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS studies (
                study_uid TEXT PRIMARY KEY,
                patient_id TEXT,
                study_date TEXT,
                study_time TEXT,
                accession_number TEXT,
                study_description TEXT,
                modalities TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS series (
                series_uid TEXT PRIMARY KEY,
                study_uid TEXT,
                series_number INTEGER,
                modality TEXT,
                series_description TEXT,
                FOREIGN KEY (study_uid) REFERENCES studies(study_uid)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS instances (
                sop_uid TEXT PRIMARY KEY,
                series_uid TEXT,
                instance_number INTEGER,
                file_path TEXT,
                FOREIGN KEY (series_uid) REFERENCES series(series_uid)
            )
        ''')
        
        self.conn.commit()
    
    def index_dicom_file(self, filepath):
        ds = pydicom.dcmread(filepath, stop_before_pixels=True)
        
        # Insert patient
        self.conn.execute('''
            INSERT OR REPLACE INTO patients VALUES (?, ?, ?, ?)
        ''', (
            ds.PatientID,
            str(ds.PatientName),
            ds.get('PatientBirthDate', ''),
            ds.get('PatientSex', '')
        ))
        
        # Insert study
        self.conn.execute('''
            INSERT OR REPLACE INTO studies VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            ds.StudyInstanceUID,
            ds.PatientID,
            ds.get('StudyDate', ''),
            ds.get('StudyTime', ''),
            ds.get('AccessionNumber', ''),
            ds.get('StudyDescription', ''),
            ds.get('Modality', '')
        ))
        
        # Insert series
        self.conn.execute('''
            INSERT OR REPLACE INTO series VALUES (?, ?, ?, ?, ?)
        ''', (
            ds.SeriesInstanceUID,
            ds.StudyInstanceUID,
            ds.get('SeriesNumber', 0),
            ds.get('Modality', ''),
            ds.get('SeriesDescription', '')
        ))
        
        # Insert instance
        self.conn.execute('''
            INSERT OR REPLACE INTO instances VALUES (?, ?, ?, ?)
        ''', (
            ds.SOPInstanceUID,
            ds.SeriesInstanceUID,
            ds.get('InstanceNumber', 0),
            str(filepath)
        ))
        
        self.conn.commit()
    
    def index_directory(self, directory):
        for dcm_file in Path(directory).rglob('*.dcm'):
            try:
                self.index_dicom_file(dcm_file)
                print(f"Indexed: {dcm_file}")
            except Exception as e:
                print(f"Error indexing {dcm_file}: {e}")
```

## HL7 Integration

### Parse HL7 ADT Messages
```python
from hl7apy.parser import parse_message

def handle_adt_message(hl7_message):
    """Process HL7 ADT (Admission/Discharge/Transfer) message"""
    msg = parse_message(hl7_message)
    
    # Extract patient demographics
    pid = msg.PID
    patient_id = str(pid.pid_3)
    patient_name = str(pid.pid_5)
    dob = str(pid.pid_7)
    sex = str(pid.pid_8)
    
    # Update PACS database with new patient info
    update_patient_demographics(patient_id, patient_name, dob, sex)
    
    return {
        'patient_id': patient_id,
        'name': patient_name,
        'dob': dob,
        'sex': sex
    }
```

## Best Practices

### Connection Pooling
```python
from queue import Queue
from threading import Lock

class DICOMConnectionPool:
    def __init__(self, ae_title, remote_host, remote_port, remote_ae, pool_size=5):
        self.ae = AE(ae_title=ae_title)
        self.ae.requested_contexts = StoragePresentationContexts
        
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.remote_ae = remote_ae
        
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        
        # Pre-create associations
        for _ in range(pool_size):
            assoc = self.create_association()
            if assoc:
                self.pool.put(assoc)
    
    def create_association(self):
        return self.ae.associate(
            self.remote_host,
            self.remote_port,
            ae_title=self.remote_ae
        )
    
    def get_association(self):
        return self.pool.get()
    
    def return_association(self, assoc):
        if assoc.is_established:
            self.pool.put(assoc)
        else:
            # Reconnect if association dropped
            new_assoc = self.create_association()
            if new_assoc:
                self.pool.put(new_assoc)
```

### Error Handling and Retry
```python
import time
from functools import wraps

def retry_on_failure(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator

@retry_on_failure(max_attempts=3)
def send_to_pacs_with_retry(dicom_file):
    # Send implementation
    pass
```

### Async/Await for Performance
```python
import asyncio
from pynetdicom import AE

async def send_study_async(dicom_files, pacs_config):
    ae = AE()
    ae.requested_contexts = StoragePresentationContexts
    
    tasks = []
    for dcm_file in dicom_files:
        task = asyncio.create_task(send_single_file(ae, dcm_file, pacs_config))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## Testing Integration

### Mock PACS for Testing
```python
import pytest
from pynetdicom import AE, evt, StoragePresentationContexts
import threading

class MockPACS:
    def __init__(self):
        self.received_datasets = []
        self.ae = AE(ae_title='MOCK_PACS')
        self.ae.supported_contexts = StoragePresentationContexts
        
        def handle_store(event):
            self.received_datasets.append(event.dataset)
            return 0x0000
        
        self.handlers = [(evt.EVT_C_STORE, handle_store)]
        self.server_thread = None
    
    def start(self, port=11112):
        self.server_thread = threading.Thread(
            target=lambda: self.ae.start_server(
                ('', port),
                evt_handlers=self.handlers,
                block=True
            )
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.5)  # Wait for server to start
    
    def stop(self):
        self.ae.shutdown()

@pytest.fixture
def mock_pacs():
    pacs = MockPACS()
    pacs.start()
    yield pacs
    pacs.stop()

def test_send_to_pacs(mock_pacs):
    # Test implementation
    pass
```

## Resources
- pynetdicom documentation
- DICOMweb specification
- DCMTK networking tools
- IHE Integration Profiles

# DICOM Networking Guide

## Network Architecture

### DICOM Network Model
- Application Layer: DIMSE (DICOM Message Service Element)
- Presentation Layer: DICOM Upper Layer Protocol  
- Transport Layer: TCP/IP

### Association Establishment
1. A-ASSOCIATE-RQ (Request)
2. A-ASSOCIATE-AC (Accept) or A-ASSOCIATE-RJ (Reject)
3. Data Transfer (P-DATA-TF PDUs)
4. A-RELEASE-RQ/RP or A-ABORT

## Service Classes

### Storage Service (C-STORE)
**Use Case**: Send images from modality to PACS

**SCU Implementation**:
```python
from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage
import pydicom

ae = AE(ae_title='CT_MODALITY')
ae.add_requested_context(CTImageStorage)

ds = pydicom.dcmread('ct_image.dcm')
assoc = ae.associate('192.168.1.100', 104, ae_title='PACS')

if assoc.is_established:
    status = assoc.send_c_store(ds)
    if status.Status == 0x0000:
        print("Storage successful")
    assoc.release()
```

### Query/Retrieve Service

**C-FIND (Query)**:
```python
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
from pydicom.dataset import Dataset

ds = Dataset()
ds.QueryRetrieveLevel = 'STUDY'
ds.PatientID = '12345'
ds.StudyDate = '20240301-'
ds.StudyInstanceUID = ''
ds.AccessionNumber = ''

assoc = ae.associate('192.168.1.100', 104)
responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)

for (status, identifier) in responses:
    if status and status.Status in (0xFF00, 0xFF01):
        print(f"Study: {identifier.StudyInstanceUID}")
```

**C-MOVE (Retrieve)**:
```python
ds = Dataset()
ds.QueryRetrieveLevel = 'STUDY'
ds.StudyInstanceUID = '1.2.840.113619...'

responses = assoc.send_c_move(ds, 'DEST_AE', StudyRootQueryRetrieveInformationModelMove)

for (status, identifier) in responses:
    print(f"Remaining: {status.NumberOfRemainingSuboperations}")
    print(f"Completed: {status.NumberOfCompletedSuboperations}")
```

## Advanced Networking

### Multi-threaded Server
```python
from pynetdicom import AE, evt
import threading

class ThreadedDICOMServer:
    def __init__(self, ae_title, port):
        self.ae = AE(ae_title=ae_title)
        self.ae.supported_contexts = StoragePresentationContexts
        self.port = port
        
    def handle_store(self, event):
        ds = event.dataset
        ds.file_meta = event.file_meta
        filename = f"{ds.SOPInstanceUID}.dcm"
        ds.save_as(filename)
        return 0x0000
    
    def start(self):
        handlers = [(evt.EVT_C_STORE, self.handle_store)]
        
        server_thread = threading.Thread(
            target=self.ae.start_server,
            args=(('', self.port),),
            kwargs={'evt_handlers': handlers, 'block': True}
        )
        server_thread.daemon = True
        server_thread.start()

server = ThreadedDICOMServer('MY_SCP', 11112)
server.start()
```

### Load Balancing
```python
import random

class LoadBalancedPACS:
    def __init__(self, pacs_nodes):
        self.pacs_nodes = pacs_nodes
        self.weights = {node: 1.0 for node in pacs_nodes}
    
    def select_pacs(self):
        # Weighted random selection
        total = sum(self.weights.values())
        r = random.uniform(0, total)
        
        cumulative = 0
        for node, weight in self.weights.items():
            cumulative += weight
            if r <= cumulative:
                return node
    
    def store_with_load_balancing(self, dicom_dataset):
        pacs = self.select_pacs()
        try:
            send_to_pacs(dicom_dataset, pacs)
            # Success increases weight
            self.weights[pacs] *= 1.1
        except Exception:
            # Failure decreases weight
            self.weights[pacs] *= 0.5
            raise
```

## Troubleshooting

### Network Debugging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable pynetdicom debug logging
from pynetdicom import debug_logger
debug_logger()

# DCMTK command-line debugging
# storescu -v +P 11112 -aec PACS_SCP localhost image.dcm
```

### Common Issues

**Association Rejected**:
- Check AE titles match
- Verify IP/port accessibility
- Confirm presentation contexts supported

**Timeout**:
- Network connectivity
- Firewall blocking port
- Server not running
- PDU size mismatch

**Transfer Syntax Not Supported**:
```python
# Add explicit transfer syntaxes
from pynetdicom.sop_class import CTImageStorage
from pydicom.uid import ExplicitVRLittleEndian

ae.add_requested_context(CTImageStorage, ExplicitVRLittleEndian)
```

## Performance Tuning

### PDU Size Optimization
```python
# Larger PDU = fewer network round-trips
ae.maximum_pdu_size = 0  # Unlimited (use with caution)
ae.maximum_pdu_size = 65536  # 64 KB (common)
ae.maximum_pdu_size = 131072  # 128 KB
```

### Concurrent Transfers
```python
from concurrent.futures import ThreadPoolExecutor

def send_study(study_files, pacs_config):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(send_single_file, f, pacs_config)
            for f in study_files
        ]
        results = [f.result() for f in futures]
    return results
```

## Security

### TLS Encryption
```python
import ssl
from pynetdicom import AE

# Configure TLS
tls_args = {
    'ca_file': '/path/to/ca.pem',
    'cert_file': '/path/to/cert.pem',
    'key_file': '/path/to/key.pem',
    'verify_mode': ssl.CERT_REQUIRED
}

assoc = ae.associate('192.168.1.100', 11112, tls_args=tls_args)
```

### Access Control
```python
def verify_calling_ae(event):
    """Validate calling AE title against whitelist"""
    allowed_aes = ['MODALITY1', 'MODALITY2', 'WORKSTATION1']
    
    calling_ae = event.assoc.requestor.ae_title
    if calling_ae not in allowed_aes:
        # Reject association
        return 0x0122  # SOP class not supported (generic rejection)
    
    return 0x0000  # Accept
```

## Best Practices

1. **Timeout Configuration**: Set appropriate timeouts for network operations
2. **Retry Logic**: Implement exponential backoff for failed transfers
3. **Logging**: Comprehensive logging for troubleshooting
4. **Monitoring**: Track transfer success rates and performance
5. **Graceful Shutdown**: Properly release associations
6. **Connection Pooling**: Reuse associations for multiple transfers
7. **Error Handling**: Handle all DIMSE status codes appropriately

## Resources
- DICOM Part 7: Message Exchange
- DICOM Part 8: Network Communication Support
- pynetdicom documentation
- DCMTK networking tools

# DICOM Implementation Guide

## Getting Started with DICOM

### Understanding DICOM Basics

Before implementing DICOM, understand these core concepts:

1. **DICOM is more than images**: It includes metadata, network protocols, and services
2. **Standards-based**: Follow the specification exactly
3. **Vendor variations**: Real-world DICOM may deviate from standard
4. **Testing is critical**: Test with multiple vendors' equipment

### Choosing a DICOM Library

**Python - pydicom:**
```bash
pip install pydicom
pip install pydicom[numpy]  # For pixel data manipulation
pip install pynetdicom  # For networking
```

**Pros:**
- Easy to learn
- Excellent documentation
- Active community
- Great for prototyping

**Cons:**
- Slower than C++ libraries
- Not ideal for high-performance servers

**C++ - DCMTK:**
```bash
# Ubuntu/Debian
sudo apt-get install dcmtk libdcmtk-dev

# macOS
brew install dcmtk
```

**Pros:**
- Very fast
- Complete DICOM implementation
- Command-line tools included
- Production-grade

**Cons:**
- Steeper learning curve
- C++ complexity
- Verbose API

**Java - dcm4che:**
```xml
<dependency>
    <groupId>org.dcm4che</groupId>
    <artifactId>dcm4che-core</artifactId>
    <version>5.29.0</version>
</dependency>
```

**Pros:**
- Comprehensive
- Well-maintained
- Used in dcm4chee PACS
- Good documentation

**Cons:**
- Java ecosystem dependency
- Heavyweight for simple tasks

**.NET - fo-dicom:**
```
Install-Package fo-dicom
```

**Pros:**
- Modern .NET
- Async/await support
- Good performance
- Active development

**Cons:**
- Windows-focused (though cross-platform)
- Smaller community than pydicom

## Reading and Writing DICOM Files

### Reading DICOM with pydicom

**Basic Reading:**
```python
import pydicom

# Read DICOM file
ds = pydicom.dcmread('CT_image.dcm')

# Access patient information
print(f"Patient Name: {ds.PatientName}")
print(f"Patient ID: {ds.PatientID}")
print(f"Study Date: {ds.StudyDate}")

# Access study/series information
print(f"Study Description: {ds.StudyDescription}")
print(f"Series Description: {ds.SeriesDescription}")
print(f"Modality: {ds.Modality}")

# Access image information
print(f"Rows: {ds.Rows}, Columns: {ds.Columns}")
print(f"Pixel Spacing: {ds.PixelSpacing}")
print(f"Slice Thickness: {ds.SliceThickness}")

# Get pixel data
pixel_array = ds.pixel_array  # NumPy array
print(f"Pixel array shape: {pixel_array.shape}")
print(f"Pixel array dtype: {pixel_array.dtype}")
```

**Handling Missing Tags:**
```python
# Check if tag exists
if 'StudyDescription' in ds:
    print(ds.StudyDescription)

# Use getattr with default
study_desc = getattr(ds, 'StudyDescription', 'No description')

# Try/except approach
try:
    print(ds.SliceLocation)
except AttributeError:
    print("Slice location not available")
```

**Iterating Through All Tags:**
```python
# Print all data elements
for elem in ds:
    print(f"{elem.tag} {elem.name}: {elem.value}")

# Filter by group
for elem in ds:
    if elem.tag.group == 0x0008:  # Study/Series information
        print(f"{elem.name}: {elem.value}")
```

### Writing DICOM Files

**Modify Existing DICOM:**
```python
import pydicom
from pydicom.uid import generate_uid

# Read existing file
ds = pydicom.dcmread('original.dcm')

# Modify tags
ds.PatientName = 'Anonymous^Patient'
ds.PatientID = '000000'

# Generate new UIDs to make it unique
ds.StudyInstanceUID = generate_uid()
ds.SeriesInstanceUID = generate_uid()
ds.SOPInstanceUID = generate_uid()

# Save to new file
ds.save_as('modified.dcm')
```

**Create DICOM from Scratch:**
```python
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import numpy as np
from datetime import datetime

# Create file meta information
file_meta = Dataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
file_meta.MediaStorageSOPInstanceUID = generate_uid()
file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'  # Explicit VR Little Endian
file_meta.ImplementationClassUID = generate_uid()

# Create the FileDataset instance
ds = FileDataset('ct_image.dcm', {}, file_meta=file_meta, preamble=b"\0" * 128)

# Set creation date/time
dt = datetime.now()
ds.ContentDate = dt.strftime('%Y%m%d')
ds.ContentTime = dt.strftime('%H%M%S.%f')

# Patient information
ds.PatientName = 'Test^Patient'
ds.PatientID = '123456'
ds.PatientBirthDate = '19800101'
ds.PatientSex = 'M'

# Study information
ds.StudyInstanceUID = generate_uid()
ds.StudyDate = dt.strftime('%Y%m%d')
ds.StudyTime = dt.strftime('%H%M%S')
ds.StudyID = '1'
ds.AccessionNumber = 'ACC001'
ds.ReferringPhysicianName = 'Smith^John^^Dr.'

# Series information
ds.SeriesInstanceUID = generate_uid()
ds.SeriesNumber = 1
ds.Modality = 'CT'
ds.SeriesDescription = 'Test CT Series'

# Image information
ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
ds.InstanceNumber = 1

# Image pixel information
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = 'MONOCHROME2'
ds.Rows = 512
ds.Columns = 512
ds.BitsAllocated = 16
ds.BitsStored = 12
ds.HighBit = 11
ds.PixelRepresentation = 0  # Unsigned
ds.PixelSpacing = [0.5, 0.5]  # mm
ds.SliceThickness = 5.0  # mm

# Create pixel data (example: gradient)
pixel_array = np.arange(512 * 512, dtype=np.uint16).reshape(512, 512)
ds.PixelData = pixel_array.tobytes()

# CT-specific
ds.RescaleIntercept = -1024
ds.RescaleSlope = 1
ds.RescaleType = 'HU'
ds.WindowCenter = 40
ds.WindowWidth = 400

# Save
ds.save_as('created_ct.dcm')
```

### Handling Pixel Data

**Extract and Process:**
```python
import pydicom
import numpy as np
import matplotlib.pyplot as plt

ds = pydicom.dcmread('ct_image.dcm')

# Get raw pixel data
pixel_array = ds.pixel_array

# Apply rescale (for CT: convert to Hounsfield Units)
if 'RescaleSlope' in ds and 'RescaleIntercept' in ds:
    hu_array = pixel_array * ds.RescaleSlope + ds.RescaleIntercept
else:
    hu_array = pixel_array

# Apply window/level
window_center = ds.WindowCenter if 'WindowCenter' in ds else 40
window_width = ds.WindowWidth if 'WindowWidth' in ds else 400

# Handle multiple window values (take first)
if isinstance(window_center, pydicom.multival.MultiValue):
    window_center = window_center[0]
if isinstance(window_width, pydicom.multival.MultiValue):
    window_width = window_width[0]

# Apply windowing
img_min = window_center - window_width // 2
img_max = window_center + window_width // 2
windowed = np.clip(hu_array, img_min, img_max)

# Normalize to 0-255 for display
normalized = ((windowed - img_min) / (img_max - img_min) * 255).astype(np.uint8)

# Display
plt.imshow(normalized, cmap='gray')
plt.title(f'{ds.PatientName} - {ds.SeriesDescription}')
plt.axis('off')
plt.show()
```

**Handle Compressed Pixel Data:**
```python
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut

# Read file with compressed data
ds = pydicom.dcmread('compressed.dcm')

# pydicom will decompress automatically if decompression handler available
# Install pillow for JPEG: pip install pillow
# Install pillow-jpeg-ls for JPEG-LS: pip install pillow-jpeg-ls
# Install gdcm for JPEG 2000: pip install gdcm

pixel_array = ds.pixel_array

# Apply VOI LUT (Value of Interest) - handles window/level
processed = apply_voi_lut(pixel_array, ds)
```

## DICOM Networking

### Setting Up DICOM Network Nodes

**Application Entity (AE) Configuration:**
```python
from pynetdicom import AE, StoragePresentationContexts

# Create Application Entity
ae = AE(ae_title='MY_SCU')  # Max 16 characters

# For storage SCU (sender), add presentation contexts
ae.requested_contexts = StoragePresentationContexts

# For query/retrieve, add specific contexts
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelMove,
    CTImageStorage
)

ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
ae.add_requested_context(PatientRootQueryRetrieveInformationModelMove)
ae.add_requested_context(CTImageStorage)
```

### Implementing C-STORE (Storage)

**C-STORE SCU (Sender):**
```python
from pynetdicom import AE, StoragePresentationContexts
import pydicom

# Create AE
ae = AE(ae_title='STORE_SCU')
ae.requested_contexts = StoragePresentationContexts

# Read DICOM file to send
ds = pydicom.dcmread('ct_image.dcm')

# Associate with remote AE
assoc = ae.associate('127.0.0.1', 11112, ae_title='STORE_SCP')

if assoc.is_established:
    # Send the DICOM file
    status = assoc.send_c_store(ds)

    # Check the status
    if status:
        print(f'C-STORE request status: 0x{status.Status:04x}')
        if status.Status == 0x0000:
            print('Storage successful')
        else:
            print('Storage failed')
    else:
        print('Connection timed out or aborted')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
```

**C-STORE SCP (Receiver/Server):**
```python
from pynetdicom import AE, StoragePresentationContexts, evt
import os

# Handler for incoming C-STORE requests
def handle_store(event):
    """Handle a C-STORE request."""
    # Get the dataset from the event
    ds = event.dataset

    # Add file meta information
    ds.file_meta = event.file_meta

    # Create filename from SOP Instance UID
    filename = f"{ds.SOPInstanceUID}.dcm"
    filepath = os.path.join('/path/to/storage', filename)

    # Save the dataset
    ds.save_as(filepath, write_like_original=False)

    # Return success status
    return 0x0000

# Create AE
ae = AE(ae_title='STORE_SCP')

# Add supported presentation contexts
ae.supported_contexts = StoragePresentationContexts

# Set up event handlers
handlers = [(evt.EVT_C_STORE, handle_store)]

# Start SCP server
ae.start_server(('', 11112), evt_handlers=handlers, block=True)
```

### Implementing C-FIND (Query)

**C-FIND SCU (Query Client):**
```python
from pynetdicom import AE
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
from pydicom.dataset import Dataset

# Create AE
ae = AE(ae_title='FIND_SCU')
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

# Create query dataset
ds = Dataset()
ds.QueryRetrieveLevel = 'STUDY'

# Search criteria (use wildcards)
ds.PatientName = 'DOE^JOHN*'  # Wildcard search
ds.PatientID = ''
ds.StudyDate = '20240301-20240331'  # Date range
ds.ModalitiesInStudy = 'CT'

# Return keys (empty values means we want these returned)
ds.StudyInstanceUID = ''
ds.StudyDescription = ''
ds.AccessionNumber = ''
ds.NumberOfStudyRelatedInstances = ''

# Associate and query
assoc = ae.associate('127.0.0.1', 11112, ae_title='FIND_SCP')

if assoc.is_established:
    # Send C-FIND request
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)

    for (status, identifier) in responses:
        if status:
            print(f'C-FIND status: 0x{status.Status:04x}')

            # If pending, print the match
            if status.Status in (0xFF00, 0xFF01):  # Pending
                print(f'Patient: {identifier.PatientName}')
                print(f'Study: {identifier.StudyDescription}')
                print(f'Date: {identifier.StudyDate}')
                print(f'Accession: {identifier.AccessionNumber}')
                print('---')
        else:
            print('Connection timed out or aborted')

    assoc.release()
```

**C-FIND SCP (Query Server):**
```python
from pynetdicom import AE, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
import sqlite3

def handle_find(event):
    """Handle a C-FIND request."""
    ds = event.identifier

    # Build SQL query based on DICOM query
    query = "SELECT * FROM studies WHERE 1=1"
    params = []

    if 'PatientName' in ds and ds.PatientName:
        # Convert DICOM wildcard to SQL LIKE
        pattern = ds.PatientName.replace('*', '%').replace('?', '_')
        query += " AND patient_name LIKE ?"
        params.append(pattern)

    if 'StudyDate' in ds and ds.StudyDate:
        # Handle date range
        if '-' in ds.StudyDate:
            start, end = ds.StudyDate.split('-')
            query += " AND study_date BETWEEN ? AND ?"
            params.extend([start, end])
        else:
            query += " AND study_date = ?"
            params.append(ds.StudyDate)

    # Execute query
    conn = sqlite3.connect('/path/to/database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)

    # Yield results
    for row in cursor.fetchall():
        # Create identifier dataset
        identifier = Dataset()
        identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel
        identifier.PatientName = row['patient_name']
        identifier.PatientID = row['patient_id']
        identifier.StudyInstanceUID = row['study_uid']
        identifier.StudyDate = row['study_date']
        identifier.StudyDescription = row['study_description']
        identifier.AccessionNumber = row['accession_number']

        # Yield with pending status
        yield (0xFF00, identifier)

    conn.close()

# Setup SCP
ae = AE(ae_title='FIND_SCP')
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)

handlers = [(evt.EVT_C_FIND, handle_find)]

ae.start_server(('', 11112), evt_handlers=handlers, block=True)
```

### Implementing C-MOVE (Retrieve)

**C-MOVE SCU:**
```python
from pynetdicom import AE
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelMove,
    CTImageStorage
)
from pydicom.dataset import Dataset

# Create AE with both C-MOVE and C-STORE contexts
ae = AE(ae_title='MOVE_SCU')
ae.add_requested_context(PatientRootQueryRetrieveInformationModelMove)
ae.add_requested_context(CTImageStorage)  # For receiving images

# Create identifier (what to retrieve)
ds = Dataset()
ds.QueryRetrieveLevel = 'SERIES'
ds.StudyInstanceUID = '1.2.840.113619.2.1.1.1'
ds.SeriesInstanceUID = '1.2.840.113619.2.1.2.1'

# Associate
assoc = ae.associate('127.0.0.1', 11112, ae_title='MOVE_SCP')

if assoc.is_established:
    # Send C-MOVE request (destination is our AE title)
    responses = assoc.send_c_move(
        ds,
        'MOVE_SCU',  # Destination AE title (can be different)
        PatientRootQueryRetrieveInformationModelMove
    )

    for (status, identifier) in responses:
        if status:
            print(f'C-MOVE status: 0x{status.Status:04x}')
            print(f'Remaining: {status.NumberOfRemainingSuboperations}')
            print(f'Completed: {status.NumberOfCompletedSuboperations}')
            print(f'Failed: {status.NumberOfFailedSuboperations}')
            print(f'Warning: {status.NumberOfWarningSuboperations}')
        else:
            print('Connection timed out or aborted')

    assoc.release()
```

## Best Practices

### UID Management

**Generate Valid UIDs:**
```python
from pydicom.uid import generate_uid

# Generate new UID using your organization root
org_root = '1.2.840.99999'  # Register with appropriate authority
study_uid = generate_uid(prefix=org_root)

# Or use pydicom's default
study_uid = generate_uid()  # Uses pydicom's registered prefix
```

**Rules:**
- Each study needs unique Study Instance UID
- Each series needs unique Series Instance UID
- Each image needs unique SOP Instance UID
- UIDs must not exceed 64 characters
- Only use digits and dots, no leading zeros

### Error Handling

**Robust File Reading:**
```python
import pydicom

def safe_read_dicom(filepath):
    """Safely read DICOM file with error handling."""
    try:
        ds = pydicom.dcmread(filepath, force=True)

        # Verify it's actually DICOM
        if not hasattr(ds, 'SOPClassUID'):
            print(f"Warning: {filepath} missing SOPClassUID")
            return None

        return ds

    except pydicom.errors.InvalidDicomError:
        print(f"Error: {filepath} is not a valid DICOM file")
        return None

    except Exception as e:
        print(f"Error reading {filepath}: {str(e)}")
        return None
```

### Performance Optimization

**Lazy Loading:**
```python
# Don't load pixel data if not needed
ds = pydicom.dcmread('large_image.dcm', stop_before_pixels=True)

# Only load pixel data when needed
if need_pixels:
    ds = pydicom.dcmread('large_image.dcm')
    pixels = ds.pixel_array
```

**Bulk Processing:**
```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def process_dicom(filepath):
    """Process single DICOM file."""
    ds = pydicom.dcmread(filepath, stop_before_pixels=True)
    # Extract metadata
    return {
        'path': filepath,
        'patient_id': ds.PatientID,
        'study_uid': ds.StudyInstanceUID,
        'modality': ds.Modality
    }

# Process directory in parallel
dicom_dir = Path('/path/to/dicoms')
dicom_files = list(dicom_dir.glob('**/*.dcm'))

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(process_dicom, dicom_files))
```

## Testing and Validation

### Conformance Testing

**Test with Real Equipment:**
- Send test images to actual PACS
- Retrieve from actual modalities
- Test with different vendors

**Public Test Servers:**
- **DICOM Test Server (dicomserver.co.uk)**:
  - Address: www.dicomserver.co.uk
  - Port: 104
  - AE Title: ANY-SCP

**Validation Tools:**
- **DCMTK utilities**: dcmdump, dcmconv, dcmqrscp
- **DVTk**: DICOM Validation Toolkit
- **DICOM Library**: Online DICOM validator

### Common Issues and Solutions

**Issue: "No suitable presentation context"**
```python
# Solution: Add the required presentation context
ae.add_requested_context(CTImageStorage)
```

**Issue: "Association rejected"**
```python
# Solution: Check AE titles, IP, port
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Issue: "Unable to decode pixel data"**
```python
# Solution: Install appropriate decoder
# pip install pillow  # For JPEG
# pip install gdcm  # For JPEG 2000
```

## Resources

- **pydicom Documentation**: https://pydicom.github.io
- **DICOM Standard**: https://dicom.nema.org
- **DCMTK Tools**: https://dicom.offis.de/dcmtk
- **pynetdicom Examples**: https://pydicom.github.io/pynetdicom
- **DICOM Test Data**: https://www.dicomlibrary.com

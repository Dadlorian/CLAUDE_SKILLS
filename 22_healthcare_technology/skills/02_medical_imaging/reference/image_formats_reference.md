# Medical Image Formats Reference

## DICOM Format

### File Structure
```
[128-byte Preamble] [DICM] [File Meta Information] [Data Set]
```

### Characteristics
- **Standard**: ISO 12052 compliant
- **Metadata**: Rich patient/study/series information embedded
- **Pixel Data**: Multiple transfer syntaxes (compressed/uncompressed)
- **Multi-frame**: Support for cine loops, 3D volumes
- **Encapsulation**: Can contain PDFs, documents, waveforms

### Transfer Syntaxes
**Uncompressed:**
- Implicit VR Little Endian: 1.2.840.10008.1.2
- Explicit VR Little Endian: 1.2.840.10008.1.2.1
- Explicit VR Big Endian: 1.2.840.10008.1.2.2 (retired)

**Compressed (Lossless):**
- JPEG Lossless: 1.2.840.10008.1.2.4.70
- JPEG-LS Lossless: 1.2.840.10008.1.2.4.80
- JPEG 2000 Lossless: 1.2.840.10008.1.2.4.90
- RLE Lossless: 1.2.840.10008.1.2.5

**Compressed (Lossy):**
- JPEG Baseline: 1.2.840.10008.1.2.4.50
- JPEG 2000: 1.2.840.10008.1.2.4.91
- JPEG-LS Near-Lossless: 1.2.840.10008.1.2.4.81

### Use Cases
- **Primary format** for medical imaging
- **Archival**: Long-term storage
- **Exchange**: Between medical systems
- **Legal**: Maintains full provenance

### Advantages
- Complete metadata
- Vendor neutral
- Standardized globally
- Regulatory accepted

### Disadvantages
- Complex specification
- Large file sizes (if uncompressed)
- Requires specialized viewers
- Not web-friendly

## NIFTI (Neuroimaging Informatics Technology Initiative)

### File Structure
```
[348-byte Header] [Optional Extension] [Image Data]
```

### Variants
- **NIFTI-1**: .nii (single file), .hdr/.img (header/image pair)
- **NIFTI-2**: Extended for large datasets

### Header Information
- Dimensions (up to 7D)
- Voxel sizes
- Data type
- Orientation (qform, sform matrices)
- Units (space: mm/microns, time: sec/ms)
- Calibration min/max

### Characteristics
- **Orientation**: Robust 3D orientation encoding
- **Dimensions**: Supports up to 7D data (x, y, z, time, etc.)
- **Compression**: .nii.gz (gzip compressed)
- **Open Standard**: Public specification

### Use Cases
- **Neuroimaging research**: fMRI, DTI, structural MRI
- **Software**: FSL, SPM, AFNI, FreeSurfer
- **Analysis pipelines**: Batch processing
- **Data sharing**: Research collaborations

### Conversion
- **dcm2niix**: DICOM to NIFTI conversion
- Handles complex acquisitions (multi-echo, diffusion)
- Preserves critical metadata

### Advantages
- Simple format
- Research tool support
- Efficient for 3D/4D data
- Well-documented orientation

### Disadvantages
- Limited metadata
- Not for clinical archival
- Single modality per file
- No patient demographics

## NRRD (Nearly Raw Raster Data)

### File Structure
```
NRRD0004
# Complete NRRD file format
type: unsigned char
dimension: 3
sizes: 256 256 128
spacings: 1.0 1.0 2.0
endian: little
encoding: raw

[Binary Data]
```

### Characteristics
- **Header**: Human-readable ASCII
- **Flexible**: Arbitrary dimensions
- **Metadata**: Key-value pairs
- **Detached Header**: .nhdr (header) + .raw (data)

### Supported Encodings
- Raw (binary)
- Gzip compressed
- Bzip2 compressed
- ASCII (text, for small data)

### Use Cases
- **3D Slicer**: Native format
- **Medical image processing**: ITK, VTK
- **Visualization**: Volume rendering
- **Research**: Image analysis

### Advantages
- Simple and flexible
- Well-supported by tools
- Compression options
- Clear documentation

### Disadvantages
- Not standardized widely
- Limited clinical use
- Minimal patient metadata

## MetaImage (MHD/MHA)

### File Structure
**MHD (MetaImage Header) + Raw:**
```
ObjectType = Image
NDims = 3
DimSize = 256 256 128
ElementSpacing = 1.0 1.0 2.0
ElementType = MET_UCHAR
ElementDataFile = image.raw
```

**MHA (MetaImage Archive):**
Single file with embedded binary data

### Characteristics
- **ITK Native**: InsightToolkit format
- **Simple**: Easy to create/parse
- **Flexible**: Various data types
- **Portable**: Text header, binary data

### Use Cases
- **ITK/SimpleITK**: Image processing
- **Segmentation**: Label maps
- **Registration**: Transformed images
- **Research pipelines**: Intermediate format

### Advantages
- Simple specification
- ITK integration
- Human-readable header
- Flexible metadata

### Disadvantages
- Less common than NIFTI
- Minimal standardization
- Limited tool support

## Analyze 7.5 (Legacy)

### File Structure
- **.hdr**: 348-byte header
- **.img**: Raw binary image data

### Characteristics
- **Deprecated**: Replaced by NIFTI
- **Ambiguous Orientation**: Left/right ambiguity
- **Limited Metadata**: Minimal header
- **Legacy Support**: Old software

### Use Cases
- **Legacy data**: Old research datasets
- **SPM99**: Early versions
- **Conversion**: To NIFTI recommended

### Issues
- Left-right flip ambiguity
- No standard orientation
- Limited by NIFTI

## MINC (Medical Image NetCDF)

### File Structure
Based on NetCDF (Network Common Data Form)

### Variants
- **MINC 1.0**: NetCDF-3 based
- **MINC 2.0**: HDF5 based (modern)

### Characteristics
- **Multi-dimensional**: Arbitrary dimensions
- **Metadata**: Rich, hierarchical
- **Self-describing**: Complete provenance
- **NetCDF**: Standard scientific data format

### Use Cases
- **Montreal Neurological Institute**: MNI tools
- **Brain imaging**: Structural, functional
- **Research**: Canadian brain imaging
- **CIVET pipeline**: Cortical analysis

### Advantages
- Rich metadata
- HDF5 benefits (MINC 2.0)
- Scientific standard (NetCDF)
- Complete provenance

### Disadvantages
- Limited to specific tools
- Less common globally
- Complex specification

## Medical Image Compression

### Lossless Compression

**JPEG Lossless (Process 14)**
- **Ratio**: 2:1 to 3:1 typical
- **Use**: General medical imaging
- **Standard**: Well-supported in DICOM
- **Speed**: Fast encoding/decoding

**JPEG-LS**
- **Ratio**: 2:1 to 3:1 typical
- **Use**: Low-complexity lossless
- **Near-Lossless**: Controlled error
- **Speed**: Very fast

**JPEG 2000 Lossless**
- **Ratio**: 2:1 to 4:1 typical
- **Use**: High-quality archival
- **Wavelet-based**: Better than JPEG
- **Speed**: Slower encoding
- **Progressive**: Multi-resolution

**RLE (Run-Length Encoding)**
- **Ratio**: Varies, 1.5:1 to 2:1
- **Use**: Simple compression
- **Fast**: Very fast decoding
- **Best for**: Images with large uniform areas

### Lossy Compression

**JPEG Baseline**
- **Ratio**: 10:1 to 20:1
- **Use**: Non-diagnostic, teaching files
- **Quality**: Adjustable
- **Artifacts**: Blocking at high compression

**JPEG 2000 Lossy**
- **Ratio**: 10:1 to 100:1
- **Use**: Teleradiology, web viewers
- **Quality**: Better than JPEG at same ratio
- **Artifacts**: Less noticeable
- **Diagnostic**: Up to 10:1 sometimes acceptable

### Compression Guidelines

**Primary Interpretation:**
- **Lossless only** or uncompressed
- Diagnostic quality required
- Legal/regulatory compliance

**Secondary/Reference:**
- **Lossy acceptable** (up to 10:1)
- Faster transmission
- Reduced storage

**Teaching/Research:**
- **Lossy acceptable** (higher ratios)
- De-identified
- Not for clinical decisions

**Teleradiology:**
- **Lossy for speed** (10:1 to 15:1)
- Lossless on-demand
- Bandwidth optimization

## Format Conversion

### DICOM to NIFTI
```bash
# Using dcm2niix (recommended)
dcm2niix -f %n_%p_%t_%s -o /output /input_dicom

# Options:
# -f: Filename format
# -z: Compress (y/n)
# -b: Generate BIDS sidecar JSON
```

**Metadata Handling:**
- Patient info stripped
- Orientation preserved (sform/qform)
- Acquisition parameters in JSON sidecar

### DICOM to PNG/JPEG
```python
# Using pydicom
import pydicom
from PIL import Image
import numpy as np

ds = pydicom.dcmread('image.dcm')
pixel_array = ds.pixel_array

# Apply windowing
window_center = ds.WindowCenter
window_width = ds.WindowWidth
img_min = window_center - window_width // 2
img_max = window_center + window_width // 2

# Normalize to 8-bit
windowed = np.clip(pixel_array, img_min, img_max)
normalized = ((windowed - img_min) / (img_max - img_min) * 255).astype(np.uint8)

# Save as PNG
Image.fromarray(normalized).save('image.png')
```

**Caveats:**
- Loses DICOM metadata
- Window/level applied
- Not reversible
- Not for archival

### NIFTI to DICOM
```python
# Using SimpleITK
import SimpleITK as sitk

# Read NIFTI
nifti = sitk.ReadImage('brain.nii.gz')

# Convert to DICOM series
writer = sitk.ImageSeriesWriter()
writer.SetFileName(['output_{}.dcm'.format(i) for i in range(nifti.GetDepth())])

# Need to set DICOM tags manually
# (Patient ID, Study UID, Series UID, etc.)
```

**Challenges:**
- Metadata reconstruction
- UID generation
- Patient demographics
- Clinical context lost

### Multi-frame DICOM to Single Files
```python
import pydicom
import numpy as np

# Read multi-frame
ds = pydicom.dcmread('multiframe.dcm')
frames = ds.pixel_array  # Shape: (num_frames, rows, cols)

# Save each frame
for i in range(frames.shape[0]):
    frame_ds = ds.copy()
    frame_ds.PixelData = frames[i].tobytes()
    frame_ds.NumberOfFrames = 1
    frame_ds.InstanceNumber = i + 1
    frame_ds.SOPInstanceUID = generate_uid()  # New UID
    frame_ds.save_as(f'frame_{i:04d}.dcm')
```

## Web-Optimized Formats

### JPEG 2000 with Progressive Decoding
- **Use**: Web PACS viewers
- **Benefit**: Show low-res quickly, refine progressively
- **Implementation**: DICOMweb WADO-RS with JPEG 2000

### Tiled Pyramidal TIFF
- **Use**: Digital pathology (WSI)
- **Structure**: Multi-resolution pyramid
- **Access**: Tile-based random access
- **Size**: Gigapixel images

### WebP
- **Use**: Teaching files, patient portals
- **Compression**: Better than JPEG
- **Support**: Modern browsers
- **Limitation**: Not for diagnostic

## Format Recommendations

### Clinical PACS Archive
- **Primary**: DICOM uncompressed or lossless
- **Reason**: Quality, standard compliance, legal

### Research Dataset
- **Primary**: NIFTI (.nii.gz)
- **Secondary**: DICOM for raw data preservation
- **Reason**: Tool support, efficient

### AI Training Dataset
- **Primary**: NIFTI or NumPy arrays
- **Metadata**: Separate CSV/JSON
- **Reason**: Framework compatibility

### Web Viewer
- **Transmission**: JPEG 2000 or JPEG lossy
- **Cache**: DICOM lossless locally
- **Reason**: Speed vs. quality balance

### Teaching File
- **Format**: DICOM anonymized or JPEG
- **Annotation**: DICOM SC or PDF
- **Reason**: Versatility, viewer compatibility

### Patient CD/Portal
- **Format**: DICOM with embedded viewer
- **Alternative**: JPEG/PDF for accessibility
- **Reason**: Patient access without DICOM viewer

## Legal and Regulatory Considerations

### Lossless Requirement
- **Primary diagnostic**: Lossless only in many jurisdictions
- **Legal cases**: Original uncompressed data may be required
- **Retention**: Check local regulations

### Lossy Acceptable
- **Teleradiology**: Some regions allow lossy for initial read
- **Final interpretation**: Should use lossless or original
- **Documentation**: Must document if lossy used

### Format Validation
- **FDA Cleared Viewers**: Must support specific transfer syntaxes
- **Conformance**: Viewer conformance to display standards
- **Calibration**: Monitor calibration for diagnostic viewing

## File Size Comparison

**Example: CT Chest (512×512, 200 slices, 16-bit)**

| Format | Compression | Size | Ratio |
|--------|-------------|------|-------|
| DICOM Uncompressed | None | 100 MB | 1:1 |
| DICOM JPEG Lossless | Lossless | 33 MB | 3:1 |
| DICOM JPEG 2000 Lossless | Lossless | 25 MB | 4:1 |
| DICOM JPEG 2000 (10:1) | Lossy | 10 MB | 10:1 |
| NIFTI Uncompressed | None | 52 MB | - |
| NIFTI Gzipped | Lossless | 18 MB | 2.9:1 |

**Notes:**
- DICOM includes metadata (~50 KB per image)
- Actual ratios vary by image content
- CT compresses better than MRI typically

## Best Practices

### Archival
1. Use DICOM with lossless or uncompressed
2. Verify data integrity (checksums)
3. Test restore procedures regularly
4. Plan for format migration

### Research
1. Convert DICOM to NIFTI for analysis
2. Preserve original DICOM
3. Document conversion parameters
4. Use BIDS standard for organization

### Sharing
1. De-identify DICOM properly
2. Consider NIFTI for neuro research
3. Include README with dataset description
4. Provide conversion scripts if needed

### AI/ML
1. Preprocess to common format (NIFTI/NumPy)
2. Standardize orientation
3. Normalize intensity
4. Document preprocessing pipeline

## Tools and Libraries

### Python
- **pydicom**: Read/write DICOM
- **SimpleITK**: Multi-format support
- **nibabel**: NIFTI/MINC/Analyze
- **dcm2niix**: Python wrapper for conversion

### Command-Line
- **dcm2niix**: DICOM to NIFTI conversion
- **DCMTK**: DICOM toolkit
- **ImageMagick**: Format conversion (non-medical)
- **gdcm**: Grassroots DICOM

### GUI Applications
- **3D Slicer**: Multi-format viewer/converter
- **Horos**: DICOM viewer with export
- **MITK**: Medical imaging toolkit
- **ITK-SNAP**: Segmentation, NIFTI focus

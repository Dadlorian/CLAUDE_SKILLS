# Digital Asset Management (DAM) System Implementation

Complete guide to building enterprise DAM systems for managing media libraries, metadata, workflows, and rights.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Upload/Ingest  │─────>│  Processing      │─────>│  Storage        │
│  (Files/Meta)   │      │  (Transcode/QC)  │      │  (S3/Filesystem)│
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Search/Browse  │<─────│  Metadata DB     │<─────│  Indexing       │
│  (UI/API)       │      │  (Elasticsearch) │      │  (Full-text)    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │
        ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Workflow       │<─────│  Rights Mgmt     │<─────│  Licensing DB   │
│  Automation     │      │  (Permissions)   │      │  (Agreements)   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## Phase 1: Asset Ingest Pipeline

### 1.1 File Upload & Validation

```python
# asset_ingest.py
import os
import hashlib
import magic
from pathlib import Path
from typing import Dict, Optional

class AssetIngestPipeline:
    """Comprehensive asset ingest with validation and processing"""

    def __init__(self, config: Dict):
        self.config = config
        self.storage_path = Path(config['storage_path'])
        self.allowed_types = config.get('allowed_types', [
            'video/mp4', 'video/quicktime', 'video/x-msvideo',
            'image/jpeg', 'image/png', 'image/tiff',
            'audio/mpeg', 'audio/wav', 'audio/flac',
            'application/pdf'
        ])
        self.max_file_size = config.get('max_file_size', 10 * 1024 * 1024 * 1024)  # 10GB

    async def ingest_asset(self, file_path: str, metadata: Dict) -> Dict:
        """Complete asset ingest workflow"""

        result = {
            'success': False,
            'asset_id': None,
            'errors': [],
            'warnings': [],
            'steps_completed': []
        }

        try:
            # Step 1: Validate file
            validation = await self._validate_file(file_path)
            if not validation['valid']:
                result['errors'].extend(validation['errors'])
                return result
            result['steps_completed'].append('validation')

            # Step 2: Generate asset ID
            asset_id = self._generate_asset_id(file_path)
            result['asset_id'] = asset_id

            # Step 3: Compute checksums
            checksums = self._compute_checksums(file_path)
            result['steps_completed'].append('checksum')

            # Step 4: Extract technical metadata
            technical_metadata = await self._extract_metadata(file_path)
            result['steps_completed'].append('metadata_extraction')

            # Step 5: Virus scan
            virus_scan = await self._virus_scan(file_path)
            if not virus_scan['clean']:
                result['errors'].append('Virus detected')
                return result
            result['steps_completed'].append('virus_scan')

            # Step 6: Generate proxies
            proxies = await self._generate_proxies(file_path, asset_id)
            result['steps_completed'].append('proxy_generation')

            # Step 7: Store files
            storage_info = await self._store_asset(file_path, asset_id, proxies)
            result['steps_completed'].append('storage')

            # Step 8: Index for search
            await self._index_asset(asset_id, metadata, technical_metadata)
            result['steps_completed'].append('indexing')

            # Step 9: Store metadata
            await self._store_metadata(asset_id, {
                **metadata,
                'technical': technical_metadata,
                'checksums': checksums,
                'storage': storage_info
            })
            result['steps_completed'].append('metadata_storage')

            result['success'] = True

        except Exception as e:
            result['errors'].append(str(e))

        return result

    async def _validate_file(self, file_path: str) -> Dict:
        """Validate uploaded file"""

        errors = []

        # Check file exists
        if not os.path.exists(file_path):
            errors.append('File does not exist')
            return {'valid': False, 'errors': errors}

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            errors.append(f'File too large: {file_size} bytes (max: {self.max_file_size})')

        if file_size == 0:
            errors.append('File is empty')

        # Check MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)

        if mime_type not in self.allowed_types:
            errors.append(f'Unsupported file type: {mime_type}')

        # Check file extension matches MIME type
        extension = Path(file_path).suffix.lower()
        expected_extensions = self._mime_to_extensions(mime_type)
        if extension not in expected_extensions:
            errors.append(f'File extension {extension} does not match MIME type {mime_type}')

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'mime_type': mime_type,
            'file_size': file_size
        }

    def _compute_checksums(self, file_path: str) -> Dict:
        """Compute file checksums"""

        checksums = {}

        # MD5
        md5 = hashlib.md5()
        # SHA-256
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                md5.update(chunk)
                sha256.update(chunk)

        checksums['md5'] = md5.hexdigest()
        checksums['sha256'] = sha256.hexdigest()

        return checksums

    async def _extract_metadata(self, file_path: str) -> Dict:
        """Extract technical metadata from file"""

        import subprocess
        import json

        # Use ffprobe for media files
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            metadata = json.loads(result.stdout)

            # Extract key information
            format_info = metadata.get('format', {})
            streams = metadata.get('streams', [])

            technical = {
                'format': format_info.get('format_name'),
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bit_rate': int(format_info.get('bit_rate', 0)),
                'streams': []
            }

            for stream in streams:
                stream_info = {
                    'codec_type': stream.get('codec_type'),
                    'codec_name': stream.get('codec_name'),
                }

                if stream['codec_type'] == 'video':
                    stream_info.update({
                        'width': stream.get('width'),
                        'height': stream.get('height'),
                        'frame_rate': stream.get('r_frame_rate'),
                        'aspect_ratio': stream.get('display_aspect_ratio')
                    })
                elif stream['codec_type'] == 'audio':
                    stream_info.update({
                        'sample_rate': stream.get('sample_rate'),
                        'channels': stream.get('channels'),
                        'bit_rate': stream.get('bit_rate')
                    })

                technical['streams'].append(stream_info)

            return technical

        except Exception as e:
            return {'error': str(e)}

    async def _virus_scan(self, file_path: str) -> Dict:
        """Scan file for viruses"""

        # In production: integrate with ClamAV or similar
        # For now, mock implementation

        return {'clean': True, 'scanner': 'mock'}

    async def _generate_proxies(self, file_path: str, asset_id: str) -> Dict:
        """Generate proxy versions of asset"""

        proxies = {}
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)

        if mime_type.startswith('video/'):
            # Generate video proxies
            proxies['thumbnail'] = await self._generate_video_thumbnail(file_path, asset_id)
            proxies['preview'] = await self._generate_video_preview(file_path, asset_id)
            proxies['proxy_720p'] = await self._generate_video_proxy(file_path, asset_id, '720p')

        elif mime_type.startswith('image/'):
            # Generate image proxies
            proxies['thumbnail'] = await self._generate_image_thumbnail(file_path, asset_id)
            proxies['preview'] = await self._generate_image_preview(file_path, asset_id)

        elif mime_type.startswith('audio/'):
            # Generate audio waveform
            proxies['waveform'] = await self._generate_audio_waveform(file_path, asset_id)

        return proxies

    async def _generate_video_thumbnail(self, file_path: str, asset_id: str) -> str:
        """Generate video thumbnail"""

        import subprocess

        output_path = self.storage_path / 'thumbnails' / f"{asset_id}.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-ss', '00:00:01',  # 1 second in
            '-vframes', '1',
            '-vf', 'scale=320:-1',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)

        return str(output_path)

    async def _generate_video_preview(self, file_path: str, asset_id: str) -> str:
        """Generate video preview (low-res)"""

        import subprocess

        output_path = self.storage_path / 'previews' / f"{asset_id}_preview.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-vf', 'scale=640:-1',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '28',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)

        return str(output_path)

    async def _generate_video_proxy(self, file_path: str, asset_id: str, resolution: str) -> str:
        """Generate video proxy at specific resolution"""

        import subprocess

        output_path = self.storage_path / 'proxies' / f"{asset_id}_{resolution}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Resolution mapping
        res_map = {
            '720p': '1280:720',
            '1080p': '1920:1080'
        }

        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-vf', f'scale={res_map.get(resolution, "1280:720")}',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)

        return str(output_path)

    async def _generate_image_thumbnail(self, file_path: str, asset_id: str) -> str:
        """Generate image thumbnail"""

        from PIL import Image

        output_path = self.storage_path / 'thumbnails' / f"{asset_id}.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file_path)
        img.thumbnail((320, 320))
        img.save(output_path, 'JPEG', quality=85)

        return str(output_path)

    async def _generate_image_preview(self, file_path: str, asset_id: str) -> str:
        """Generate image preview"""

        from PIL import Image

        output_path = self.storage_path / 'previews' / f"{asset_id}.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file_path)
        img.thumbnail((1920, 1920))
        img.save(output_path, 'JPEG', quality=90)

        return str(output_path)

    async def _generate_audio_waveform(self, file_path: str, asset_id: str) -> str:
        """Generate audio waveform image"""

        # In production: use librosa or similar
        # Mock implementation for now

        output_path = self.storage_path / 'waveforms' / f"{asset_id}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return str(output_path)

    async def _store_asset(self, file_path: str, asset_id: str, proxies: Dict) -> Dict:
        """Store asset and proxies"""

        import shutil

        # Create asset directory
        asset_dir = self.storage_path / 'assets' / asset_id
        asset_dir.mkdir(parents=True, exist_ok=True)

        # Copy original file
        original_path = asset_dir / 'original' / Path(file_path).name
        original_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, original_path)

        storage_info = {
            'original': str(original_path),
            'proxies': proxies,
            'storage_tier': 'hot'
        }

        return storage_info

    async def _index_asset(self, asset_id: str, metadata: Dict, technical: Dict):
        """Index asset for search"""

        # Index in Elasticsearch
        # Mock implementation

        document = {
            'asset_id': asset_id,
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'tags': metadata.get('tags', []),
            'creator': metadata.get('creator', ''),
            'created_date': metadata.get('created_date'),
            'technical': technical
        }

        print(f"Indexed asset {asset_id}")

    async def _store_metadata(self, asset_id: str, metadata: Dict):
        """Store asset metadata"""

        # Store in database
        # Mock implementation

        print(f"Stored metadata for asset {asset_id}")

    def _generate_asset_id(self, file_path: str) -> str:
        """Generate unique asset ID"""

        import uuid
        import time

        timestamp = str(time.time())
        filename = Path(file_path).name

        unique_string = f"{timestamp}_{filename}"
        asset_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16]

        return f"asset_{asset_id}"

    def _mime_to_extensions(self, mime_type: str) -> list:
        """Map MIME type to expected file extensions"""

        mime_map = {
            'video/mp4': ['.mp4', '.m4v'],
            'video/quicktime': ['.mov'],
            'video/x-msvideo': ['.avi'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'image/tiff': ['.tif', '.tiff'],
            'audio/mpeg': ['.mp3'],
            'audio/wav': ['.wav'],
            'audio/flac': ['.flac'],
            'application/pdf': ['.pdf']
        }

        return mime_map.get(mime_type, [])
```

## Phase 2: Metadata Management

### 2.1 Metadata Schema

```python
# metadata_schema.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class AssetType(Enum):
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"

class RightsStatus(Enum):
    AVAILABLE = "available"
    RESTRICTED = "restricted"
    EXPIRED = "expired"
    NEGOTIATING = "negotiating"

@dataclass
class DublinCoreMetadata:
    """Dublin Core metadata standard"""
    title: str
    creator: str
    subject: List[str] = field(default_factory=list)
    description: str = ""
    publisher: str = ""
    contributor: List[str] = field(default_factory=list)
    date: Optional[datetime] = None
    type: str = ""
    format: str = ""
    identifier: str = ""
    source: str = ""
    language: str = "en"
    relation: List[str] = field(default_factory=list)
    coverage: str = ""
    rights: str = ""

@dataclass
class TechnicalMetadata:
    """Technical metadata for media assets"""
    file_format: str
    codec: str
    duration: float  # seconds
    file_size: int  # bytes
    resolution: Optional[str] = None  # e.g., "1920x1080"
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    color_space: Optional[str] = None

@dataclass
class RightsMetadata:
    """Rights and licensing metadata"""
    copyright_holder: str
    license_type: str
    usage_rights: List[str] = field(default_factory=list)
    territory: List[str] = field(default_factory=list)  # Geographic restrictions
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    restrictions: str = ""
    contact: str = ""

@dataclass
class AssetMetadata:
    """Complete asset metadata"""
    asset_id: str
    asset_type: AssetType
    dublin_core: DublinCoreMetadata
    technical: TechnicalMetadata
    rights: RightsMetadata
    custom_fields: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

## Best Practices

1. **Validate all uploads**: Check file type, size, integrity
2. **Generate proxies**: Thumbnails, previews for fast browsing
3. **Extract metadata**: Auto-extract technical metadata
4. **Index for search**: Full-text search across all fields
5. **Track versions**: Maintain history of all changes
6. **Implement workflows**: Automate common tasks
7. **Control access**: Role-based permissions
8. **Monitor rights**: Track license expiration
9. **Backup regularly**: Multi-region replication
10. **Archive cold assets**: Move to cheaper storage tiers

## Performance Targets

- **Upload speed**: > 100 MB/s
- **Ingest time**: < 2 minutes per file
- **Search latency**: < 200ms
- **Thumbnail generation**: < 30 seconds
- **Metadata extraction**: < 1 minute
- **Availability**: 99.9% uptime

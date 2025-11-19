# Metadata Standards Quick Reference

## Standard Comparison

| Standard | Domain | Complexity | Adoption | Best For |
|----------|--------|------------|----------|----------|
| **Dublin Core** | General | Low | Universal | Basic metadata |
| **PBCore** | Broadcasting | Medium | Broadcasting | Public media |
| **EIDR** | Entertainment | Low | Film/TV | Unique identification |
| **ISAN** | Audiovisual | Low | International | Global works |
| **EBUCore** | Broadcasting | High | European | Professional media |
| **IPTC** | News/Photos | Medium | Journalism | Photo metadata |
| **XMP** | Adobe | Medium | Creative | Embedded metadata |

## Dublin Core Elements

| Element | Required | Description | Example |
|---------|----------|-------------|---------|
| **Title** | Yes | Name of resource | "The Matrix" |
| **Creator** | Yes | Primary author | "Wachowski Sisters" |
| **Subject** | No | Topic/keywords | "Science Fiction, Action" |
| **Description** | No | Summary | "A hacker discovers reality..." |
| **Publisher** | No | Responsible entity | "Warner Bros" |
| **Contributor** | No | Other contributors | "Keanu Reeves, Producer" |
| **Date** | No | Creation date | "1999-03-31" |
| **Type** | No | Nature/genre | "Motion Picture" |
| **Format** | No | File format | "video/mp4" |
| **Identifier** | No | Unique ID | "EIDR:10.5240/..." |
| **Source** | No | Derived from | "Original Production" |
| **Language** | No | Language | "en-US" |
| **Relation** | No | Related resources | "Part of Matrix Trilogy" |
| **Coverage** | No | Spatial/temporal | "United States, 1999" |
| **Rights** | No | Rights statement | "© 1999 Warner Bros" |

## EIDR (Entertainment Identifier Registry)

### Format
```
EIDR:10.5240/[checksum]-[type]-[content-identifier]

Example: EIDR:10.5240/7791-8534-2C23-9030-8610-5
```

### Content Types
- **0**: Movie
- **1**: TV Series
- **2**: TV Season
- **3**: TV Episode
- **4**: Short
- **5**: Web Original
- **6**: Supplemental Content

### Registration Requirements
- Title
- Release year
- Type
- Primary language
- Alternate IDs (IMDb, etc.)

## PBCore (Public Broadcasting Core)

### Key Elements

| Element | Usage | Example |
|---------|-------|---------|
| **pbcoreTitle** | Multiple types | Main title, Episode title |
| **pbcoreDescription** | Summary/Abstract | Program description |
| **pbcoreGenre** | Classification | Documentary, News |
| **pbcoreRelation** | Relationships | Part of series |
| **pbcoreRightsSummary** | Rights info | Broadcast rights |
| **pbcoreInstantiation** | Technical details | Format, bitrate |

### Asset Types
- **Program**: Complete show
- **Episode**: Single episode
- **Segment**: Part of program
- **Clip**: Short excerpt
- **Raw Footage**: Unedited material

## Technical Metadata Fields

### Video

| Field | Format | Example | Standard |
|-------|--------|---------|----------|
| **Codec** | String | H.264, H.265, VP9 | ffprobe |
| **Resolution** | WxH | 1920x1080 | ffprobe |
| **Frame Rate** | Decimal | 23.976, 29.97 | ffprobe |
| **Aspect Ratio** | Ratio | 16:9, 2.39:1 | ffprobe |
| **Bitrate** | Integer (kbps) | 10000 | ffprobe |
| **Duration** | Seconds | 7200.5 | ffprobe |
| **Color Space** | String | Rec.709, DCI-P3 | ffprobe |
| **Scan Type** | String | Progressive, Interlaced | ffprobe |

### Audio

| Field | Format | Example |
|-------|--------|---------|
| **Codec** | String | AAC, PCM, Opus |
| **Sample Rate** | Hz | 48000, 44100 |
| **Channels** | Integer | 2, 6 (5.1) |
| **Bit Depth** | Bits | 16, 24 |
| **Bitrate** | kbps | 192, 320 |
| **Loudness** | LUFS | -14, -23 |

## Rights & Licensing Fields

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| **Copyright Holder** | String | "Warner Bros Entertainment" | Owner |
| **License Type** | Enum | Exclusive, Non-exclusive | Usage type |
| **Territory** | List | ["US", "CA", "MX"] | Geographic rights |
| **Media Rights** | List | ["Broadcast", "Streaming"] | Distribution |
| **Start Date** | Date | 2024-01-01 | License begins |
| **End Date** | Date | 2029-12-31 | License expires |
| **Restrictions** | Text | "No theatrical" | Limitations |

### Common License Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Exclusive** | Only one licensee | Major releases |
| **Non-Exclusive** | Multiple licensees | Library content |
| **Perpetual** | No expiration | Acquired content |
| **Term-Limited** | Fixed duration | Licensed content |
| **Revenue Share** | Percentage-based | Independent films |
| **Royalty-Free** | One-time fee | Stock footage |

## Controlled Vocabularies

### Genres (EIDR)

```
Action, Animation, Biography, Comedy, Crime, Documentary,
Drama, Family, Fantasy, Film-Noir, Game-Show, History,
Horror, Music, Musical, Mystery, News, Reality-TV, Romance,
Sci-Fi, Short, Sport, Talk-Show, Thriller, War, Western
```

### Content Ratings (MPAA)

| Rating | Description | Age |
|--------|-------------|-----|
| **G** | General Audiences | All |
| **PG** | Parental Guidance | All |
| **PG-13** | Parents Strongly Cautioned | 13+ |
| **R** | Restricted | 17+ |
| **NC-17** | Adults Only | 18+ |

### Production Status

```
Development, Pre-Production, In Production,
Post-Production, Completed, Released, Archived
```

## Search & Discovery Fields

### Faceted Search Categories

| Facet | Type | Example Values |
|-------|------|----------------|
| **Type** | Enum | Video, Audio, Image, Document |
| **Genre** | List | Action, Drama, Comedy |
| **Year** | Range | 2020-2024 |
| **Language** | ISO 639 | en, es, fr |
| **Duration** | Range | 0-30m, 30-60m, 60-120m |
| **Resolution** | Enum | SD, HD, 4K, 8K |
| **Format** | List | MP4, MOV, AVI |

### Recommended Indexes

```sql
-- Full-text search
CREATE INDEX idx_fulltext ON assets USING GIN(
  to_tsvector('english', title || ' ' || description)
);

-- Faceted search
CREATE INDEX idx_genre ON assets(genre);
CREATE INDEX idx_year ON assets(created_year);
CREATE INDEX idx_type ON assets(asset_type);

-- Date range
CREATE INDEX idx_created ON assets(created_at);
CREATE INDEX idx_license_expiry ON assets(rights_end_date);

-- Performance
CREATE INDEX idx_popularity ON assets(view_count DESC);
```

## Metadata Validation Rules

### Required Fields

```yaml
required_fields:
  - title
  - asset_type
  - creator
  - created_date
  - file_format
  - file_size
  - checksum

conditional_required:
  video:
    - resolution
    - codec
    - duration
  audio:
    - sample_rate
    - codec
    - duration
  image:
    - resolution
    - color_space
```

### Field Constraints

| Field | Min Length | Max Length | Pattern |
|-------|-----------|------------|---------|
| **Title** | 1 | 255 | Any |
| **Description** | 0 | 5000 | Any |
| **EIDR** | 26 | 26 | `EIDR:10.5240/...` |
| **Email** | 5 | 254 | RFC 5322 |
| **URL** | 10 | 2048 | http(s):// |
| **Phone** | 10 | 20 | +1234567890 |

## Storage Tiers

| Tier | Access Time | Cost/GB/Month | Use Case |
|------|-------------|---------------|----------|
| **Hot** | < 10ms | $0.023 | Active assets |
| **Warm** | < 1s | $0.01 | Occasional access |
| **Cold** | < 1min | $0.004 | Archive |
| **Glacier** | < 1hour | $0.001 | Long-term archive |

### Lifecycle Rules

```
Age 30 days → Move to Warm
Age 90 days → Move to Cold
Age 365 days → Move to Glacier
Age 2555 days (7 years) → Delete (if retention allows)
```

## API Response Format

### Asset Detail Response

```json
{
  "asset_id": "asset_abc123",
  "type": "video",
  "title": "Sample Video",
  "description": "A sample video asset",
  "metadata": {
    "dublin_core": {
      "creator": "John Doe",
      "date": "2024-01-01",
      "language": "en"
    },
    "technical": {
      "format": "mp4",
      "codec": "H.264",
      "resolution": "1920x1080",
      "duration": 180.5,
      "bitrate": 5000,
      "file_size": 112640000
    },
    "rights": {
      "copyright": "© 2024 Example Corp",
      "license": "Exclusive",
      "territory": ["US", "CA"],
      "expires": "2029-12-31"
    }
  },
  "files": {
    "original": "s3://bucket/assets/abc123/original.mp4",
    "proxies": {
      "thumbnail": "s3://bucket/thumbnails/abc123.jpg",
      "preview": "s3://bucket/previews/abc123.mp4",
      "720p": "s3://bucket/proxies/abc123_720p.mp4"
    }
  },
  "checksums": {
    "md5": "5d41402abc4b2a76b9719d911017c592",
    "sha256": "6c3f4e..."
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-02T08:30:00Z"
}
```

## Best Practices

1. **Use standard vocabularies** for interoperability
2. **Validate on input** to maintain data quality
3. **Index strategically** for fast search
4. **Version metadata** to track changes
5. **Normalize formats** (dates, languages, codes)
6. **Extract automatically** where possible
7. **Enrich progressively** over time
8. **Cache frequently accessed** metadata
9. **Backup metadata** separately from assets
10. **Monitor completeness** with quality scores

## Common Pitfalls

- **Missing required fields**: Validate on upload
- **Inconsistent formats**: Use controlled vocabularies
- **Duplicate entries**: Check before creating
- **Orphaned metadata**: Cascade deletes
- **Outdated licenses**: Monitor expiration
- **Poor search results**: Improve indexing
- **Slow queries**: Add indexes
- **Data loss**: Regular backups

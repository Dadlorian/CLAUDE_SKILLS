# MLS/RESO Integration Guide

**Version:** 2.5
**Last Updated:** 2025-01-15
**Status:** Active Standard
**Authority:** Real Estate Standards Organization (RESO)
**References:** RESO Web API Specification, RETS 1.8, MLS Grid, CoreLogic, RPR

## Table of Contents

1. [Overview](#overview)
2. [RETS (Real Estate Transaction Standard)](#rets-real-estate-transaction-standard)
3. [RESO Web API](#reso-web-api)
4. [MLS Data Dictionary](#mls-data-dictionary)
5. [Authentication Methods](#authentication-methods)
6. [Data Synchronization Patterns](#data-synchronization-patterns)
7. [Media Handling](#media-handling)
8. [Compliance Requirements](#compliance-requirements)
9. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
10. [Error Handling](#error-handling)
11. [Real-World Implementation Examples](#real-world-implementation-examples)

## Overview

Multiple Listing Services (MLS) provide access to real estate listing data through standardized APIs. This guide covers integration with MLS systems using both legacy RETS (Real Estate Transaction Standard) and modern RESO Web API standards.

### Key MLS Providers

| Provider | Coverage | API Type | Notes |
|----------|----------|----------|-------|
| **MLS Grid** | 50+ MLSs, nationwide | RESO Web API | Cloud-based aggregation |
| **CoreLogic (Matrix)** | Largest MLS provider | RETS, RESO Web API | Powers 200+ MLSs |
| **Realtors Property Resource (RPR)** | National (NAR) | RESO Web API | Aggregated national data |
| **Local MLSs** | Regional | RETS (legacy), RESO | Direct MLS access |
| **ListHub** | Syndication | RESO Web API | Zillow, Trulia, Realtor.com |

### Integration Architecture

```
PropTech Platform
       ↓
   MLS Gateway Service
       ↓
   ┌───────┴───────┐
   ↓               ↓
RETS Client    RESO Web API Client
   ↓               ↓
Legacy MLSs    Modern MLSs
```

### Data Flow

1. **Authentication**: OAuth 2.0 (RESO) or Digest Auth (RETS)
2. **Query**: Search for listings by criteria
3. **Fetch Listings**: Retrieve listing details
4. **Fetch Media**: Download photos, virtual tours, documents
5. **Incremental Updates**: Poll for changes (delta queries)
6. **Normalize**: Map MLS fields to internal schema
7. **Store**: Save to local database with MLS attribution

## RETS (Real Estate Transaction Standard)

RETS 1.8 is the legacy standard (1999-2016), still used by many MLSs.

### RETS Architecture

**Transport:** HTTP/HTTPS with Digest Authentication
**Data Format:** XML
**Operations:**
- Login
- Search
- GetObject (media)
- GetMetadata
- Logout

### RETS Authentication

**Digest Authentication (RFC 2617):**

```python
import requests
from requests.auth import HTTPDigestAuth

class RETSClient:
    def __init__(self, url, username, password, user_agent):
        self.url = url
        self.username = username
        self.password = password
        self.user_agent = user_agent  # Required, registered with MLS
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(username, password)
        self.session.headers.update({
            "User-Agent": user_agent,
            "RETS-Version": "RETS/1.8"
        })
        self.login_url = None
        self.search_url = None
        self.getobject_url = None

    def login(self):
        """
        Login and retrieve capability URLs
        """
        response = self.session.get(f"{self.url}/Login")
        response.raise_for_status()

        # Parse response headers for capability URLs
        # Example: "Search=/rets/search,GetObject=/rets/getobject"
        capability_urls = response.headers.get("RETS-Response", "")

        # Parse XML response body
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)

        # Extract capability URLs from RETS-RESPONSE
        self.search_url = f"{self.url}/Search"
        self.getobject_url = f"{self.url}/GetObject"

        return root.attrib["ReplyCode"] == "0"  # 0 = success

    def search(self, resource, class_name, query, limit=100):
        """
        Search for listings

        Args:
            resource: "Property" (typical)
            class_name: "Residential", "Commercial", etc.
            query: DMQL query string
            limit: Max records to return
        """
        params = {
            "SearchType": resource,
            "Class": class_name,
            "Query": query,
            "Format": "COMPACT-DECODED",
            "Limit": limit,
            "Select": "ListingKey,ListPrice,City,StateOrProvince,PostalCode,BedroomsTotal,BathroomsTotalInteger,PropertyType,StandardStatus,ListingContractDate,ModificationTimestamp,Media"
        }

        response = self.session.get(self.search_url, params=params)
        response.raise_for_status()

        return self.parse_compact_format(response.content)

    def parse_compact_format(self, content):
        """
        Parse RETS COMPACT-DECODED format
        """
        from xml.etree import ElementTree as ET
        root = ET.fromstring(content)

        # Extract column names
        columns_elem = root.find(".//COLUMNS")
        if columns_elem is None:
            return []
        columns = columns_elem.text.split("\t")

        # Extract data rows
        data_rows = []
        for data_elem in root.findall(".//DATA"):
            values = data_elem.text.split("\t")
            row = dict(zip(columns, values))
            data_rows.append(row)

        return data_rows

    def get_object(self, resource, object_type, resource_id, object_id=0):
        """
        Fetch media (photos, documents)

        Args:
            resource: "Property"
            object_type: "Photo", "Document"
            resource_id: ListingKey
            object_id: 0 for all, 1-N for specific object
        """
        params = {
            "Type": object_type,
            "Resource": resource,
            "ID": f"{resource_id}:{object_id}"  # "12345:0" for all photos
        }

        response = self.session.get(self.getobject_url, params=params)
        response.raise_for_status()

        # Parse multipart response (multiple images)
        return self.parse_multipart_response(response)

    def parse_multipart_response(self, response):
        """
        Parse multipart/parallel response for multiple objects
        """
        import email
        from email import policy

        # Parse multipart message
        msg = email.message_from_bytes(
            response.content,
            policy=policy.default
        )

        objects = []
        if msg.is_multipart():
            for part in msg.iter_parts():
                content_id = part.get("Content-ID", "")
                content_type = part.get_content_type()
                object_id = part.get("Object-ID", "")
                location = part.get("Location", "")

                objects.append({
                    "object_id": object_id,
                    "content_type": content_type,
                    "content": part.get_payload(decode=True),
                    "location": location
                })
        else:
            # Single object
            objects.append({
                "object_id": "1",
                "content_type": response.headers["Content-Type"],
                "content": response.content
            })

        return objects

    def logout(self):
        """
        Logout and end session
        """
        logout_url = f"{self.url}/Logout"
        response = self.session.get(logout_url)
        return response.status_code == 200
```

### RETS DMQL Queries

**Data Model Query Language (DMQL):**

```python
# Active residential listings in San Francisco
query = "(StandardStatus=Active),(City=San Francisco),(PropertyType=Residential)"

# Price range
query = "(ListPrice=200000-500000)"

# Date range (last 7 days)
query = "(ModificationTimestamp=2025-01-08T00:00:00+)"

# Complex query
query = "(StandardStatus=|Active,Pending),(PropertyType=Residential),(City=|San Francisco,Oakland),(BedroomsTotal=2+),(ListPrice=500000-1000000)"

# Search
results = client.search(
    resource="Property",
    class_name="Residential",
    query=query,
    limit=500
)
```

### RETS Metadata

**Fetch Field Definitions:**

```python
def get_metadata(self, metadata_type, resource=""):
    """
    Fetch metadata (field definitions, lookup values)

    Types: METADATA-SYSTEM, METADATA-RESOURCE, METADATA-CLASS,
           METADATA-TABLE, METADATA-LOOKUP, METADATA-LOOKUP_TYPE
    """
    params = {
        "Type": metadata_type,
        "ID": resource
    }

    response = self.session.get(f"{self.url}/GetMetadata", params=params)
    return self.parse_metadata(response.content)

# Example: Get field definitions for Residential class
metadata = client.get_metadata("METADATA-TABLE", "Property:Residential")

# Returns field information:
# - SystemName (ListPrice, BedroomsTotal)
# - DataType (Int, Decimal, Character)
# - MaxLength
# - Required
# - Searchable
```

## RESO Web API

Modern OData-based API standard (2016+), replacing RETS.

### RESO Web API Authentication

**OAuth 2.0 Client Credentials Flow:**

```python
import requests

class RESOWebAPIClient:
    def __init__(self, token_url, client_id, client_secret, api_base_url):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base_url = api_base_url
        self.access_token = None

    def authenticate(self):
        """
        Get OAuth 2.0 access token
        """
        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "OData"  # MLS-specific scope
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expires_in = token_data["expires_in"]

        return self.access_token

    def get_headers(self):
        """
        Standard headers for API requests
        """
        if not self.access_token:
            self.authenticate()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "OData-Version": "4.0"
        }
```

### RESO OData Queries

**OData Query Syntax:**

```python
# GET /Property?$filter=StandardStatus eq 'Active' and City eq 'San Francisco'

def search_properties(self, filters=None, select=None, orderby=None, top=100, skip=0):
    """
    Search properties using OData syntax
    """
    params = {}

    # Filter
    if filters:
        params["$filter"] = filters

    # Select specific fields
    if select:
        params["$select"] = ",".join(select)

    # Sort
    if orderby:
        params["$orderby"] = orderby

    # Pagination
    params["$top"] = top
    params["$skip"] = skip

    # Count
    params["$count"] = "true"

    response = requests.get(
        f"{self.api_base_url}/Property",
        headers=self.get_headers(),
        params=params
    )

    response.raise_for_status()
    return response.json()

# Example queries

# Active listings in San Francisco
results = client.search_properties(
    filters="StandardStatus eq 'Active' and City eq 'San Francisco'",
    select=["ListingKey", "ListPrice", "BedroomsTotal", "BathroomsTotalInteger"],
    orderby="ListPrice desc",
    top=50
)

# Price range
results = client.search_properties(
    filters="ListPrice ge 500000 and ListPrice le 1000000"
)

# Date range (last 7 days)
results = client.search_properties(
    filters="ModificationTimestamp ge 2025-01-08T00:00:00Z"
)

# Complex filter
results = client.search_properties(
    filters="StandardStatus in ('Active','Pending') and PropertyType eq 'Residential' and City in ('San Francisco','Oakland') and BedroomsTotal ge 2"
)

# Geographic search (within bounding box)
results = client.search_properties(
    filters="Latitude ge 37.7 and Latitude le 37.8 and Longitude ge -122.5 and Longitude le -122.4"
)
```

**OData Operators:**

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equal | `StandardStatus eq 'Active'` |
| `ne` | Not equal | `PropertyType ne 'Land'` |
| `gt` | Greater than | `ListPrice gt 500000` |
| `ge` | Greater than or equal | `BedroomsTotal ge 3` |
| `lt` | Less than | `ListPrice lt 1000000` |
| `le` | Less than or equal | `DaysOnMarket le 30` |
| `in` | In list | `City in ('SF','Oakland')` |
| `and` | Logical AND | `condition1 and condition2` |
| `or` | Logical OR | `condition1 or condition2` |
| `not` | Logical NOT | `not (StandardStatus eq 'Closed')` |
| `contains` | String contains | `contains(City,'San')` |
| `startswith` | String starts with | `startswith(PostalCode,'94')` |

### RESO Media Endpoint

```python
def get_media(self, listing_key):
    """
    Fetch all media for a listing
    """
    response = requests.get(
        f"{self.api_base_url}/Property('{listing_key}')/Media",
        headers=self.get_headers()
    )

    response.raise_for_status()
    media_items = response.json()["value"]

    # Download each media item
    for media in media_items:
        media_url = media["MediaURL"]
        media_type = media["MediaCategory"]  # Photo, Video, Document
        media_order = media["Order"]

        # Download media
        media_content = self.download_media(media_url)

        # Save locally
        self.save_media(listing_key, media_type, media_order, media_content)

    return media_items

def download_media(self, media_url):
    """
    Download media from URL
    """
    response = requests.get(
        media_url,
        headers=self.get_headers(),
        stream=True
    )

    response.raise_for_status()
    return response.content
```

### RESO Metadata Endpoint

```python
def get_metadata(self):
    """
    Fetch metadata (field definitions)
    """
    response = requests.get(
        f"{self.api_base_url}/$metadata",
        headers=self.get_headers()
    )

    response.raise_for_status()
    return response.content  # XML format (EDMX)

# Parse metadata to understand available fields
import xml.etree.ElementTree as ET

def parse_metadata(self, metadata_xml):
    """
    Parse RESO metadata to extract field definitions
    """
    root = ET.fromstring(metadata_xml)
    namespaces = {
        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
        'edm': 'http://docs.oasis-open.org/odata/ns/edm'
    }

    # Find Property entity type
    entity_type = root.find(".//edm:EntityType[@Name='Property']", namespaces)

    fields = []
    for prop in entity_type.findall(".//edm:Property", namespaces):
        field = {
            "name": prop.attrib["Name"],
            "type": prop.attrib["Type"],
            "nullable": prop.attrib.get("Nullable", "true") == "true",
            "max_length": prop.attrib.get("MaxLength")
        }
        fields.append(field)

    return fields
```

## MLS Data Dictionary

### RESO Standard Fields

**Property Resource (Residential):**

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| **ListingKey** | String | Unique listing ID | "3yd-NWMLS-12345" |
| **ListingId** | String | Human-readable ID | "12345678" |
| **StandardStatus** | Enum | Active, Pending, Closed, Expired | "Active" |
| **ListPrice** | Decimal | Current list price | 750000 |
| **OriginalListPrice** | Decimal | Initial list price | 795000 |
| **ClosePrice** | Decimal | Sold price | 760000 |
| **ListingContractDate** | DateTime | Listing start date | "2025-01-01" |
| **CloseDate** | DateTime | Sale close date | "2025-02-15" |
| **DaysOnMarket** | Int | Days on market | 45 |
| **CumulativeDaysOnMarket** | Int | Total days (including previous listings) | 60 |
| **PropertyType** | Enum | Residential, Commercial, Land | "Residential" |
| **PropertySubType** | Enum | SingleFamily, Condominium, Townhouse | "Condominium" |
| **BedroomsTotal** | Int | Number of bedrooms | 3 |
| **BathroomsTotalInteger** | Int | Total bathrooms (integer) | 2 |
| **BathroomsFull** | Int | Full bathrooms | 2 |
| **BathroomsHalf** | Int | Half bathrooms | 1 |
| **LivingArea** | Decimal | Square footage | 1850 |
| **LotSizeSquareFeet** | Decimal | Lot size | 5000 |
| **YearBuilt** | Int | Year constructed | 2015 |
| **UnparsedAddress** | String | Full address | "123 Main St, San Francisco, CA 94102" |
| **StreetNumber** | String | Street number | "123" |
| **StreetName** | String | Street name | "Main" |
| **StreetSuffix** | Enum | St, Ave, Blvd, Dr | "St" |
| **City** | String | City | "San Francisco" |
| **StateOrProvince** | Enum | CA, NY, TX | "CA" |
| **PostalCode** | String | ZIP code | "94102" |
| **Country** | Enum | US, CA, MX | "US" |
| **Latitude** | Decimal | Latitude | 37.7749 |
| **Longitude** | Decimal | Longitude | -122.4194 |
| **ListAgentKey** | String | Listing agent ID | "agent_123" |
| **ListAgentFullName** | String | Agent name | "Jane Smith" |
| **ListOfficeName** | String | Brokerage | "Compass" |
| **PublicRemarks** | Text | Public description | "Stunning 3BR condo..." |
| **PrivateRemarks** | Text | Agent notes | "Seller motivated..." |
| **ModificationTimestamp** | DateTime | Last modified | "2025-01-15T10:30:00Z" |

**Lookup Values (Enums):**

```
StandardStatus: Active, ActiveUnderContract, Pending, Hold, Closed, Expired, Canceled, Delete, Incomplete, ComingSoon

PropertyType: Residential, Commercial, Land, Rental, Business Opportunity

PropertySubType: SingleFamily, Condominium, Townhouse, Manufactured, Cooperative, MultiFamily

Appliances: Dishwasher, Dryer, Refrigerator, Washer, Microwave, Oven, Range

Heating: ForcedAir, Radiant, HeatPump, Baseboard, Electric, Gas

Cooling: CentralAir, WindowUnit, HeatPump, EvaporativeCooler, None
```

## Authentication Methods

### OAuth 2.0 (RESO Standard)

**Authorization Code Flow (User Authorization):**

```python
# Step 1: Redirect user to authorization URL
authorization_url = f"{auth_endpoint}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=OData&state={state}"

# Step 2: User approves, receives authorization code
# Redirect: https://yourapp.com/callback?code=AUTH_CODE&state=STATE

# Step 3: Exchange code for access token
token_response = requests.post(
    token_endpoint,
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
)

access_token = token_response.json()["access_token"]
refresh_token = token_response.json()["refresh_token"]

# Step 4: Use access token
response = requests.get(
    f"{api_base_url}/Property",
    headers={"Authorization": f"Bearer {access_token}"}
)
```

**Client Credentials Flow (Server-to-Server):**

```python
# Direct token request (no user interaction)
token_response = requests.post(
    token_endpoint,
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "OData"
    }
)

access_token = token_response.json()["access_token"]
```

**Token Refresh:**

```python
def refresh_access_token(self, refresh_token):
    """
    Refresh expired access token
    """
    response = requests.post(
        self.token_url,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
    )

    response.raise_for_status()
    token_data = response.json()
    self.access_token = token_data["access_token"]

    # Some providers issue new refresh token
    if "refresh_token" in token_data:
        self.refresh_token = token_data["refresh_token"]

    return self.access_token
```

## Data Synchronization Patterns

### Initial Full Sync

```python
def initial_sync(self):
    """
    Full sync of all active listings
    """
    page_size = 500
    skip = 0
    total_synced = 0

    while True:
        # Fetch batch of listings
        results = self.client.search_properties(
            filters="StandardStatus in ('Active','Pending','ActiveUnderContract')",
            top=page_size,
            skip=skip
        )

        listings = results["value"]
        if not listings:
            break  # No more results

        # Process batch
        for listing in listings:
            self.save_listing(listing)
            total_synced += 1

        # Next page
        skip += page_size

        # Rate limiting (respect MLS limits)
        time.sleep(1)  # 1 second between batches

    print(f"Initial sync complete: {total_synced} listings")
```

### Incremental Delta Sync

**Recommended:** Sync every 15-60 minutes using `ModificationTimestamp`

```python
import datetime

def incremental_sync(self, last_sync_time):
    """
    Sync only changed listings since last sync
    """
    # Format timestamp for OData
    timestamp_filter = f"ModificationTimestamp ge {last_sync_time.isoformat()}Z"

    results = self.client.search_properties(
        filters=timestamp_filter,
        top=1000  # Adjust based on expected change volume
    )

    listings = results["value"]

    for listing in listings:
        # Check status
        if listing["StandardStatus"] in ["Active", "Pending", "ActiveUnderContract"]:
            self.save_listing(listing)
        elif listing["StandardStatus"] in ["Closed", "Expired", "Canceled", "Delete"]:
            self.remove_listing(listing["ListingKey"])

    # Update last sync time
    self.save_last_sync_time(datetime.datetime.utcnow())

    return len(listings)

# Schedule incremental sync every 15 minutes
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=lambda: incremental_sync(get_last_sync_time()),
    trigger="interval",
    minutes=15
)
scheduler.start()
```

### Change Detection

```python
def save_listing(self, mls_listing):
    """
    Save or update listing in local database
    """
    listing_key = mls_listing["ListingKey"]

    # Check if exists
    existing = self.db.get_listing_by_mls_key(listing_key)

    if existing:
        # Compare modification timestamps
        if mls_listing["ModificationTimestamp"] > existing.modification_timestamp:
            # Update listing
            self.db.update_listing(listing_key, self.normalize_listing(mls_listing))
            self.sync_media(listing_key)
        # else: No changes, skip
    else:
        # New listing
        self.db.create_listing(self.normalize_listing(mls_listing))
        self.sync_media(listing_key)

def remove_listing(self, listing_key):
    """
    Remove or mark listing as inactive
    """
    # Soft delete (preserve history)
    self.db.mark_listing_inactive(listing_key)

    # Or hard delete
    # self.db.delete_listing(listing_key)
```

### Field Mapping

```python
def normalize_listing(self, mls_listing):
    """
    Map MLS fields to internal schema
    """
    return {
        "mls_listing_key": mls_listing["ListingKey"],
        "mls_id": mls_listing["ListingId"],
        "status": self.map_status(mls_listing["StandardStatus"]),
        "price": mls_listing["ListPrice"],
        "original_price": mls_listing.get("OriginalListPrice"),
        "bedrooms": mls_listing.get("BedroomsTotal"),
        "bathrooms": mls_listing.get("BathroomsTotalInteger"),
        "square_feet": mls_listing.get("LivingArea"),
        "lot_size": mls_listing.get("LotSizeSquareFeet"),
        "year_built": mls_listing.get("YearBuilt"),
        "property_type": mls_listing.get("PropertyType"),
        "property_subtype": mls_listing.get("PropertySubType"),
        "address": {
            "street_address": mls_listing.get("UnparsedAddress"),
            "city": mls_listing.get("City"),
            "state": mls_listing.get("StateOrProvince"),
            "postal_code": mls_listing.get("PostalCode"),
            "latitude": mls_listing.get("Latitude"),
            "longitude": mls_listing.get("Longitude")
        },
        "description": mls_listing.get("PublicRemarks"),
        "listed_date": mls_listing.get("ListingContractDate"),
        "days_on_market": mls_listing.get("DaysOnMarket"),
        "modification_timestamp": mls_listing["ModificationTimestamp"],
        "listing_agent": {
            "name": mls_listing.get("ListAgentFullName"),
            "mls_key": mls_listing.get("ListAgentKey")
        },
        "mls_source": "NWMLS"  # Track source MLS
    }

def map_status(self, standard_status):
    """
    Map RESO StandardStatus to internal status
    """
    status_map = {
        "Active": "active",
        "ActiveUnderContract": "pending",
        "Pending": "pending",
        "Closed": "sold",
        "Expired": "expired",
        "Canceled": "canceled",
        "Delete": "deleted"
    }
    return status_map.get(standard_status, "unknown")
```

## Media Handling

### Photo Download Strategy

```python
import hashlib
import boto3

def sync_media(self, listing_key):
    """
    Download and store listing photos
    """
    # Fetch media metadata
    media_items = self.client.get_media(listing_key)

    # Filter for photos only
    photos = [m for m in media_items if m["MediaCategory"] == "Photo"]

    # Sort by Order
    photos.sort(key=lambda x: x.get("Order", 999))

    for index, photo in enumerate(photos):
        media_url = photo["MediaURL"]

        # Check if already downloaded (hash-based deduplication)
        url_hash = hashlib.md5(media_url.encode()).hexdigest()
        if self.db.media_exists(url_hash):
            continue  # Skip, already have this photo

        # Download photo
        photo_content = self.download_media(media_url)

        # Upload to S3
        s3_key = f"listings/{listing_key}/photo_{index}.jpg"
        self.upload_to_s3(s3_key, photo_content)

        # Save metadata
        self.db.save_media({
            "listing_key": listing_key,
            "media_type": "photo",
            "order": index,
            "url_hash": url_hash,
            "s3_key": s3_key,
            "original_url": media_url
        })

def upload_to_s3(self, s3_key, content):
    """
    Upload media to S3
    """
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket="proptech-mls-media",
        Key=s3_key,
        Body=content,
        ContentType="image/jpeg",
        CacheControl="public, max-age=31536000"  # 1 year cache
    )
```

### Image Optimization

```python
from PIL import Image
import io

def optimize_image(self, image_content):
    """
    Resize and compress images
    """
    # Open image
    img = Image.open(io.BytesIO(image_content))

    # Create multiple sizes
    sizes = {
        "thumbnail": (300, 200),
        "medium": (800, 600),
        "large": (1600, 1200)
    }

    optimized_images = {}

    for size_name, dimensions in sizes.items():
        # Resize maintaining aspect ratio
        img_copy = img.copy()
        img_copy.thumbnail(dimensions, Image.Resampling.LANCZOS)

        # Compress to JPEG
        buffer = io.BytesIO()
        img_copy.save(buffer, format="JPEG", quality=85, optimize=True)
        optimized_images[size_name] = buffer.getvalue()

    return optimized_images
```

## Compliance Requirements

### MLS Rules and Regulations

**1. Attribution Requirements:**

All listings must display proper attribution:

```
"Listing courtesy of [Brokerage Name]"
"Data provided by [MLS Name]"
"©2025 Northwest Multiple Listing Service. All rights reserved."
```

**2. Data Usage Restrictions:**

- **VOW (Virtual Office Website) Compliance**: Only for licensed brokers
- **IDX (Internet Data Exchange)**: Display on broker websites only
- **No Scraping**: Must use official API, no web scraping
- **No Data Resale**: Cannot sell or redistribute MLS data
- **Timeliness**: Must refresh data at least daily (some MLSs require hourly)
- **Deletion**: Must remove sold/expired listings within 24-48 hours

**3. Data Display Rules:**

- Must display listing agent/office information
- Cannot display sold prices in some MLSs (regional variation)
- Must display listing status accurately
- Cannot alter listing data without permission

**4. User Authentication (VOW):**

```python
def check_vow_access(user):
    """
    Verify user has signed VOW agreement
    """
    if not user.is_authenticated:
        return False

    # User must accept VOW terms
    if not user.vow_agreement_signed:
        return False

    # Track access for compliance audit
    log_vow_access(user.id, datetime.datetime.utcnow())

    return True
```

### DMCA Compliance

**Handle DMCA takedown notices:**

```python
def handle_dmca_takedown(listing_key, takedown_notice):
    """
    Process DMCA takedown request
    """
    # Immediately remove listing
    db.mark_listing_hidden(listing_key, reason="dmca_takedown")

    # Remove media
    db.delete_media_for_listing(listing_key)

    # Log takedown
    db.save_dmca_notice({
        "listing_key": listing_key,
        "received_at": datetime.datetime.utcnow(),
        "notice_details": takedown_notice
    })

    # Notify listing agent
    send_dmca_notification(listing_key, takedown_notice)
```

## Rate Limiting and Throttling

### MLS Rate Limits

| MLS Provider | Rate Limit | Notes |
|--------------|-----------|-------|
| **MLS Grid** | 10 req/sec | Burst: 50 req/sec for 10 sec |
| **CoreLogic** | 5 req/sec | Per API key |
| **RPR** | 1000 req/hour | Daily limit: 10,000 |
| **Local MLSs** | Varies | 1-10 req/sec typical |

### Implementing Rate Limiting

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests_per_second):
        self.max_requests = max_requests_per_second
        self.requests = deque()

    def wait_if_needed(self):
        """
        Throttle requests to stay within rate limit
        """
        now = time.time()

        # Remove requests older than 1 second
        while self.requests and self.requests[0] < now - 1:
            self.requests.popleft()

        # Check if at limit
        if len(self.requests) >= self.max_requests:
            # Wait until oldest request is > 1 second old
            sleep_time = 1 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Record this request
        self.requests.append(time.time())

# Usage
rate_limiter = RateLimiter(max_requests_per_second=5)

def search_with_rate_limit(filters):
    rate_limiter.wait_if_needed()
    return client.search_properties(filters)
```

### Exponential Backoff (429 Responses)

```python
import time
import random

def search_with_retry(filters, max_retries=5):
    """
    Retry with exponential backoff on rate limit errors
    """
    for attempt in range(max_retries):
        try:
            return client.search_properties(filters)
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                retry_after = int(e.response.headers.get("Retry-After", 60))

                # Exponential backoff with jitter
                wait_time = min(retry_after, (2 ** attempt) + random.uniform(0, 1))

                print(f"Rate limited. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise  # Other error, don't retry

    raise Exception(f"Max retries ({max_retries}) exceeded")
```

## Error Handling

### Common Error Scenarios

**1. Authentication Errors:**

```python
try:
    client.authenticate()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        # Invalid credentials
        log_error("MLS authentication failed: Invalid credentials")
        notify_admin("MLS API credentials invalid")
    elif e.response.status_code == 403:
        # Access forbidden (subscription issue)
        log_error("MLS access forbidden: Check subscription status")
```

**2. Query Errors:**

```python
try:
    results = client.search_properties(filters)
except requests.HTTPError as e:
    if e.response.status_code == 400:
        # Bad request (invalid filter syntax)
        error_body = e.response.json()
        log_error(f"Invalid OData query: {error_body}")
```

**3. Media Download Failures:**

```python
def download_media_with_retry(media_url, max_retries=3):
    """
    Retry media downloads on failure
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(media_url, timeout=30)
            response.raise_for_status()
            return response.content
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                log_error(f"Failed to download media after {max_retries} attempts: {media_url}")
                return None
```

## Real-World Implementation Examples

### Complete Sync Service

```python
import logging
from datetime import datetime, timedelta

class MLSSyncService:
    def __init__(self, reso_client, database, s3_client):
        self.client = reso_client
        self.db = database
        self.s3 = s3_client
        self.logger = logging.getLogger(__name__)

    def full_sync(self):
        """
        Full synchronization of all active listings
        """
        self.logger.info("Starting full MLS sync")
        start_time = datetime.utcnow()

        try:
            # Sync active listings
            active_count = self.sync_active_listings()

            # Sync pending listings
            pending_count = self.sync_pending_listings()

            # Clean up expired listings
            removed_count = self.cleanup_expired_listings()

            # Log summary
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(
                f"Full sync complete: {active_count} active, {pending_count} pending, "
                f"{removed_count} removed. Duration: {duration:.2f}s"
            )

            # Update metrics
            self.db.save_sync_metrics({
                "sync_type": "full",
                "active_listings": active_count,
                "pending_listings": pending_count,
                "removed_listings": removed_count,
                "duration_seconds": duration,
                "completed_at": datetime.utcnow()
            })

        except Exception as e:
            self.logger.error(f"Full sync failed: {e}", exc_info=True)
            self.notify_error("MLS full sync failed", str(e))
            raise

    def incremental_sync(self):
        """
        Incremental sync (last 1 hour of changes)
        """
        self.logger.info("Starting incremental MLS sync")

        # Get last sync time (fallback to 1 hour ago)
        last_sync = self.db.get_last_sync_time() or (datetime.utcnow() - timedelta(hours=1))

        # Sync changed listings
        filters = f"ModificationTimestamp ge {last_sync.isoformat()}Z"

        try:
            results = self.client.search_properties(
                filters=filters,
                top=1000
            )

            changed_count = 0
            for listing in results["value"]:
                self.process_listing(listing)
                changed_count += 1

            # Update last sync time
            self.db.save_last_sync_time(datetime.utcnow())

            self.logger.info(f"Incremental sync complete: {changed_count} changes")

        except Exception as e:
            self.logger.error(f"Incremental sync failed: {e}", exc_info=True)
            raise

    def sync_active_listings(self):
        """
        Sync all active listings
        """
        count = 0
        skip = 0
        page_size = 500

        while True:
            results = self.client.search_properties(
                filters="StandardStatus eq 'Active'",
                top=page_size,
                skip=skip
            )

            listings = results["value"]
            if not listings:
                break

            for listing in listings:
                self.process_listing(listing)
                count += 1

            skip += page_size
            time.sleep(0.2)  # Rate limiting

        return count

    def process_listing(self, mls_listing):
        """
        Process single listing (create/update)
        """
        listing_key = mls_listing["ListingKey"]

        try:
            # Normalize data
            normalized = self.normalize_listing(mls_listing)

            # Save to database
            self.db.upsert_listing(listing_key, normalized)

            # Sync media
            if self.should_sync_media(listing_key, mls_listing):
                self.sync_media(listing_key)

        except Exception as e:
            self.logger.error(f"Failed to process listing {listing_key}: {e}")

# Usage
reso_client = RESOWebAPIClient(...)
database = Database(...)
s3_client = S3Client(...)

sync_service = MLSSyncService(reso_client, database, s3_client)

# Run full sync daily
sync_service.full_sync()

# Run incremental sync every 15 minutes
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(sync_service.incremental_sync, 'interval', minutes=15)
scheduler.start()
```

---

## References

1. **RESO Web API Specification**: https://www.reso.org/reso-web-api/
2. **RESO Data Dictionary**: https://ddwiki.reso.org/
3. **RETS 1.8 Specification**: https://www.reso.org/rets-1-8/
4. **MLS Grid**: https://mlsgrid.com/
5. **CoreLogic API Documentation**: https://developer.corelogic.com/
6. **RPR API**: https://blog.narrpr.com/api
7. **OData 4.0 Specification**: https://www.odata.org/documentation/

---

*This document is maintained by the PropTech Integration Standards Committee. For questions or updates, contact integrations@proptech.com.*

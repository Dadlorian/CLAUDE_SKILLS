# MLS/RESO Standards Reference

## Quick Reference for MLS Integration

### RESO (Real Estate Standards Organization)

**Mission**: Create and promote common standards for real estate data

**Key Standards**:
- Data Dictionary
- Web API (replaces RETS)
- Transport (OData/JSON)
- Certification Program

### RETS (Real Estate Transaction Standard)

#### RETS Overview

**Current Version**: 1.7.2 (legacy, being phased out)
**Protocol**: HTTP-based XML
**Authentication**: HTTP Digest or Basic
**Primary Operations**:
- Login
- Search
- GetObject (photos/documents)
- GetMetadata
- Logout

#### RETS Transaction Flow

```
1. Login Request
   POST /rets/login
   Authorization: Digest username="user", ...

2. Login Response (XML)
   <RETS ReplyCode="0" ReplyText="Operation Successful">
     <RETS-RESPONSE>
       MemberName=John Doe
       User=user123
       Broker=BR123
       MetadataVersion=1.0.0
     </RETS-RESPONSE>
   </RETS>

3. GetMetadata Request
   GET /rets/getmetadata?Type=METADATA-RESOURCE&ID=0

4. Search Request
   GET /rets/search?SearchType=Property&Class=RES&Query=(Status=Active)&Limit=100

5. GetObject Request (Photos)
   GET /rets/getobject?Type=Photo&Resource=Property&ID=12345:*

6. Logout
   GET /rets/logout
```

#### RETS Query Syntax (DMQL)

```
Basic Queries:
(Status=Active)
(ListPrice=300000+)
(Bedrooms=3+)
(City=Austin)

Compound Queries:
(Status=Active),(ListPrice=300000-500000)  // AND
(City=Austin|Dallas|Houston)               // OR
(ListDate=2025-01-01+)                     // Date range
(Status=Active),(Bedrooms=3+),(ListPrice=500000-)  // Multiple conditions

Wildcards:
(City=San*)                                // Starts with
(Address=*Main*)                           // Contains
```

#### RETS Response Formats

**COMPACT Format** (most common):
```xml
<RETS ReplyCode="0">
  <DELIMITER value="09"/>
  <COLUMNS>ListingID	Status	Price	Bedrooms</COLUMNS>
  <DATA>12345	Active	450000	3</DATA>
  <DATA>12346	Active	375000	2</DATA>
</RETS>
```

**GetObject Photo Response**:
```
Content-Type: multipart/parallel; boundary="boundary-string"

--boundary-string
Content-Type: image/jpeg
Content-ID: 12345:1
Object-ID: 1
Location: http://mls.com/photos/12345_1.jpg

[JPEG Binary Data]
--boundary-string
```

### RESO Web API (Modern Standard)

#### Web API Overview

**Protocol**: RESTful HTTP
**Data Format**: JSON (OData)
**Authentication**: OAuth 2.0
**Base URL**: `https://api.mls.com/odata/`

#### OAuth 2.0 Flow

```javascript
// 1. Authorization Request
GET /oauth2/authorize?
  response_type=code&
  client_id=YOUR_CLIENT_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  scope=api

// 2. Token Request
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET&
redirect_uri=YOUR_REDIRECT_URI

// 3. Token Response
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "tGzv3..."
}

// 4. Use Access Token
GET /odata/Property
Authorization: Bearer eyJhbGc...
```

#### OData Query Operations

**Basic Query**:
```
GET /odata/Property?$filter=StandardStatus eq 'Active'
```

**Filter Operations**:
```
Equality:
  $filter=BedroomsTotal eq 3

Comparison:
  $filter=ListPrice gt 300000
  $filter=ListPrice ge 300000 and ListPrice le 500000

String Functions:
  $filter=contains(City, 'San')
  $filter=startswith(City, 'San')
  $filter=endswith(PostalCode, '78701')

Logical Operators:
  $filter=StandardStatus eq 'Active' and BedroomsTotal ge 3
  $filter=City eq 'Austin' or City eq 'Dallas'

Date Queries:
  $filter=ModificationTimestamp gt 2025-01-01T00:00:00Z
```

**Select Specific Fields**:
```
GET /odata/Property?$select=ListingKey,ListPrice,StandardStatus
```

**Expand Related Entities**:
```
GET /odata/Property?$expand=Media,Rooms
```

**Top/Skip (Pagination)**:
```
GET /odata/Property?$top=100&$skip=0
GET /odata/Property?$top=100&$skip=100
```

**OrderBy**:
```
GET /odata/Property?$orderby=ListPrice desc
GET /odata/Property?$orderby=ModificationTimestamp desc
```

**Count**:
```
GET /odata/Property/$count?$filter=StandardStatus eq 'Active'
```

#### Complete Query Example

```
GET /odata/Property?
  $filter=StandardStatus eq 'Active'
    and City eq 'Austin'
    and ListPrice ge 300000
    and ListPrice le 500000
    and BedroomsTotal ge 3&
  $select=ListingKey,ListPrice,BedroomsTotal,BathroomsTotalInteger,
          PublicRemarks,UnparsedAddress,Latitude,Longitude&
  $expand=Media($select=MediaURL,Order)&
  $orderby=ModificationTimestamp desc&
  $top=100&
  $skip=0
```

**Response**:
```json
{
  "@odata.context": "http://api.mls.com/odata/$metadata#Property",
  "value": [
    {
      "ListingKey": "12345",
      "ListPrice": 450000,
      "BedroomsTotal": 3,
      "BathroomsTotalInteger": 2,
      "PublicRemarks": "Beautiful home...",
      "UnparsedAddress": "123 Main St",
      "Latitude": 30.2672,
      "Longitude": -97.7431,
      "Media": [
        {
          "MediaURL": "http://photos.mls.com/12345_1.jpg",
          "Order": 1
        }
      ]
    }
  ]
}
```

### RESO Data Dictionary

#### Standard Resource Classes

**Property Resource**
- Residential
- Commercial
- Land
- Rental

**Member Resource**
- Agents
- Brokers
- Teams

**Office Resource**
- Brokerage offices

**OpenHouse Resource**
- Open house events

#### Key Property Fields (RESO Standard Names)

```javascript
// Identifiers
ListingKey              // Unique listing ID
ListingId               // MLS number
OriginatingSystemKey    // Source system ID

// Status
StandardStatus          // Active, Pending, Closed, Expired
StatusChangeTimestamp   // When status changed
CloseDate              // Sale close date

// Pricing
ListPrice              // Current list price
OriginalListPrice      // Initial list price
ClosePrice             // Sold price

// Physical Characteristics
BedroomsTotal          // Total bedrooms
BathroomsTotalInteger  // Total full baths
BathroomsHalf          // Half baths
LivingArea             // Square footage
LotSizeSquareFeet      // Lot size
YearBuilt              // Year constructed

// Location
UnparsedAddress        // Full address
City                   // City name
StateOrProvince        // State
PostalCode             // ZIP code
Latitude               // Latitude coordinate
Longitude              // Longitude coordinate

// Property Type
PropertyType           // Residential, Commercial, etc.
PropertySubType        // Single Family, Condo, etc.

// Dates
ListingContractDate    // Listing start date
ModificationTimestamp  // Last modified
OnMarketDate          // Date listed for sale

// Media
Media                  // Related media (expand)
MediaURL              // Photo/video URLs

// Agent/Office
ListAgentKey          // Listing agent ID
ListOfficeKey         // Listing office ID
```

#### Status Standardization

| RESO Standard | Common MLS Values | Meaning |
|---------------|-------------------|---------|
| Active | Active, A | Available for sale |
| Pending | Pending, P, Under Contract | Offer accepted |
| Closed | Closed, Sold, S | Sale completed |
| Expired | Expired, E | Listing expired |
| Withdrawn | Withdrawn, W | Removed from market |
| Canceled | Canceled, C | Listing canceled |
| Coming Soon | Coming Soon | Pre-market |
| Hold | Hold, H | Temporarily off market |

### Incremental Update Pattern

#### Timestamp-Based Sync

```javascript
// Initial full sync
GET /odata/Property?
  $filter=StandardStatus eq 'Active'&
  $orderby=ModificationTimestamp&
  $top=1000

// Store last sync timestamp
lastSync = "2025-01-15T12:00:00Z"

// Incremental updates (every 15 minutes)
GET /odata/Property?
  $filter=ModificationTimestamp gt {lastSync}&
  $orderby=ModificationTimestamp&
  $top=1000

// Process changes
- New listings (check if ListingKey exists)
- Updates (update existing records)
- Status changes (Active -> Sold)
```

#### Handling Deletes

```javascript
// Option 1: Status-based detection
// If status changes to Sold/Expired/Withdrawn, handle accordingly

// Option 2: Full sync reconciliation (weekly)
// Compare all active listings, find missing ones

// Option 3: DeletedListings endpoint (if available)
GET /odata/DeletedListings?
  $filter=DeletedTimestamp gt {lastSync}
```

### MLS Compliance Requirements

#### IDX (Internet Data Exchange) Rules

**Display Requirements**:
- MLS attribution/logo
- Listing broker name
- Data currency disclaimer
- Opt-out compliance

**Sample Attribution**:
```html
<div class="mls-attribution">
  Data provided by Austin MLS. Copyright © 2025.
  Information deemed reliable but not guaranteed.
  Last updated: January 15, 2025 12:00 PM
</div>
```

#### VOW (Virtual Office Website) Rules

**Additional Requirements**:
- Registrant authentication
- Password protection
- Usage tracking
- Stricter opt-out rules

#### Update Frequency

| Data Type | Maximum Age | Typical Sync Frequency |
|-----------|-------------|------------------------|
| Listings | 12-24 hours | 15-30 minutes |
| Photos | 24-48 hours | 1-4 hours |
| Agent data | 24 hours | Daily |
| Sold data | 48 hours | Daily |

### Rate Limiting

```javascript
// Typical MLS rate limits
const RATE_LIMITS = {
  RETS: {
    requestsPerMinute: 30,
    maxConcurrentConnections: 2,
    maxSearchRecords: 1000
  },
  WEB_API: {
    requestsPerMinute: 60,
    requestsPerHour: 5000,
    maxRecordsPerRequest: 1000
  }
};

// Implement rate limiting
const rateLimiter = new RateLimiter({
  tokensPerInterval: 60,
  interval: 'minute'
});

await rateLimiter.removeTokens(1);
const response = await mlsApi.search(query);
```

### Error Handling

#### RETS Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Process normally |
| 20201 | Invalid credentials | Check auth |
| 20202 | Session expired | Re-login |
| 20514 | Query limit exceeded | Reduce limit |
| 20400 | Query syntax error | Fix DMQL |

#### Web API Error Codes

```json
{
  "error": {
    "code": "InvalidAuthenticationToken",
    "message": "Access token has expired",
    "innerError": {
      "date": "2025-01-15T12:00:00",
      "request-id": "abc-123"
    }
  }
}
```

**Common HTTP Status Codes**:
- 400: Bad request (invalid query)
- 401: Unauthorized (token expired)
- 403: Forbidden (insufficient permissions)
- 429: Too many requests (rate limit)
- 500: Server error

### Testing & Certification

#### RESO Certification

**Web API Certification**:
1. Data Dictionary 1.7 compliance
2. OData protocol compliance
3. OAuth 2.0 implementation
4. Replication testing
5. Field validation

**Certification Levels**:
- **Bronze**: Basic compliance
- **Silver**: Enhanced features
- **Gold**: Full specification
- **Platinum**: Advanced features

#### Testing Endpoints

```javascript
// Use MLS sandbox/test endpoints
const config = {
  production: {
    baseUrl: 'https://api.mls.com/odata',
    authUrl: 'https://auth.mls.com/oauth2'
  },
  sandbox: {
    baseUrl: 'https://sandbox-api.mls.com/odata',
    authUrl: 'https://sandbox-auth.mls.com/oauth2'
  }
};
```

## See Also
- property_search_reference.md
- mls_integration_guide.md
- listing_syndication_reference.md

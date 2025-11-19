# Listing Syndication Reference

## Quick Reference for Multi-Platform Listing Distribution

### Overview

Listing syndication is the process of distributing property listings from a source (MLS, broker, agent) to multiple real estate portals and websites.

### Syndication Networks

#### Major Consumer Portals

**Zillow Group**
- Zillow.com
- Trulia.com
- StreetEasy.com (NYC)
- HotPads.com (rentals)

**Move, Inc. (News Corp)**
- Realtor.com
- Move.com

**CoStar Group**
- Apartments.com
- ForRent.com
- ApartmentFinder.com

**Other Portals**
- Redfin.com
- Homes.com
- Homesnap.com

#### Syndication Platforms

**ListHub** (Owned by Move, Inc.)
- Central syndication network
- Connects to 100+ portals
- XML/API feeds
- Analytics and tracking

**Homesnap** (Now CoStar)
- MLS data aggregation
- Agent-centric platform

**Point2** (Yardi)
- International reach
- Multi-language support

### Syndication Methods

#### 1. Direct API Integration

```javascript
// Example: Zillow Bridge API
const syndicateToZillow = async (listing) => {
  const payload = {
    partner_property_id: listing.id,
    address: {
      street: listing.address,
      city: listing.city,
      state: listing.state,
      zip: listing.zip
    },
    price: listing.price,
    bedrooms: listing.bedrooms,
    bathrooms: listing.bathrooms,
    square_feet: listing.sqft,
    description: listing.description,
    photos: listing.photos.map(p => p.url),
    status: mapStatusToZillow(listing.status)
  };

  const response = await fetch('https://api.zillow.com/bridge/Listing.htm', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${ZILLOW_API_KEY}`
    },
    body: JSON.stringify(payload)
  });

  return response.json();
};
```

#### 2. XML Feed

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Listings version="2.0">
  <Listing>
    <ListingID>12345</ListingID>
    <Status>Active</Status>
    <Price>450000</Price>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Austin</City>
      <State>TX</State>
      <Zip>78701</Zip>
    </Address>
    <Details>
      <Bedrooms>3</Bedrooms>
      <Bathrooms>2</Bathrooms>
      <SquareFeet>2000</SquareFeet>
      <YearBuilt>2010</YearBuilt>
      <PropertyType>Single Family</PropertyType>
    </Details>
    <Description><![CDATA[
      Beautiful home in downtown Austin...
    ]]></Description>
    <Photos>
      <Photo>
        <URL>https://cdn.example.com/photos/12345_1.jpg</URL>
        <Order>1</Order>
        <Caption>Front view</Caption>
      </Photo>
    </Photos>
    <Agent>
      <Name>John Smith</Name>
      <Email>john@realty.com</Email>
      <Phone>512-555-0100</Phone>
    </Agent>
    <Office>
      <Name>Smith Realty</Name>
      <Phone>512-555-0101</Phone>
    </Office>
    <LastModified>2025-01-15T12:00:00Z</LastModified>
  </Listing>
</Listings>
```

#### 3. RETS/IDX Feed

```javascript
// Provide RETS endpoint for portals
// Portals pull data on their schedule
const retsEndpoint = {
  loginUrl: 'https://your-site.com/rets/login',
  searchUrl: 'https://your-site.com/rets/search',
  credentials: {
    username: 'portal_user',
    password: 'secure_password'
  }
};
```

### Syndication Data Mapping

#### Status Mapping

```javascript
const STATUS_MAPPING = {
  // Your system -> Portal systems
  active: {
    zillow: 'for_sale',
    realtor: 'Active',
    trulia: 'for_sale',
    redfin: 'Active'
  },
  pending: {
    zillow: 'pending',
    realtor: 'Pending',
    trulia: 'pending',
    redfin: 'Pending'
  },
  sold: {
    zillow: 'off_market',
    realtor: 'Sold',
    trulia: 'off_market',
    redfin: 'Sold'
  },
  withdrawn: {
    zillow: 'off_market',
    realtor: 'Withdrawn',
    trulia: 'off_market',
    redfin: 'Withdrawn'
  }
};
```

#### Property Type Mapping

```javascript
const PROPERTY_TYPE_MAPPING = {
  single_family: {
    zillow: 'SingleFamily',
    realtor: 'RES',
    trulia: 'SINGLE_FAMILY'
  },
  condo: {
    zillow: 'Condo',
    realtor: 'CND',
    trulia: 'CONDO'
  },
  townhouse: {
    zillow: 'Townhouse',
    realtor: 'TWN',
    trulia: 'TOWNHOUSE'
  },
  multi_family: {
    zillow: 'MultiFamily',
    realtor: 'MUL',
    trulia: 'MULTI_FAMILY'
  }
};
```

### Syndication Workflow

```javascript
class ListingSyndicator {
  constructor() {
    this.portals = ['zillow', 'trulia', 'realtor', 'redfin'];
  }

  async syndicateListing(listing) {
    const results = {
      success: [],
      failed: [],
      skipped: []
    };

    // Check syndication eligibility
    if (!this.isEligibleForSyndication(listing)) {
      results.skipped.push('Not eligible for syndication');
      return results;
    }

    // Syndicate to each portal
    for (const portal of this.portals) {
      try {
        // Check if agent opted in for this portal
        if (!listing.agent.syndication_preferences[portal]) {
          results.skipped.push(portal);
          continue;
        }

        // Transform listing data for portal
        const portalListing = this.transformForPortal(listing, portal);

        // Send to portal
        await this.sendToPortal(portal, portalListing);

        // Log success
        await this.logSyndication(listing.id, portal, 'success');
        results.success.push(portal);

      } catch (error) {
        console.error(`Failed to syndicate to ${portal}:`, error);
        await this.logSyndication(listing.id, portal, 'failed', error.message);
        results.failed.push({ portal, error: error.message });
      }
    }

    return results;
  }

  isEligibleForSyndication(listing) {
    return (
      listing.status === 'active' &&
      listing.price > 0 &&
      listing.photos.length >= 1 &&
      listing.description.length >= 100 &&
      !listing.is_private_listing
    );
  }

  transformForPortal(listing, portal) {
    const transformer = this.getTransformer(portal);
    return transformer.transform(listing);
  }

  async sendToPortal(portal, listing) {
    const client = this.getPortalClient(portal);
    return await client.createOrUpdateListing(listing);
  }

  async logSyndication(listingId, portal, status, errorMessage = null) {
    await db.syndication_log.create({
      listing_id: listingId,
      portal,
      status,
      error_message: errorMessage,
      timestamp: new Date()
    });
  }
}
```

### Quality Requirements by Portal

#### Zillow/Trulia

**Minimum Requirements**:
- ✅ Valid address (verified by geocoding)
- ✅ At least 1 photo (recommend 10+)
- ✅ Description 100+ characters
- ✅ Accurate price
- ✅ Bedrooms, bathrooms, sqft

**Recommended**:
- 🌟 10+ high-quality photos
- 🌟 Virtual tour link
- 🌟 Open house schedule
- 🌟 School information

#### Realtor.com

**Minimum Requirements**:
- ✅ MLS number
- ✅ Listing agent license #
- ✅ Office information
- ✅ At least 1 photo
- ✅ Complete address

**Premium Features**:
- 🌟 Video walkthrough
- 🌟 3D tour
- 🌟 Agent headshot

### Photo Optimization for Syndication

```javascript
const optimizePhotosForSyndication = async (photos) => {
  return await Promise.all(photos.map(async (photo, index) => {
    // Resize and optimize
    const optimized = await sharp(photo.buffer)
      .resize(2048, 1536, { // Max size for most portals
        fit: 'inside',
        withoutEnlargement: true
      })
      .jpeg({ quality: 85 })
      .toBuffer();

    // Generate CDN URLs
    const url = await uploadToCDN(optimized, `${listingId}_${index + 1}.jpg`);

    return {
      url,
      order: index + 1,
      caption: photo.caption || '',
      width: 2048,
      height: 1536
    };
  }));
};
```

### Syndication Analytics

```javascript
// Track syndication performance
const syndicationMetrics = {
  listing_id: '12345',
  portals: {
    zillow: {
      status: 'active',
      syndicated_at: '2025-01-15T10:00:00Z',
      last_updated: '2025-01-15T12:00:00Z',
      views: 247,
      saves: 15,
      contacts: 8,
      portal_url: 'https://zillow.com/homedetails/...'
    },
    trulia: {
      status: 'active',
      syndicated_at: '2025-01-15T10:05:00Z',
      views: 189,
      contacts: 5
    },
    realtor: {
      status: 'active',
      syndicated_at: '2025-01-15T10:10:00Z',
      views: 312,
      contacts: 12
    }
  },
  total_views: 748,
  total_contacts: 25
};
```

### Update Frequency

```javascript
const SYNDICATION_SCHEDULE = {
  // New listings
  new_listing: 'immediate', // Within 15 minutes

  // Price changes
  price_change: 'immediate',

  // Status changes
  status_change: 'immediate',

  // Photo updates
  photos_updated: 'hourly',

  // Description edits
  description_updated: 'hourly',

  // Minor field updates
  other_updates: 'every_4_hours'
};
```

### Opt-Out Handling

```javascript
// Respect agent/broker opt-out preferences
const syndicationPreferences = {
  agent_id: '789',
  opt_out: {
    zillow: false,      // Syndicate to Zillow
    trulia: true,       // Opt-out from Trulia
    realtor: false,
    redfin: false
  },
  opt_out_reason: {
    trulia: 'Prefers direct leads only'
  },
  updated_at: '2025-01-15T00:00:00Z'
};

// Check before syndicating
if (listing.agent.opt_out[portal]) {
  console.log(`Skipping ${portal} - agent opted out`);
  return;
}
```

### ListHub Integration

```javascript
// ListHub XML Feed Format
const generateListHubFeed = (listings) => {
  return `<?xml version="1.0" encoding="UTF-8"?>
<ListHub>
  <ListingFeed>
    <VendorID>YOUR_VENDOR_ID</VendorID>
    <Listings>
      ${listings.map(listing => `
      <Listing>
        <ListingID>${listing.id}</ListingID>
        <ProviderListingID>${listing.mls_number}</ProviderListingID>
        <ListingURL>https://yoursite.com/property/${listing.id}</ListingURL>
        <Price>${listing.price}</Price>
        <StreetAddress>${listing.address}</StreetAddress>
        <City>${listing.city}</City>
        <StateOrProvince>${listing.state}</StateOrProvince>
        <PostalCode>${listing.zip}</PostalCode>
        <Bedrooms>${listing.bedrooms}</Bedrooms>
        <Bathrooms>${listing.bathrooms}</Bathrooms>
        <LivingArea>${listing.sqft}</LivingArea>
        <PropertyType>${listing.property_type}</PropertyType>
        <Status>${listing.status}</Status>
        <ListingDescription>${escapeXML(listing.description)}</ListingDescription>
        <Images>
          ${listing.photos.map((photo, i) => `
          <Image sequence="${i + 1}">
            <URL>${photo.url}</URL>
            <Caption>${escapeXML(photo.caption)}</Caption>
          </Image>
          `).join('')}
        </Images>
        <Agent>
          <Name>${listing.agent.name}</Name>
          <Email>${listing.agent.email}</Email>
          <Phone>${listing.agent.phone}</Phone>
        </Agent>
      </Listing>
      `).join('')}
    </Listings>
  </ListingFeed>
</ListHub>`;
};

// Host feed at URL for ListHub to poll
app.get('/feeds/listhub.xml', async (req, res) => {
  const listings = await getActiveListings();
  const feed = generateListHubFeed(listings);
  res.type('application/xml');
  res.send(feed);
});
```

### Error Handling

```javascript
const handleSyndicationError = async (error, listing, portal) => {
  const errorHandlers = {
    'INVALID_ADDRESS': async () => {
      // Attempt geocoding correction
      const correctedAddress = await geocodeAddress(listing.address);
      if (correctedAddress) {
        listing.latitude = correctedAddress.lat;
        listing.longitude = correctedAddress.lng;
        return 'retry';
      }
      return 'skip';
    },

    'MISSING_PHOTOS': async () => {
      // Notify agent to add photos
      await notifyAgent(listing.agent_id, 'Please add photos for syndication');
      return 'skip';
    },

    'DUPLICATE_LISTING': async () => {
      // Update existing listing instead
      return 'update';
    },

    'RATE_LIMIT': async () => {
      // Retry after delay
      await delay(60000); // 1 minute
      return 'retry';
    }
  };

  const handler = errorHandlers[error.code];
  return handler ? await handler() : 'skip';
};
```

### Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Syndication delay | < 15min | New listing to portal |
| Update propagation | < 1 hour | Changes to portals |
| Success rate | > 95% | Successful syndications |
| Portal coverage | 4+ portals | Major portals |
| Photo optimization | < 5s per photo | Processing time |

### Compliance & Best Practices

**Fair Housing**
- No discriminatory language in descriptions
- Equal opportunity statements
- Compliant photo selection

**Data Accuracy**
- Verify all information before syndication
- Keep portals updated with changes
- Remove listings promptly when sold

**Attribution**
- Proper broker/agent attribution
- MLS compliance on all portals
- Logo/branding requirements

**Privacy**
- Respect opt-out preferences
- Secure credential management
- No unauthorized data sharing

## See Also
- mls_reso_standards.md
- seo_reference.md
- property_search_reference.md

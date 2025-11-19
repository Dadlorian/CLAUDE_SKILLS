# Property Listing Workflow Guide

## Complete workflow from MLS to marketplace display

### Workflow Overview

```
MLS → Ingest → Transform → Enrich → Index → Display → Syndicate
  ↓       ↓         ↓         ↓        ↓       ↓         ↓
RETS   Validate  Normalize  Photos  Elastic  Web     Portals
```

### Step 1: MLS Data Ingestion

**Frequency**: Every 15 minutes

```javascript
// cron job: */15 * * * *
const syncMLSListings = async () => {
  try {
    // Get last sync timestamp
    const lastSync = await getLastSyncTime();

    // Connect to MLS
    const mls = new MLSClient({
      url: process.env.MLS_URL,
      username: process.env.MLS_USER,
      password: process.env.MLS_PASS
    });

    await mls.login();

    // Incremental query
    const listings = await mls.search({
      query: `(ModificationTimestamp=${lastSync}+)`,
      limit: 1000
    });

    console.log(`Found ${listings.length} updated listings`);

    // Process each listing
    for (const listing of listings) {
      await processListing(listing);
    }

    // Update sync timestamp
    await updateLastSyncTime(new Date());

    await mls.logout();

  } catch (error) {
    console.error('MLS sync failed:', error);
    await notifyError(error);
  }
};
```

### Step 2: Data Validation

```javascript
const validateListing = (listing) => {
  const errors = [];

  // Required fields
  const required = ['ListingKey', 'ListPrice', 'UnparsedAddress', 'City', 'StateOrProvince'];
  required.forEach(field => {
    if (!listing[field]) {
      errors.push(`Missing required field: ${field}`);
    }
  });

  // Numeric validations
  if (listing.ListPrice <= 0) {
    errors.push('Invalid price');
  }

  if (listing.BedroomsTotal < 0 || listing.BedroomsTotal > 50) {
    errors.push('Invalid bedroom count');
  }

  if (listing.LivingArea && listing.LivingArea < 100) {
    errors.push('Suspiciously small square footage');
  }

  // Coordinate validation
  if (listing.Latitude && (listing.Latitude < -90 || listing.Latitude > 90)) {
    errors.push('Invalid latitude');
  }

  // Status validation
  const validStatuses = ['Active', 'Pending', 'Closed', 'Expired', 'Withdrawn'];
  if (!validStatuses.includes(listing.StandardStatus)) {
    errors.push('Invalid status');
  }

  return {
    valid: errors.length === 0,
    errors
  };
};
```

### Step 3: Data Transformation

```javascript
const transformListing = (mlsListing) => {
  return {
    // Identifiers
    property_id: generatePropertyId(mlsListing.ListingKey),
    mls_number: mlsListing.ListingKey,
    mls_name: 'Austin MLS',

    // Status
    status: mapStatus(mlsListing.StandardStatus),
    listing_date: mlsListing.ListingContractDate,
    updated_at: mlsListing.ModificationTimestamp,

    // Location
    address: mlsListing.UnparsedAddress,
    city: mlsListing.City,
    state: mlsListing.StateOrProvince,
    zip: mlsListing.PostalCode,
    county: mlsListing.CountyOrParish,
    latitude: mlsListing.Latitude,
    longitude: mlsListing.Longitude,

    // Property details
    price: mlsListing.ListPrice,
    original_price: mlsListing.OriginalListPrice,
    bedrooms: mlsListing.BedroomsTotal,
    bathrooms: mlsListing.BathroomsTotalInteger + (mlsListing.BathroomsHalf * 0.5),
    sqft: mlsListing.LivingArea,
    lot_size: mlsListing.LotSizeSquareFeet,
    year_built: mlsListing.YearBuilt,
    property_type: mapPropertyType(mlsListing.PropertyType),
    property_subtype: mlsListing.PropertySubType,

    // Features
    features: extractFeatures(mlsListing),
    description: cleanDescription(mlsListing.PublicRemarks),

    // Agent/Office
    agent_id: mlsListing.ListAgentKey,
    agent_name: mlsListing.ListAgentFullName,
    office_id: mlsListing.ListOfficeKey,
    office_name: mlsListing.ListOfficeName,

    // Photos (will be enriched)
    photos: [],

    // Metadata
    source: 'mls',
    source_id: mlsListing.ListingKey,
    imported_at: new Date()
  };
};

const mapStatus = (mlsStatus) => {
  const statusMap = {
    'Active': 'active',
    'Pending': 'pending',
    'Closed': 'sold',
    'Expired': 'expired',
    'Withdrawn': 'withdrawn',
    'Coming Soon': 'coming_soon'
  };
  return statusMap[mlsStatus] || 'unknown';
};
```

### Step 4: Photo Enrichment

```javascript
const enrichWithPhotos = async (listing, mlsListing) => {
  try {
    // Download photos from MLS
    const photos = await mls.getPhotos(mlsListing.ListingKey);

    // Process each photo
    const processedPhotos = await Promise.all(
      photos.map(async (photo, index) => {
        // Upload to CDN
        const cdnUrl = await uploadToCDN(photo.data, {
          key: `properties/${listing.property_id}/${index}.jpg`,
          contentType: 'image/jpeg'
        });

        // Generate optimized versions
        await generateImageSizes(cdnUrl, [
          { name: 'thumbnail', width: 200, height: 150 },
          { name: 'medium', width: 800, height: 600 },
          { name: 'large', width: 1920, height: 1440 }
        ]);

        return {
          url: cdnUrl,
          order: index + 1,
          caption: photo.caption || '',
          width: photo.width,
          height: photo.height
        };
      })
    );

    listing.photos = processedPhotos;
    listing.photo_count = processedPhotos.length;

    if (processedPhotos.length > 0) {
      listing.main_photo = processedPhotos[0].url;
    }

  } catch (error) {
    console.error('Photo enrichment failed:', error);
    listing.photos = [];
  }

  return listing;
};
```

### Step 5: Geocoding Enhancement

```javascript
const enhanceGeocoding = async (listing) => {
  // If coordinates missing, geocode address
  if (!listing.latitude || !listing.longitude) {
    const coords = await geocodeAddress(
      `${listing.address}, ${listing.city}, ${listing.state} ${listing.zip}`
    );

    if (coords) {
      listing.latitude = coords.lat;
      listing.longitude = coords.lng;
    }
  }

  // Get additional location data
  if (listing.latitude && listing.longitude) {
    // Reverse geocode for neighborhood
    const place = await reverseGeocode(listing.latitude, listing.longitude);
    listing.neighborhood = place.neighborhood;

    // Get walkability scores
    const scores = await getWalkScores(listing.latitude, listing.longitude);
    listing.walk_score = scores.walk;
    listing.transit_score = scores.transit;

    // Get school information
    const schools = await getNearbySchools(listing.latitude, listing.longitude);
    listing.schools = schools;

    // Get POIs
    const pois = await getNearbyPOIs(listing.latitude, listing.longitude);
    listing.nearby_places = pois;
  }

  return listing;
};
```

### Step 6: Elasticsearch Indexing

```javascript
const indexListing = async (listing) => {
  try {
    const esDocument = {
      property_id: listing.property_id,
      mls_number: listing.mls_number,
      status: listing.status,

      // Location (geo_point)
      location: {
        lat: listing.latitude,
        lon: listing.longitude
      },

      // Address fields
      address: listing.address,
      city: listing.city,
      state: listing.state,
      zip: listing.zip,

      // Property details
      price: listing.price,
      bedrooms: listing.bedrooms,
      bathrooms: listing.bathrooms,
      sqft: listing.sqft,
      lot_size: listing.lot_size,
      year_built: listing.year_built,
      property_type: listing.property_type,

      // Searchable text
      description: listing.description,
      features: listing.features,

      // Photos
      photos: listing.photos,
      photo_count: listing.photo_count,

      // Dates
      listing_date: listing.listing_date,
      updated_at: listing.updated_at,

      // Agent
      agent: {
        id: listing.agent_id,
        name: listing.agent_name
      }
    };

    // Index in Elasticsearch
    await elasticsearch.index({
      index: 'properties',
      id: listing.property_id,
      body: esDocument
    });

    console.log(`Indexed property ${listing.property_id}`);

  } catch (error) {
    console.error('Indexing failed:', error);
    throw error;
  }
};
```

### Step 7: Database Storage

```javascript
const saveListing = async (listing) => {
  try {
    // Upsert property
    await db.properties.upsert({
      property_id: listing.property_id,
      mls_number: listing.mls_number,
      ...listing
    });

    // Save photos separately
    if (listing.photos.length > 0) {
      await db.property_photos.bulkCreate(
        listing.photos.map(photo => ({
          property_id: listing.property_id,
          url: photo.url,
          order: photo.order,
          caption: photo.caption
        })),
        { updateOnDuplicate: ['url', 'caption'] }
      );
    }

    // Track history
    await db.property_history.create({
      property_id: listing.property_id,
      event: 'updated',
      data: listing,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('Database save failed:', error);
    throw error;
  }
};
```

### Step 8: Syndication

```javascript
const syndicateListing = async (listing) => {
  // Only syndicate active listings
  if (listing.status !== 'active') {
    return;
  }

  // Check if listing qualifies for syndication
  if (!qualifiesForSyndication(listing)) {
    console.log(`Listing ${listing.property_id} does not qualify for syndication`);
    return;
  }

  // Syndicate to configured portals
  const portals = ['zillow', 'trulia', 'realtor'];

  for (const portal of portals) {
    try {
      await syndicateToPortal(listing, portal);
      console.log(`Syndicated to ${portal}`);
    } catch (error) {
      console.error(`Syndication to ${portal} failed:`, error);
    }
  }
};

const qualifiesForSyndication = (listing) => {
  return (
    listing.price > 0 &&
    listing.photos.length >= 1 &&
    listing.description.length >= 100 &&
    listing.latitude &&
    listing.longitude
  );
};
```

### Complete Workflow Function

```javascript
const processListing = async (mlsListing) => {
  try {
    console.log(`Processing listing ${mlsListing.ListingKey}`);

    // 1. Validate
    const validation = validateListing(mlsListing);
    if (!validation.valid) {
      console.error('Validation failed:', validation.errors);
      return;
    }

    // 2. Transform
    let listing = transformListing(mlsListing);

    // 3. Enrich with photos
    listing = await enrichWithPhotos(listing, mlsListing);

    // 4. Enhance geocoding
    listing = await enhanceGeocoding(listing);

    // 5. Save to database
    await saveListing(listing);

    // 6. Index in Elasticsearch
    await indexListing(listing);

    // 7. Syndicate to portals
    await syndicateListing(listing);

    console.log(`Successfully processed listing ${listing.property_id}`);

  } catch (error) {
    console.error(`Failed to process listing:`, error);

    // Log error for review
    await db.listing_errors.create({
      mls_number: mlsListing.ListingKey,
      error: error.message,
      stack: error.stack,
      data: mlsListing,
      timestamp: new Date()
    });
  }
};
```

### Monitoring & Alerts

```javascript
const monitorWorkflow = async () => {
  // Check sync health
  const lastSync = await getLastSyncTime();
  const minutesSinceSync = (Date.now() - lastSync) / 60000;

  if (minutesSinceSync > 30) {
    await sendAlert({
      type: 'sync_delayed',
      message: `MLS sync has not run for ${minutesSinceSync} minutes`
    });
  }

  // Check error rate
  const errors = await db.listing_errors.count({
    where: {
      timestamp: { [Op.gte]: new Date(Date.now() - 3600000) } // Last hour
    }
  });

  if (errors > 50) {
    await sendAlert({
      type: 'high_error_rate',
      message: `${errors} listing errors in the last hour`
    });
  }

  // Check index health
  const esStats = await elasticsearch.indices.stats({ index: 'properties' });
  const docCount = esStats.indices.properties.total.docs.count;

  const dbCount = await db.properties.count({ where: { status: 'active' } });

  if (Math.abs(docCount - dbCount) > 100) {
    await sendAlert({
      type: 'index_drift',
      message: `ES count (${docCount}) differs from DB count (${dbCount})`
    });
  }
};
```

## Best Practices

1. **Incremental Syncs**: Always use timestamp-based incremental updates
2. **Error Handling**: Log all errors, don't fail entire batch
3. **Idempotency**: Make processing idempotent (safe to re-run)
4. **Rate Limiting**: Respect MLS API rate limits
5. **Monitoring**: Alert on sync delays and error spikes
6. **Photo Optimization**: Always optimize images before display
7. **Data Quality**: Validate before indexing
8. **Fallback**: Have geocoding fallbacks if MLS data incomplete

## See Also
- mls_integration_guide.md
- elasticsearch_setup.md
- listing_syndication_reference.md

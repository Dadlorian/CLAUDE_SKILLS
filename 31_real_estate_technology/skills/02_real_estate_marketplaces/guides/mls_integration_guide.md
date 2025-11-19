# MLS Integration Guide

## Connecting to MLS via RETS and Web API

### RETS Integration

```javascript
// Install: npm install node-rets
const RETS = require('node-rets');

class RETSClient {
  constructor(config) {
    this.client = new RETS({
      loginUrl: config.url,
      username: config.username,
      password: config.password,
      version: 'RETS/1.7.2',
      userAgent: 'YourApp/1.0'
    });
  }

  async connect() {
    return await this.client.login();
  }

  async getMetadata() {
    return await this.client.metadata.getAllMetadata();
  }

  async search(options) {
    const results = await this.client.search({
      searchType: 'Property',
      class: 'RES',
      query: options.query || '(Status=Active)',
      limit: options.limit || 1000,
      offset: options.offset || 0
    });

    return results.results;
  }

  async getPhotos(listingKey) {
    const photos = await this.client.objects.getAllObjects({
      resource: 'Property',
      type: 'Photo',
      id: listingKey
    });

    return photos.objects.map((photo, index) => ({
      data: photo.data,
      contentType: photo.headers['content-type'],
      order: index + 1
    }));
  }

  async disconnect() {
    return await this.client.logout();
  }
}

// Usage
const mls = new RETSClient({
  url: 'https://mls.example.com/rets/login',
  username: process.env.MLS_USER,
  password: process.env.MLS_PASS
});

await mls.connect();
const listings = await mls.search({ query: '(Status=Active)' });
await mls.disconnect();
```

### Web API Integration (RESO)

```javascript
// OAuth 2.0 + OData
const axios = require('axios');

class RESOWebAPIClient {
  constructor(config) {
    this.config = config;
    this.accessToken = null;
    this.tokenExpiry = null;
  }

  async authenticate() {
    const response = await axios.post(this.config.tokenUrl, {
      grant_type: 'client_credentials',
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
      scope: 'api'
    });

    this.accessToken = response.data.access_token;
    this.tokenExpiry = Date.now() + (response.data.expires_in * 1000);
  }

  async ensureAuthenticated() {
    if (!this.accessToken || Date.now() >= this.tokenExpiry) {
      await this.authenticate();
    }
  }

  async getProperties(filter = null, options = {}) {
    await this.ensureAuthenticated();

    const params = {
      $filter: filter || "StandardStatus eq 'Active'",
      $select: options.select || 'ListingKey,ListPrice,BedroomsTotal,BathroomsTotalInteger',
      $top: options.top || 100,
      $skip: options.skip || 0,
      $orderby: options.orderby || 'ModificationTimestamp desc'
    };

    if (options.expand) {
      params.$expand = options.expand;
    }

    const response = await axios.get(`${this.config.baseUrl}/Property`, {
      params,
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Accept': 'application/json'
      }
    });

    return response.data.value;
  }

  async getIncrementalUpdates(since) {
    const filter = `ModificationTimestamp gt ${since.toISOString()}`;
    return await this.getProperties(filter, { top: 1000 });
  }

  async getMedia(listingKey) {
    await this.ensureAuthenticated();

    const response = await axios.get(`${this.config.baseUrl}/Media`, {
      params: {
        $filter: `ResourceRecordKey eq '${listingKey}'`,
        $orderby: 'Order'
      },
      headers: {
        'Authorization': `Bearer ${this.accessToken}`
      }
    });

    return response.data.value;
  }
}

// Usage
const webApi = new RESOWebAPIClient({
  baseUrl: 'https://api.mls.com/odata',
  tokenUrl: 'https://auth.mls.com/oauth2/token',
  clientId: process.env.MLS_CLIENT_ID,
  clientSecret: process.env.MLS_CLIENT_SECRET
});

const listings = await webApi.getProperties(
  "City eq 'Austin' and ListPrice gt 300000",
  { expand: 'Media', top: 100 }
);
```

### Incremental Sync Pattern

```javascript
class MLSSync {
  async performSync() {
    const lastSync = await this.getLastSyncTime();
    console.log(`Syncing changes since ${lastSync}`);

    let skip = 0;
    const pageSize = 1000;
    let hasMore = true;

    while (hasMore) {
      const filter = `ModificationTimestamp gt ${lastSync.toISOString()}`;
      const listings = await webApi.getProperties(filter, {
        top: pageSize,
        skip: skip
      });

      if (listings.length === 0) {
        hasMore = false;
        break;
      }

      // Process batch
      await this.processBatch(listings);

      skip += pageSize;
      console.log(`Processed ${skip} listings`);

      // Rate limiting
      await this.delay(1000);
    }

    await this.updateLastSyncTime(new Date());
    console.log('Sync complete');
  }

  async processBatch(listings) {
    for (const listing of listings) {
      try {
        await this.processListing(listing);
      } catch (error) {
        console.error(`Error processing ${listing.ListingKey}:`, error);
      }
    }
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## See Also
- mls_reso_standards.md
- property_listing_workflow.md

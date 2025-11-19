# Elasticsearch Setup Guide for Real Estate

## Installation & Configuration

### Docker Setup (Recommended)

```yaml
# docker-compose.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: es-properties
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es-data:/usr/share/elasticsearch/data
    networks:
      - elastic

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    networks:
      - elastic
    depends_on:
      - elasticsearch

volumes:
  es-data:
    driver: local

networks:
  elastic:
    driver: bridge
```

```bash
# Start services
docker-compose up -d

# Verify Elasticsearch is running
curl -X GET "localhost:9200/_cluster/health?pretty"
```

### Index Creation

```javascript
// Create properties index with proper mappings
const createPropertiesIndex = async () => {
  const indexConfig = {
    settings: {
      number_of_shards: 3,
      number_of_replicas: 1,
      analysis: {
        analyzer: {
          address_analyzer: {
            tokenizer: 'standard',
            filter: ['lowercase', 'asciifolding']
          }
        }
      },
      max_result_window: 10000
    },
    mappings: {
      properties: {
        property_id: { type: 'keyword' },
        mls_number: { type: 'keyword' },
        status: { type: 'keyword' },

        // Text fields
        address: {
          type: 'text',
          analyzer: 'address_analyzer',
          fields: {
            keyword: { type: 'keyword' }
          }
        },
        city: { type: 'keyword' },
        state: { type: 'keyword' },
        zip: { type: 'keyword' },
        neighborhood: { type: 'keyword' },
        description: { type: 'text' },

        // Geo location
        location: { type: 'geo_point' },

        // Numeric fields
        price: { type: 'integer' },
        bedrooms: { type: 'integer' },
        bathrooms: { type: 'float' },
        sqft: { type: 'integer' },
        lot_size: { type: 'integer' },
        year_built: { type: 'integer' },

        // Property type
        property_type: { type: 'keyword' },
        property_subtype: { type: 'keyword' },

        // Features
        features: { type: 'keyword' },
        has_pool: { type: 'boolean' },
        has_ac: { type: 'boolean' },
        garage_spaces: { type: 'integer' },

        // Photos
        photos: {
          type: 'nested',
          properties: {
            url: { type: 'keyword' },
            order: { type: 'integer' }
          }
        },
        photo_count: { type: 'integer' },

        // Agent/Office
        agent: {
          properties: {
            id: { type: 'keyword' },
            name: { type: 'text' }
          }
        },

        // Dates
        listing_date: { type: 'date' },
        updated_at: { type: 'date' },

        // Schools
        schools: {
          type: 'nested',
          properties: {
            name: { type: 'text' },
            rating: { type: 'integer' },
            distance: { type: 'float' }
          }
        },

        // Scores
        walk_score: { type: 'integer' },
        transit_score: { type: 'integer' }
      }
    }
  };

  await elasticsearch.indices.create({
    index: 'properties',
    body: indexConfig
  });

  console.log('Properties index created successfully');
};
```

### Bulk Indexing

```javascript
const bulkIndexListings = async (listings) => {
  const body = listings.flatMap(listing => [
    { index: { _index: 'properties', _id: listing.property_id } },
    {
      property_id: listing.property_id,
      mls_number: listing.mls_number,
      status: listing.status,
      address: listing.address,
      city: listing.city,
      state: listing.state,
      zip: listing.zip,
      location: {
        lat: listing.latitude,
        lon: listing.longitude
      },
      price: listing.price,
      bedrooms: listing.bedrooms,
      bathrooms: listing.bathrooms,
      sqft: listing.sqft,
      description: listing.description,
      listing_date: listing.listing_date,
      updated_at: new Date()
    }
  ]);

  const response = await elasticsearch.bulk({ body });

  if (response.errors) {
    const erroredDocuments = response.items.filter(item => item.index?.error);
    console.error('Bulk indexing errors:', erroredDocuments);
  }

  console.log(`Indexed ${listings.length} properties`);
  return response;
};
```

### Index Aliases for Zero-Downtime Updates

```javascript
// Blue-green deployment pattern
const reindexWithZeroDowntime = async () => {
  const timestamp = Date.now();
  const newIndex = `properties_${timestamp}`;

  // 1. Create new index
  await elasticsearch.indices.create({
    index: newIndex,
    body: indexConfig
  });

  // 2. Bulk index all data
  const listings = await db.properties.findAll();
  await bulkIndexListings(listings, newIndex);

  // 3. Point alias to new index
  await elasticsearch.indices.updateAliases({
    body: {
      actions: [
        { remove: { index: 'properties_*', alias: 'properties' } },
        { add: { index: newIndex, alias: 'properties' } }
      ]
    }
  });

  // 4. Delete old indices (keep last 2)
  const indices = await elasticsearch.cat.indices({ format: 'json' });
  const propertyIndices = indices
    .filter(i => i.index.startsWith('properties_'))
    .sort((a, b) => b.index.localeCompare(a.index))
    .slice(2);

  for (const index of propertyIndices) {
    await elasticsearch.indices.delete({ index: index.index });
  }
};
```

### Query Examples

```javascript
// Basic search
const searchProperties = async (query) => {
  const response = await elasticsearch.search({
    index: 'properties',
    body: {
      query: {
        bool: {
          must: [
            { term: { status: 'active' } }
          ],
          filter: [
            { range: { price: { gte: 300000, lte: 500000 } } },
            { range: { bedrooms: { gte: 3 } } },
            { term: { city: 'Austin' } }
          ]
        }
      },
      sort: [{ listing_date: 'desc' }],
      from: 0,
      size: 20
    }
  });

  return response.hits.hits.map(hit => hit._source);
};

// Geo search
const searchByLocation = async (lat, lon, radiusMiles) => {
  const response = await elasticsearch.search({
    index: 'properties',
    body: {
      query: {
        bool: {
          must: [{ term: { status: 'active' } }],
          filter: [
            {
              geo_distance: {
                distance: `${radiusMiles}mi`,
                location: { lat, lon }
              }
            }
          ]
        }
      }
    }
  });

  return response.hits.hits.map(hit => hit._source);
};
```

### Performance Optimization

```javascript
// 1. Use filters instead of queries for caching
const optimizedQuery = {
  query: {
    bool: {
      filter: [  // Cached
        { term: { status: 'active' } },
        { range: { price: { gte: 300000 } } }
      ],
      must: [  // Scored
        { match: { description: 'luxury' } }
      ]
    }
  }
};

// 2. Limit fields returned
const response = await elasticsearch.search({
  index: 'properties',
  _source: ['property_id', 'address', 'price', 'bedrooms'],
  body: query
});

// 3. Use scroll for large result sets
const scrollSearch = async () => {
  let allHits = [];

  const response = await elasticsearch.search({
    index: 'properties',
    scroll: '1m',
    size: 1000,
    body: { query: { match_all: {} } }
  });

  let scrollId = response._scroll_id;
  allHits = allHits.concat(response.hits.hits);

  while (response.hits.hits.length) {
    const scrollResponse = await elasticsearch.scroll({
      scroll_id: scrollId,
      scroll: '1m'
    });

    scrollId = scrollResponse._scroll_id;
    allHits = allHits.concat(scrollResponse.hits.hits);

    if (scrollResponse.hits.hits.length === 0) break;
  }

  await elasticsearch.clearScroll({ scroll_id: scrollId });
  return allHits;
};
```

### Monitoring

```javascript
const monitorES = async () => {
  // Cluster health
  const health = await elasticsearch.cluster.health();
  console.log('Cluster status:', health.status);

  // Index stats
  const stats = await elasticsearch.indices.stats({ index: 'properties' });
  console.log('Document count:', stats.indices.properties.total.docs.count);
  console.log('Index size:', stats.indices.properties.total.store.size);

  // Node stats
  const nodes = await elasticsearch.nodes.stats();
  Object.values(nodes.nodes).forEach(node => {
    console.log(`Node ${node.name}:`);
    console.log('  JVM heap used:', node.jvm.mem.heap_used_percent + '%');
    console.log('  CPU usage:', node.os.cpu.percent + '%');
  });
};
```

## Best Practices

1. **Use Aliases**: Always query via alias for zero-downtime reindexing
2. **Proper Mapping**: Define explicit mappings, don't rely on dynamic
3. **Filters vs Queries**: Use filters for exact matches (faster, cached)
4. **Pagination**: Use `search_after` for deep pagination, not `from/size`
5. **Monitoring**: Monitor cluster health, query performance, JVM heap
6. **Sharding**: Size shards to 20-50GB each
7. **Replicas**: Use at least 1 replica for high availability

## See Also
- property_search_reference.md
- property_listing_workflow.md

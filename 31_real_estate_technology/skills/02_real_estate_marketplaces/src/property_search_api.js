/**
 * Property Search API
 * RESTful API for searching real estate listings
 */

const express = require('express');
const { Client } = require('@elastic/elasticsearch');
const router = express.Router();

// Elasticsearch client
const es = new Client({
  node: process.env.ELASTICSEARCH_URL || 'http://localhost:9200'
});

/**
 * POST /api/search/properties
 * Search properties with filters
 *
 * Body:
 * {
 *   query: "downtown condo",
 *   location: { lat: 30.27, lon: -97.74, radius: 10 },
 *   filters: {
 *     price: { min: 300000, max: 500000 },
 *     bedrooms: { min: 2 },
 *     bathrooms: { min: 2 },
 *     property_type: ["condo", "townhouse"]
 *   },
 *   sort: "price_asc",
 *   page: 1,
 *   pageSize: 20
 * }
 */
router.post('/properties', async (req, res) => {
  try {
    const {
      query,
      location,
      filters = {},
      sort = 'relevance',
      page = 1,
      pageSize = 20
    } = req.body;

    // Build Elasticsearch query
    const esQuery = buildQuery(query, location, filters);

    // Execute search
    const response = await es.search({
      index: 'properties',
      body: {
        query: esQuery,
        sort: getSortCriteria(sort),
        from: (page - 1) * pageSize,
        size: pageSize,
        aggs: {
          property_types: {
            terms: { field: 'property_type', size: 10 }
          },
          price_ranges: {
            range: {
              field: 'price',
              ranges: [
                { to: 200000 },
                { from: 200000, to: 400000 },
                { from: 400000, to: 600000 },
                { from: 600000, to: 800000 },
                { from: 800000 }
              ]
            }
          },
          avg_price: {
            avg: { field: 'price' }
          }
        }
      }
    });

    // Format response
    const results = {
      total: response.hits.total.value,
      page,
      pageSize,
      totalPages: Math.ceil(response.hits.total.value / pageSize),
      listings: response.hits.hits.map(hit => ({
        id: hit._id,
        score: hit._score,
        ...hit._source
      })),
      aggregations: {
        property_types: response.aggregations.property_types.buckets,
        price_ranges: response.aggregations.price_ranges.buckets,
        avg_price: Math.round(response.aggregations.avg_price.value)
      }
    };

    res.json(results);

  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({
      error: 'Search failed',
      message: error.message
    });
  }
});

/**
 * GET /api/search/autocomplete
 * Autocomplete for locations
 */
router.get('/autocomplete', async (req, res) => {
  try {
    const { q } = req.query;

    if (!q || q.length < 2) {
      return res.json({ suggestions: [] });
    }

    const response = await es.search({
      index: 'properties',
      body: {
        size: 0,
        aggs: {
          cities: {
            terms: {
              field: 'city',
              include: `.*${q}.*`,
              size: 10
            }
          },
          neighborhoods: {
            terms: {
              field: 'neighborhood',
              include: `.*${q}.*`,
              size: 10
            }
          },
          zips: {
            terms: {
              field: 'zip',
              include: `${q}.*`,
              size: 10
            }
          }
        }
      }
    });

    const suggestions = [
      ...response.aggregations.cities.buckets.map(b => ({
        type: 'city',
        value: b.key,
        count: b.doc_count
      })),
      ...response.aggregations.neighborhoods.buckets.map(b => ({
        type: 'neighborhood',
        value: b.key,
        count: b.doc_count
      })),
      ...response.aggregations.zips.buckets.map(b => ({
        type: 'zip',
        value: b.key,
        count: b.doc_count
      }))
    ];

    res.json({ suggestions });

  } catch (error) {
    console.error('Autocomplete error:', error);
    res.status(500).json({ error: 'Autocomplete failed' });
  }
});

/**
 * GET /api/search/similar/:propertyId
 * Find similar properties
 */
router.get('/similar/:propertyId', async (req, res) => {
  try {
    const { propertyId } = req.params;

    // Get the subject property
    const property = await es.get({
      index: 'properties',
      id: propertyId
    });

    const source = property._source;

    // Find similar properties
    const response = await es.search({
      index: 'properties',
      body: {
        query: {
          bool: {
            must: [
              { term: { status: 'active' } }
            ],
            filter: [
              { term: { property_type: source.property_type } },
              {
                geo_distance: {
                  distance: '5mi',
                  location: source.location
                }
              },
              {
                range: {
                  price: {
                    gte: source.price * 0.8,
                    lte: source.price * 1.2
                  }
                }
              },
              {
                range: {
                  bedrooms: {
                    gte: Math.max(source.bedrooms - 1, 0),
                    lte: source.bedrooms + 1
                  }
                }
              }
            ],
            must_not: [
              { term: { property_id: propertyId } }
            ]
          }
        },
        size: 10
      }
    });

    const similar = response.hits.hits.map(hit => hit._source);
    res.json({ similar });

  } catch (error) {
    console.error('Similar properties error:', error);
    res.status(500).json({ error: 'Failed to find similar properties' });
  }
});

/**
 * Build Elasticsearch query from search parameters
 */
function buildQuery(query, location, filters) {
  const must = [];
  const filter = [{ term: { status: 'active' } }];

  // Text search
  if (query) {
    must.push({
      multi_match: {
        query,
        fields: ['address^3', 'city^2', 'neighborhood^2', 'description'],
        fuzziness: 'AUTO'
      }
    });
  }

  // Location search
  if (location && location.lat && location.lon) {
    filter.push({
      geo_distance: {
        distance: `${location.radius || 10}mi`,
        location: {
          lat: location.lat,
          lon: location.lon
        }
      }
    });
  }

  // Bounding box (map viewport)
  if (location && location.bounds) {
    filter.push({
      geo_bounding_box: {
        location: {
          top_left: {
            lat: location.bounds.north,
            lon: location.bounds.west
          },
          bottom_right: {
            lat: location.bounds.south,
            lon: location.bounds.east
          }
        }
      }
    });
  }

  // Price filter
  if (filters.price) {
    const priceRange = {};
    if (filters.price.min) priceRange.gte = filters.price.min;
    if (filters.price.max) priceRange.lte = filters.price.max;
    if (Object.keys(priceRange).length > 0) {
      filter.push({ range: { price: priceRange } });
    }
  }

  // Bedrooms filter
  if (filters.bedrooms) {
    const bedroomRange = {};
    if (filters.bedrooms.min) bedroomRange.gte = filters.bedrooms.min;
    if (filters.bedrooms.max) bedroomRange.lte = filters.bedrooms.max;
    if (Object.keys(bedroomRange).length > 0) {
      filter.push({ range: { bedrooms: bedroomRange } });
    }
  }

  // Bathrooms filter
  if (filters.bathrooms) {
    const bathroomRange = {};
    if (filters.bathrooms.min) bathroomRange.gte = filters.bathrooms.min;
    if (filters.bathrooms.max) bathroomRange.lte = filters.bathrooms.max;
    if (Object.keys(bathroomRange).length > 0) {
      filter.push({ range: { bathrooms: bathroomRange } });
    }
  }

  // Square footage filter
  if (filters.sqft) {
    const sqftRange = {};
    if (filters.sqft.min) sqftRange.gte = filters.sqft.min;
    if (filters.sqft.max) sqftRange.lte = filters.sqft.max;
    if (Object.keys(sqftRange).length > 0) {
      filter.push({ range: { sqft: sqftRange } });
    }
  }

  // Property type filter
  if (filters.property_type && filters.property_type.length > 0) {
    filter.push({
      terms: { property_type: filters.property_type }
    });
  }

  // Features filter
  if (filters.features) {
    if (filters.features.pool) {
      filter.push({ term: { has_pool: true } });
    }
    if (filters.features.ac) {
      filter.push({ term: { has_ac: true } });
    }
    if (filters.features.garage && filters.features.garage > 0) {
      filter.push({
        range: { garage_spaces: { gte: filters.features.garage } }
      });
    }
  }

  return {
    bool: {
      must: must.length > 0 ? must : [{ match_all: {} }],
      filter
    }
  };
}

/**
 * Get sort criteria
 */
function getSortCriteria(sortOption) {
  const sortOptions = {
    relevance: [{ _score: 'desc' }],
    price_asc: [{ price: 'asc' }],
    price_desc: [{ price: 'desc' }],
    newest: [{ listing_date: 'desc' }],
    sqft_desc: [{ sqft: 'desc' }],
    beds_desc: [{ bedrooms: 'desc' }]
  };

  return sortOptions[sortOption] || sortOptions.relevance;
}

module.exports = router;

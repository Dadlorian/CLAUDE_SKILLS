# SEO Reference for Real Estate Marketplaces

## Quick Reference for Real Estate SEO

### Property Page SEO Structure

#### URL Structure

**Best Practices**:
```
Good:
/property/123-main-st-austin-tx-78701-12345
/homes-for-sale/austin-tx/78701/123-main-st

Bad:
/property?id=12345
/listing.php?mls=12345
```

**Pattern**:
```javascript
const generatePropertyURL = (listing) => {
  const address = slugify(listing.address);
  const city = slugify(listing.city);
  const state = listing.state.toLowerCase();
  const zip = listing.zip;
  const id = listing.id;

  return `/property/${address}-${city}-${state}-${zip}-${id}`;
};

// slugify function
const slugify = (text) => {
  return text.toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
};
```

#### Title Tags

**Template**:
```
{beds} BR, {baths} BA Home at {address}, {city}, {state} {zip} | {site_name}

Examples:
3 BR, 2 BA Home at 123 Main St, Austin, TX 78701 | Austin Realty
Luxury 4 Bedroom Home for Sale in Downtown Dallas | DFW Homes
```

**Implementation**:
```javascript
const generateTitle = (listing) => {
  const beds = listing.bedrooms;
  const baths = listing.bathrooms;
  const address = listing.address;
  const city = listing.city;
  const state = listing.state;
  const zip = listing.zip;

  return `${beds} BR, ${baths} BA Home at ${address}, ${city}, ${state} ${zip} | Your Site`;
};
```

#### Meta Descriptions

**Template**:
```
{property_type} for sale in {neighborhood}, {city}. {beds} bedrooms, {baths} bathrooms, {sqft} sqft. ${price}. {unique_feature}. {cta}

Examples:
Beautiful single-family home in Hyde Park, Austin. 3 bedrooms, 2 bathrooms, 2,000 sqft. $450,000. Updated kitchen with granite countertops. Schedule a showing today!
```

**Implementation**:
```javascript
const generateMetaDescription = (listing) => {
  const propertyType = listing.property_type_display;
  const neighborhood = listing.neighborhood || listing.city;
  const uniqueFeature = extractUniqueFeature(listing.features);

  return `${propertyType} for sale in ${neighborhood}, ${listing.city}. ` +
         `${listing.bedrooms} bedrooms, ${listing.bathrooms} bathrooms, ` +
         `${listing.sqft.toLocaleString()} sqft. ` +
         `$${listing.price.toLocaleString()}. ${uniqueFeature}. ` +
         `Schedule a showing today!`;
};
```

### Schema.org Structured Data

#### RealEstateListing Schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "RealEstateListing",
  "name": "Beautiful 3 Bedroom Home in Austin",
  "url": "https://example.com/property/123-main-st-austin-tx",
  "image": [
    "https://cdn.example.com/photos/12345_1.jpg",
    "https://cdn.example.com/photos/12345_2.jpg"
  ],
  "description": "Beautiful home in downtown Austin with updated kitchen...",
  "offers": {
    "@type": "Offer",
    "price": "450000",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/property/123-main-st-austin-tx"
  },
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "Austin",
    "addressRegion": "TX",
    "postalCode": "78701",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "30.2672",
    "longitude": "-97.7431"
  },
  "numberOfRooms": 3,
  "numberOfBedrooms": 3,
  "numberOfBathroomsTotal": 2,
  "floorSize": {
    "@type": "QuantitativeValue",
    "value": 2000,
    "unitCode": "FTK"
  },
  "yearBuilt": 2010,
  "datePosted": "2025-01-15",
  "propertyType": "SingleFamilyResidence"
}
</script>
```

#### Apartment Schema

```javascript
const generateApartmentSchema = (listing) => {
  return {
    "@context": "https://schema.org",
    "@type": "Apartment",
    "name": `${listing.bedrooms} Bedroom Apartment`,
    "url": listing.url,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": listing.address,
      "addressLocality": listing.city,
      "addressRegion": listing.state,
      "postalCode": listing.zip
    },
    "numberOfRooms": listing.bedrooms,
    "floorSize": {
      "@type": "QuantitativeValue",
      "value": listing.sqft,
      "unitCode": "FTK"
    },
    "occupancy": {
      "@type": "QuantitativeValue",
      "maxValue": listing.bedrooms * 2
    },
    "petsAllowed": listing.pets_allowed
  };
};
```

### Programmatic SEO Pages

#### Location Pages

```javascript
// Generate city landing pages
const cityPageTemplate = (city, state) => ({
  url: `/homes-for-sale/${state.toLowerCase()}/${slugify(city)}`,
  title: `Homes for Sale in ${city}, ${state} | Real Estate Listings`,
  h1: `${city}, ${state} Real Estate & Homes for Sale`,
  content: {
    intro: `Find your dream home in ${city}, ${state}...`,
    sections: [
      'Market Overview',
      'Neighborhoods',
      'Schools',
      'Things to Do',
      'Recent Sales'
    ]
  }
});

// Generate neighborhood pages
const neighborhoodPageTemplate = (neighborhood, city, state) => ({
  url: `/homes/${slugify(city)}/${slugify(neighborhood)}`,
  title: `${neighborhood} Homes for Sale in ${city}, ${state}`,
  h1: `${neighborhood}, ${city} Real Estate`,
  content: `Discover homes in the ${neighborhood} neighborhood of ${city}...`
});

// Generate ZIP code pages
const zipPageTemplate = (zip, city, state) => ({
  url: `/homes-for-sale/${state.toLowerCase()}/${slugify(city)}/${zip}`,
  title: `Homes for Sale in ${zip} - ${city}, ${state}`,
  h1: `${zip} Real Estate & Homes for Sale`
});
```

#### Market Report Pages

```javascript
const marketReportTemplate = (city, state, month, year) => ({
  url: `/market-report/${state.toLowerCase()}/${slugify(city)}/${year}/${month}`,
  title: `${city} Real Estate Market Report - ${month} ${year}`,
  h1: `${city}, ${state} Housing Market - ${month} ${year}`,
  sections: {
    median_price: {
      title: 'Median Home Price',
      data: '$450,000 (+5.2% YoY)'
    },
    inventory: {
      title: 'Active Listings',
      data: '1,247 homes (-12% YoY)'
    },
    days_on_market: {
      title: 'Median Days on Market',
      data: '23 days'
    },
    price_trends: {
      title: 'Price Trends',
      chart: 'line_chart_data'
    }
  }
});
```

### Internal Linking Strategy

```javascript
const internalLinkingRules = {
  // From property pages
  property_page: {
    links_to: [
      'similar_properties', // 3-5 similar listings
      'neighborhood_page',  // Neighborhood landing page
      'city_page',          // City landing page
      'market_report',      // Latest market report
      'agent_profile'       // Listing agent page
    ]
  },

  // From city pages
  city_page: {
    links_to: [
      'neighborhood_pages',  // All neighborhoods
      'recent_listings',     // Latest 10 listings
      'market_report',       // City market report
      'school_pages'         // School district pages
    ]
  },

  // From neighborhood pages
  neighborhood_page: {
    links_to: [
      'active_listings',     // All active listings
      'sold_properties',     // Recent sales
      'city_page',           // Parent city page
      'nearby_neighborhoods' // Adjacent neighborhoods
    ]
  }
};
```

### Image SEO

#### Alt Text Best Practices

```javascript
const generateImageAltText = (listing, photoIndex, photoType) => {
  const templates = {
    exterior: `Front view of ${listing.bedrooms} bedroom home at ${listing.address}, ${listing.city}`,
    kitchen: `Modern kitchen with ${extractFeature(listing, 'kitchen')} at ${listing.address}`,
    bedroom: `Master bedroom in ${listing.city} home`,
    bathroom: `Updated bathroom in ${listing.address} property`,
    backyard: `Backyard of ${listing.address}, ${listing.city}`
  };

  return templates[photoType] ||
         `Photo ${photoIndex + 1} of ${listing.address}, ${listing.city}, ${listing.state}`;
};

// Implementation
listing.photos.forEach((photo, index) => {
  photo.alt = generateImageAltText(listing, index, photo.type);
  photo.title = `${listing.address} - Photo ${index + 1}`;
});
```

#### Image Optimization

```javascript
// Responsive images with srcset
const generateImageSrcSet = (baseUrl, sizes = [320, 640, 1024, 1920]) => {
  return sizes.map(width => `${baseUrl}?w=${width} ${width}w`).join(', ');
};

// Usage in HTML
const imageHTML = `
  <img
    src="${photo.url}?w=1024"
    srcset="${generateImageSrcSet(photo.url)}"
    sizes="(max-width: 640px) 100vw,
           (max-width: 1024px) 50vw,
           33vw"
    alt="${photo.alt}"
    loading="lazy"
  />
`;
```

### Performance Optimization

#### Critical Rendering Path

```html
<!-- Inline critical CSS -->
<style>
  /* Above-the-fold styles */
  .property-header { ... }
  .photo-gallery { ... }
  .key-details { ... }
</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="/css/full.css" as="style" onload="this.onload=null;this.rel='stylesheet'">

<!-- Preload critical images -->
<link rel="preload" as="image" href="${mainPhoto.url}">

<!-- Preconnect to CDN -->
<link rel="preconnect" href="https://cdn.example.com">
```

#### Lazy Loading

```javascript
// Lazy load images below fold
const observerOptions = {
  root: null,
  rootMargin: '50px',
  threshold: 0.01
};

const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.srcset = img.dataset.srcset;
      imageObserver.unobserve(img);
    }
  });
}, observerOptions);

document.querySelectorAll('img[data-src]').forEach(img => {
  imageObserver.observe(img);
});
```

### Mobile Optimization

```html
<!-- Responsive viewport -->
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Mobile-friendly tap targets (48x48px minimum) -->
<button class="contact-agent" style="min-width: 48px; min-height: 48px;">
  Contact Agent
</button>

<!-- AMP for instant mobile loading (optional) -->
<link rel="amphtml" href="https://example.com/property/123/amp">
```

### Local SEO

#### Google My Business Integration

```javascript
const generateLocalBusinessSchema = (office) => {
  return {
    "@context": "https://schema.org",
    "@type": "RealEstateAgent",
    "name": office.name,
    "image": office.logo,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": office.address,
      "addressLocality": office.city,
      "addressRegion": office.state,
      "postalCode": office.zip
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": office.latitude,
      "longitude": office.longitude
    },
    "url": office.website,
    "telephone": office.phone,
    "priceRange": "$$",
    "openingHoursSpecification": [
      {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "09:00",
        "closes": "18:00"
      }
    ]
  };
};
```

### Canonical URLs

```html
<!-- Prevent duplicate content -->
<link rel="canonical" href="https://example.com/property/123-main-st-austin-tx">

<!-- Handle parameters -->
<link rel="canonical" href="https://example.com/search/austin-tx">
<!-- Even if accessed via: /search?city=Austin&state=TX -->
```

### XML Sitemaps

```javascript
const generatePropertySitemap = async () => {
  const listings = await getActiveListings();

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${listings.map(listing => `
  <url>
    <loc>https://example.com${generatePropertyURL(listing)}</loc>
    <lastmod>${listing.updated_at.toISOString().split('T')[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
    <image:image>
      <image:loc>${listing.main_photo}</image:loc>
      <image:caption>${listing.address}</image:caption>
    </image:image>
  </url>
  `).join('')}
</urlset>`;

  return sitemap;
};

// Dynamic sitemap index
const generateSitemapIndex = () => {
  return `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-properties.xml</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-locations.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-pages.xml</loc>
  </sitemap>
</sitemapindex>`;
};
```

### SEO Monitoring Metrics

| Metric | Tool | Target |
|--------|------|--------|
| Page Speed | Lighthouse | > 90 |
| Core Web Vitals | Search Console | All "Good" |
| Index Coverage | Search Console | 95%+ indexed |
| Organic Traffic | Analytics | +10% MoM |
| Keyword Rankings | SEMrush/Ahrefs | Top 10 for targets |
| Click-Through Rate | Search Console | > 3% |

### Common SEO Mistakes to Avoid

❌ **Duplicate Content**
- Multiple URLs for same listing
- Boilerplate descriptions
- Solution: Canonical tags, unique content

❌ **Slow Page Speed**
- Unoptimized images
- Render-blocking resources
- Solution: Image optimization, code splitting

❌ **Poor Mobile Experience**
- Unresponsive design
- Small tap targets
- Solution: Mobile-first design

❌ **Missing Structured Data**
- No Schema.org markup
- Solution: Implement RealEstateListing schema

❌ **Thin Content**
- Auto-generated pages with no value
- Solution: Add unique, helpful content

## See Also
- property_search_reference.md
- listing_syndication_reference.md
- lead_management_reference.md

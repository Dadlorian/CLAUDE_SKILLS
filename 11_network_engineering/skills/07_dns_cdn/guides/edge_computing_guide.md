# Edge Computing Guide

## Edge Computing Overview

### Definition
Computation at the network edge (geographically distributed servers) instead of centralized origin

```
Traditional Architecture:
Client -> Internet -> Origin Server -> Response
(100-500ms latency)

Edge Computing Architecture:
Client -> Edge Node -> Origin Server -> Response
(< 50ms latency, often handled at edge)
```

### Benefits
- **Latency**: Sub-50ms response times globally
- **Bandwidth**: Reduced origin traffic (compute at edge)
- **Personalization**: User-aware request modification
- **Security**: WAF, bot detection at edge
- **Cost**: Lower origin infrastructure needs

## Edge Computing Platforms

### Cloudflare Workers

**Overview:**
- Serverless functions at Cloudflare edge (275+ locations)
- JavaScript/Wasm runtime
- 50ms execution limit
- Distributed key-value store

**Deployment:**
```bash
# Install Wrangler CLI
npm install -g @cloudflare/wrangler

# Create project
wrangler init my-worker

# Configure (wrangler.toml)
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-11-19"
```

**Basic Worker:**
```javascript
// src/index.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Route requests
    if (url.pathname.startsWith("/api/")) {
      return handleAPI(request);
    } else if (url.pathname.startsWith("/image/")) {
      return handleImage(request);
    } else {
      return handleDefault(request);
    }
  }
};

async function handleAPI(request) {
  // Fetch from origin
  const response = await fetch("https://origin.example.com" + request.url.pathname);
  return response;
}

async function handleImage(request) {
  // Optimize images
  const url = new URL(request.url);
  const imageUrl = url.searchParams.get("url");

  // Fetch image from origin
  const image = await fetch(imageUrl);

  // Resize if requested
  const width = url.searchParams.get("width");
  if (width) {
    // Use Cloudflare Image Processing
    const resized = image.clone();
    resized.headers.set("cf-image-optimization", `width=${width}`);
    return resized;
  }

  return image;
}

async function handleDefault(request) {
  return new Response("Hello from Cloudflare Workers!");
}
```

**Deploy:**
```bash
wrangler deploy
# Worker deployed to edge
```

### AWS Lambda@Edge

**Overview:**
- AWS Lambda functions at CloudFront edge
- Node.js or Python runtime
- Viewer-facing or origin-facing triggers
- Real-time request/response modification

**Event Sources:**
```
1. CloudFront Viewer Request (before cache check)
2. CloudFront Origin Request (cache miss)
3. CloudFront Origin Response (from origin)
4. CloudFront Viewer Response (before sending to client)
```

**Function Example:**
```javascript
// index.js
exports.handler = async (event, context) => {
  const request = event.Records[0].cf.request;
  const headers = request.headers;

  // Add security headers
  const response = {
    status: '200',
    statusDescription: 'OK',
    headers: {
      'x-frame-options': [{ key: 'X-Frame-Options', value: 'DENY' }],
      'x-content-type-options': [{ key: 'X-Content-Type-Options', value: 'nosniff' }],
      'strict-transport-security': [{ key: 'Strict-Transport-Security', value: 'max-age=31536000' }],
    },
  };

  return response;
};
```

**Deployment:**
```bash
# Package function
zip function.zip index.js

# Upload to Lambda
aws lambda create-function \
  --function-name edge-security \
  --runtime nodejs18.x \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler index.handler \
  --zip-file fileb://function.zip

# Publish version
aws lambda publish-version \
  --function-name edge-security

# Attach to CloudFront
aws cloudfront update-distribution-config \
  --distribution-id E123ABC \
  --lambda-function-associations \
  EventType=viewer-response,LambdaFunctionARN=arn:aws:lambda:us-east-1:ACCOUNT:function:edge-security:1
```

### Fastly Compute

**Overview:**
- Serverless compute platform
- WebAssembly (Wasm) support
- Rust, JavaScript, Go support
- Real-time request transformation

**Example (Rust):**
```rust
use fastly::{ Cache, Request, Response };

#[fastly::main]
fn main(req: Request) -> Result<Response, Box<dyn std::error::Error>> {
  // Check cache
  let mut cache = Cache::new();
  match cache.get(&req) {
    Ok(Some(response)) => return Ok(response),
    _ => {},
  }

  // Transform request
  let mut req = req;
  req.append_header("X-Forwarded-For", "1.2.3.4");

  // Fetch from origin
  let mut resp = req.send("origin_backend")?;

  // Add response headers
  resp.set_header("Cache-Control", "public, max-age=3600");
  resp.set_header("X-Edge-Location", "us-east-1");

  // Cache response
  cache.set(&resp);

  Ok(resp)
}
```

## Request Transformation Patterns

### Pattern 1: User-Agent Based Routing

**Use Case:**
```
Route mobile users to mobile-optimized server
Route desktop users to desktop server
```

**Implementation (Cloudflare Workers):**
```javascript
export default {
  async fetch(request) {
    const userAgent = request.headers.get("User-Agent");
    let origin = "https://desktop.example.com";

    if (userAgent.includes("Mobile") || userAgent.includes("iPad")) {
      origin = "https://mobile.example.com";
    }

    // Fetch from appropriate origin
    return fetch(origin + request.url.pathname);
  }
};
```

### Pattern 2: Geographic Routing

**Use Case:**
```
Route European users to EU servers
Route Asian users to Asia servers
```

**Implementation:**
```javascript
export default {
  async fetch(request, env) {
    const country = request.headers.get("CF-IPCountry");

    const origins = {
      US: "https://us.example.com",
      GB: "https://eu.example.com",
      DE: "https://eu.example.com",
      JP: "https://asia.example.com",
      CN: "https://asia.example.com",
    };

    const origin = origins[country] || origins.US;
    return fetch(origin + request.url.pathname);
  }
};
```

### Pattern 3: A/B Testing

**Use Case:**
```
Route 10% of users to new version
Route 90% of users to stable version
```

**Implementation:**
```javascript
export default {
  async fetch(request) {
    const cookie = request.headers.get("Cookie");
    const hasABTest = cookie && cookie.includes("ab_test=new");

    if (!hasABTest) {
      // 10% go to new version
      const random = Math.random();
      if (random < 0.1) {
        const response = await fetch("https://new.example.com" + request.url.pathname);
        response.headers.set("Set-Cookie", "ab_test=new; Max-Age=2592000");
        return response;
      }
    } else {
      // Existing users continue with same version
      return fetch("https://new.example.com" + request.url.pathname);
    }

    return fetch("https://stable.example.com" + request.url.pathname);
  }
};
```

### Pattern 4: Request/Response Modification

**Add Custom Headers:**
```javascript
export default {
  async fetch(request) {
    // Modify request
    const req = new Request(request);
    req.headers.set("X-Client-IP", "1.2.3.4");
    req.headers.set("X-Edge-Location", "nyc");

    // Fetch from origin
    const response = await fetch("https://origin.example.com", { request: req });

    // Modify response
    const newResponse = new Response(response.body);
    newResponse.headers.set("X-Cache-Status", "HIT");
    newResponse.headers.set("X-Response-Time", "25ms");

    return newResponse;
  }
};
```

## Advanced Edge Computing

### Authentication at Edge

**Check authentication before origin request:**
```javascript
export default {
  async fetch(request, env) {
    // Extract token
    const token = request.headers.get("Authorization");

    if (!token) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" }
      });
    }

    // Verify token with edge KV store
    const user = await env.AUTH_KV.get(token);

    if (!user) {
      return new Response("Unauthorized", { status: 401 });
    }

    // Add user info to request header
    const newRequest = new Request(request);
    newRequest.headers.set("X-User-ID", user);

    return fetch("https://origin.example.com", { request: newRequest });
  }
};
```

### Real-Time Analytics at Edge

**Track requests without origin latency:**
```javascript
export default {
  async fetch(request, env) {
    const country = request.headers.get("CF-IPCountry");
    const userAgent = request.headers.get("User-Agent");
    const path = request.url.pathname;

    // Log analytics asynchronously (non-blocking)
    env.ANALYTICS_QUEUE.send({
      country,
      userAgent,
      path,
      timestamp: Date.now()
    });

    // Fetch from origin (while analytics queued)
    return fetch("https://origin.example.com" + path);
  }
};
```

### Cache Manipulation at Edge

**Dynamic cache control based on content:**
```javascript
export default {
  async fetch(request, env) {
    const response = await fetch("https://origin.example.com" + request.url.pathname);

    // Check response content-type
    const contentType = response.headers.get("Content-Type");

    let cacheControl;
    if (contentType.includes("image")) {
      cacheControl = "public, max-age=31536000, immutable";  // 1 year for images
    } else if (contentType.includes("json")) {
      cacheControl = "public, max-age=60";  // 1 minute for JSON
    } else {
      cacheControl = "public, max-age=3600";  // 1 hour for HTML
    }

    response.headers.set("Cache-Control", cacheControl);
    return response;
  }
};
```

## Performance Optimization at Edge

### Image Optimization

```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Check for image optimization request
    const width = url.searchParams.get("width");
    const format = url.searchParams.get("format");

    if (width || format) {
      const imageUrl = url.searchParams.get("image");

      // Build optimized image URL
      let optimizedUrl = imageUrl;
      if (width) optimizedUrl += `?width=${width}`;
      if (format) optimizedUrl += `${optimizedUrl.includes('?') ? '&' : '?'}format=${format}`;

      return fetch(optimizedUrl);
    }

    return fetch("https://origin.example.com" + request.url.pathname);
  }
};
```

### HTML Rewriting

```javascript
export default {
  async fetch(request, env) {
    const response = await fetch("https://origin.example.com" + request.url.pathname);

    // Rewrite HTML
    const text = await response.text();
    const rewritten = text
      .replace(/\/images\//g, "/images/optimized/")  // Route images through optimizer
      .replace(/\/styles\//g, "/styles/v2/");         // Route to new CSS version

    return new Response(rewritten, {
      status: response.status,
      headers: response.headers
    });
  }
};
```

## Monitoring Edge Functions

### Cloudflare Workers Monitoring

```javascript
// Instrument function with logging
export default {
  async fetch(request, env) {
    const startTime = Date.now();

    try {
      const response = await fetch("https://origin.example.com" + request.url.pathname);
      const duration = Date.now() - startTime;

      // Send metrics
      if (env.METRICS) {
        env.METRICS.writeDataPoint({
          name: "edge_function_duration",
          value: duration,
          labels: {
            status: response.status,
            path: request.url.pathname
          }
        });
      }

      return response;
    } catch (error) {
      // Error tracking
      if (env.ERROR_LOG) {
        env.ERROR_LOG.log({
          error: error.message,
          path: request.url.pathname,
          timestamp: new Date().toISOString()
        });
      }

      return new Response("Error", { status: 500 });
    }
  }
};
```

## Cost Optimization

### Cloudflare Workers
```
Pricing:
- 10 million requests/month: Free
- Additional: $0.50 per million requests
- Compute time: Included

Cost for 100M requests/month:
(100M - 10M) × $0.50 / 1M = $45/month
```

### AWS Lambda@Edge
```
Pricing:
- $0.60 per 1M requests (viewer-facing)
- $0.01 per GB-seconds (data transfer)

Cost for 100M requests/month with 50ms execution:
Requests: (100M × $0.60) / 1M = $60
Compute: (100M × 0.05s × 0.128GB) × $0.00001667 = $8.33
Total: ~$70/month
```

### Fastly Compute
```
Pricing:
- $0.12 per 1M compute requests
- Bandwidth: Normal CloudFront rates

Cost for 100M compute requests/month:
(100M × $0.12) / 1M = $12
```

## Best Practices

1. **Keep Functions Small**: Minimize execution time
2. **Cache Aggressively**: At edge KV store
3. **Error Handling**: Graceful degradation if origin fails
4. **Logging**: Log important events for debugging
5. **Testing**: Test locally before deploying
6. **Monitoring**: Track function performance metrics
7. **Versioning**: Version functions for easy rollback
8. **Security**: Validate all inputs, sanitize output
9. **Rate Limiting**: Implement at edge if needed
10. **Documentation**: Document function behavior

## Troubleshooting

### Function Not Executing

```
Check:
1. Function deployed correctly
2. CloudFront/Fastly attached to function
3. No syntax errors in function code
4. Execution timeout not exceeded
```

### Slow Edge Function

```
Optimize:
1. Reduce fetch calls (batch requests)
2. Use edge KV cache instead of fetching
3. Reduce response rewriting
4. Minimize compute logic
```

### High Costs

```
Reduce:
1. Number of requests processed at edge
2. Function execution time
3. Data transfer (fewer fetches)
4. Compute complexity
```

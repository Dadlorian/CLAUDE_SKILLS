// Fastly VCL Configuration
// VCL (Varnish Configuration Language) for advanced edge computing
// Fastly uses VCL for request/response manipulation at edge

// Declare backends (origin servers)
backend server1 {
  .host = "origin.example.com";
  .port = "443";
  .ssl = true;
  .ssl_cert_hostname = "origin.example.com";
  .ssl_sni_hostname = "origin.example.com";
  .connect_timeout = 10s;
  .first_byte_timeout = 30s;
  .between_bytes_timeout = 30s;
  .max_connections = 100;
  .probe = healthcheck;
}

backend server2 {
  .host = "origin2.example.com";
  .port = "443";
  .ssl = true;
  .probe = healthcheck;
}

// Define health check probe
probe healthcheck {
  .url = "/health";
  .expected_response = 200;
  .timeout = 10s;
  .interval = 10s;
  .window = 5;
  .threshold = 3;
  .initial = 3;
}

// Routing subdomain
sub vcl_recv {
  #FASTLY recv

  // Set backend based on request
  if (req.url ~ "^/api/") {
    set req.backend = server1;
  } else if (req.url ~ "^/media/") {
    set req.backend = server2;
  } else {
    set req.backend = server1;
  }

  // Remove port from Host header
  set req.http.Host = regsub(req.http.Host, ":[0-9]+$", "");

  // Normalize query string for caching
  if (req.url ~ "\?") {
    set req.url = req.url + "&";
    set req.url = regsuball(req.url, "([?&])(utm_|__cf|_ga|gclid)=[^&]+&", "\1");
    set req.url = regsub(req.url, "[?&]$", "");
  }

  // Remove tracking query parameters
  set req.url = regsuball(req.url, "(\?|&)(utm_[a-z]+|fbclid|gclid)=[^&]*", "");

  // Bypass cache for specific paths
  if (req.url ~ "^/(admin|login|checkout)") {
    set req.bypass = true;
  }

  // Set device type for cache variation
  if (req.http.User-Agent ~ "Mobile|Android|iPhone|iPad") {
    set req.http.X-Device-Type = "mobile";
  } else {
    set req.http.X-Device-Type = "desktop";
  }

  // Add client geo information
  set req.http.X-Geo-Country = client.geo.country_code;
  set req.http.X-Geo-Region = client.geo.region;

  // Remove cookies for static content
  if (req.url ~ "\.(js|css|jpg|jpeg|png|gif|ico|webp|svg|woff|woff2)$") {
    unset req.http.Cookie;
    return(lookup);
  }

  // Ensure GET/HEAD requests go to cache lookup
  if (req.method != "GET" && req.method != "HEAD" && req.method != "PUT" && req.method != "DELETE") {
    return(pass);
  }

  // Normalize Accept-Encoding
  if (req.http.Accept-Encoding) {
    if (req.http.Accept-Encoding ~ "gzip") {
      set req.http.Accept-Encoding = "gzip";
    } elsif (req.http.Accept-Encoding ~ "deflate") {
      set req.http.Accept-Encoding = "deflate";
    } else {
      unset req.http.Accept-Encoding;
    }
  }

  return(lookup);
}

// Modify request before sending to origin
sub vcl_miss {
  #FASTLY miss

  // Add header to identify origin request
  set req.http.X-Forwarded-By = "fastly";
  set req.http.X-Cache-Status = "MISS";

  return(fetch);
}

// Cache object received from origin
sub vcl_deliver {
  #FASTLY deliver

  // Add cache status headers
  set resp.http.X-Cache-Status = "HIT";
  if (obj.hits > 0) {
    set resp.http.X-Cache-Status = "HIT";
  } else {
    set resp.http.X-Cache-Status = "MISS";
  }

  // Add cache age
  set resp.http.X-Cache-Age = now - obj.last_use;

  // Modernize HTTP version info
  set resp.http.Server = "Fastly";
  unset resp.http.Via;
  unset resp.http.X-Varnish;

  // Add security headers
  if (resp.status == 200 || resp.status == 404) {
    set resp.http.Strict-Transport-Security = "max-age=31536000; includeSubDomains; preload";
    set resp.http.X-Content-Type-Options = "nosniff";
    set resp.http.X-Frame-Options = "DENY";
    set resp.http.X-XSS-Protection = "1; mode=block";
    set resp.http.Referrer-Policy = "strict-origin-when-cross-origin";
  }

  return(deliver);
}

// Process response from origin
sub vcl_fetch {
  #FASTLY fetch

  // Cache control based on content type
  if (beresp.http.Content-Type ~ "text/html") {
    // HTML: Cache 1 hour
    set beresp.ttl = 1h;
    set beresp.http.Cache-Control = "public, max-age=3600";
  } elsif (beresp.http.Content-Type ~ "application/json") {
    // JSON/API: Cache 5 minutes
    set beresp.ttl = 5m;
    set beresp.http.Cache-Control = "public, max-age=300";
  } elsif (beresp.http.Content-Type ~ "text/css") {
    // CSS: Cache 1 month
    set beresp.ttl = 30d;
    set beresp.http.Cache-Control = "public, max-age=2592000, immutable";
  } elsif (beresp.http.Content-Type ~ "application/javascript") {
    // JavaScript: Cache 1 month
    set beresp.ttl = 30d;
    set beresp.http.Cache-Control = "public, max-age=2592000, immutable";
  } elsif (beresp.http.Content-Type ~ "image/") {
    // Images: Cache 1 year
    set beresp.ttl = 365d;
    set beresp.http.Cache-Control = "public, max-age=31536000, immutable";
  } else {
    // Default: Cache 1 hour
    set beresp.ttl = 1h;
  }

  // Stale while revalidate
  set beresp.http.Cache-Control = beresp.http.Cache-Control + ", stale-while-revalidate=86400";

  // Allow serving stale content
  set beresp.stale_if_error = 86400s;  // 1 day
  set beresp.stale_while_revalidate = 86400s;

  // Respect origin cache headers
  if (beresp.http.Cache-Control ~ "private" || beresp.http.Cache-Control ~ "no-store") {
    set req.bypass = true;
  }

  // Compress with gzip/brotli
  if (beresp.http.Content-Type ~ "text|application/(json|javascript)") {
    set beresp.do_gzip = true;
  }

  return(deliver);
}

// Handle errors
sub vcl_error {
  #FASTLY error

  set obj.http.Content-Type = "text/html; charset=utf-8";
  set obj.http.Retry-After = "5";

  synthetic {"
<!DOCTYPE html>
<html>
  <head>
    <title>Error "</obj.status" "</obj.response"</title>
  </head>
  <body>
    <h1>Error "</obj.status" "</obj.response"</h1>
    <p>Sorry, the origin server returned an error.</p>
  </body>
</html>
  "};

  return(deliver);
}

// Purge cache
sub vcl_purge {
  #FASTLY purge

  if (req.method == "PURGE") {
    set req.http.X-Purge = "Yes";
  }

  return(deliver);
}

// Set cache key (used for cache lookup)
sub vcl_hash {
  #FASTLY hash

  // Include URL in cache key
  set req.hash += req.url;

  // Include Host header
  set req.hash += req.http.host;

  // Include device type in cache key
  if (req.http.X-Device-Type) {
    set req.hash += req.http.X-Device-Type;
  }

  // Include Accept-Encoding
  if (req.http.Accept-Encoding) {
    set req.hash += req.http.Accept-Encoding;
  }

  return(hash);
}

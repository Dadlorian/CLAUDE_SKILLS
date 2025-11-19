# Varnish Cache Configuration
# File: /etc/varnish/default.vcl
# High-performance HTTP caching reverse proxy

vcl 4.1;

# Define backends (origin servers)
backend default {
    .host = "origin.example.com";
    .port = "80";
    .connect_timeout = 10s;
    .first_byte_timeout = 30s;
    .between_bytes_timeout = 30s;

    # Health probe
    .probe = {
        .url = "/health";
        .interval = 10s;
        .timeout = 5s;
        .window = 5;
        .threshold = 3;
        .initial = 3;
    }
}

backend secondary {
    .host = "origin2.example.com";
    .port = "80";
    .connect_timeout = 10s;
    .first_byte_timeout = 30s;
    .between_bytes_timeout = 30s;

    .probe = {
        .url = "/health";
        .interval = 10s;
        .timeout = 5s;
    }
}

# Access Control List for purging
acl purge {
    "localhost";
    "127.0.0.1";
    "192.168.1.0"/24;
}

# Initial request processing
sub vcl_recv {
    # Select backend based on URL
    if (req.url ~ "^/media/") {
        set req.backend_hint = secondary;
    } else {
        set req.backend_hint = default;
    }

    # Remove port from Host header
    set req.http.Host = regsub(req.http.Host, ":[0-9]+$", "");

    # Normalize URL (remove tracking parameters)
    set req.url = regsuball(req.url, "([?&])(utm_[a-z]+|fbclid|gclid)=[^&]*", "");

    # Handle PURGE requests
    if (req.method == "PURGE") {
        if (!client.ip ~ purge) {
            return (synth(403, "Purge not allowed"));
        }

        return (purge);
    }

    # Handle BAN requests
    if (req.method == "BAN") {
        if (!client.ip ~ purge) {
            return (synth(403, "Ban not allowed"));
        }

        # Ban all matching objects
        ban("req.url ~ " + req.url);
        return (synth(200, "Banned"));
    }

    # Only cache GET and HEAD
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }

    # Bypass cache for admin/login
    if (req.url ~ "^/(admin|login|checkout|user)") {
        return (pass);
    }

    # Remove cookies for static content
    if (req.url ~ "\.(js|css|jpg|jpeg|png|gif|ico|webp|svg|woff|woff2)$") {
        unset req.http.Cookie;
    }

    # Normalize Accept-Encoding
    if (req.http.Accept-Encoding) {
        if (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } elsif (req.http.Accept-Encoding ~ "deflate") {
            set req.http.Accept-Encoding = "deflate";
        } else {
            unset req.http.Accept-Encoding;
        }
    }
}

# Backend response processing
sub vcl_backend_response {
    # Cache control based on content type
    if (beresp.http.Content-Type ~ "text/html") {
        # HTML: Cache 1 hour
        set beresp.ttl = 1h;
        set beresp.http.Cache-Control = "public, max-age=3600";
    } elsif (beresp.http.Content-Type ~ "application/json") {
        # JSON: Cache 5 minutes
        set beresp.ttl = 5m;
        set beresp.http.Cache-Control = "public, max-age=300";
    } elsif (beresp.http.Content-Type ~ "text/css" ||
             beresp.http.Content-Type ~ "application/javascript") {
        # CSS/JS: Cache 30 days
        set beresp.ttl = 30d;
        set beresp.http.Cache-Control = "public, max-age=2592000, immutable";
    } elsif (beresp.http.Content-Type ~ "image/") {
        # Images: Cache 1 year
        set beresp.ttl = 365d;
        set beresp.http.Cache-Control = "public, max-age=31536000, immutable";
    } else {
        # Default: 1 hour
        set beresp.ttl = 1h;
    }

    # Stale while revalidate
    set beresp.http.Cache-Control = beresp.http.Cache-Control + ", stale-while-revalidate=86400";

    # Respect private/no-store cache control
    if (beresp.http.Cache-Control ~ "private" || beresp.http.Cache-Control ~ "no-store") {
        set beresp.uncacheable = true;
        set beresp.ttl = 0s;
    }

    # Allow serving stale content on errors
    set beresp.grace = 24h;

    # Gzip response
    if (beresp.http.Content-Type ~ "text|application/json|application/javascript") {
        set beresp.do_gzip = true;
    }

    return (deliver);
}

# Delivered response processing
sub vcl_deliver {
    # Add cache status header
    set resp.http.X-Cache-Status = obj.hits;
    set resp.http.X-Cache = "HIT";

    if (obj.hits == 0) {
        set resp.http.X-Cache = "MISS";
    }

    # Add cache age
    set resp.http.Age = std.integer(now - obj.time_first_use);

    # Remove backend headers
    unset resp.http.Via;
    unset resp.http.X-Varnish;
    unset resp.http.Server;

    # Add security headers
    set resp.http.Strict-Transport-Security = "max-age=31536000; includeSubDomains; preload";
    set resp.http.X-Content-Type-Options = "nosniff";
    set resp.http.X-Frame-Options = "DENY";
    set resp.http.X-XSS-Protection = "1; mode=block";

    return (deliver);
}

# Error handling
sub vcl_backend_error {
    # Return cached content if origin is down
    if (beresp.status == 503 || beresp.status == 504) {
        return (deliver);
    }

    synthetic {
        "<!DOCTYPE html>
        <html>
        <head>
            <title>Error " + beresp.status + " " + beresp.reason + "</title>
        </head>
        <body>
            <h1>Error " + beresp.status + " " + beresp.reason + "</h1>
            <p>Sorry, the backend server is temporarily unavailable.</p>
        </body>
        </html>"
    };

    return (deliver);
}

# Hash (cache key) calculation
sub vcl_hash {
    hash_data(req.url);

    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }

    # Include Accept-Encoding in hash
    if (req.http.Accept-Encoding) {
        hash_data(req.http.Accept-Encoding);
    }

    return (lookup);
}

# Synthetic errors
sub vcl_synth {
    set resp.http.Content-Type = "text/html; charset=utf-8";

    if (resp.status == 403) {
        set resp.body = "Forbidden";
    } elsif (resp.status == 404) {
        set resp.body = "Not Found";
    } else {
        set resp.body = resp.status + " " + resp.reason;
    }

    return (deliver);
}

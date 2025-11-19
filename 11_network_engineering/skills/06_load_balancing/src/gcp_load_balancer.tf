# Google Cloud Platform Load Balancing Configuration
# Terraform - Global Load Balancing Setup
# Last Updated: 2025-11-19

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# Health Check
resource "google_compute_health_check" "main" {
  name               = "prod-health-check"
  check_interval_sec = 30
  timeout_sec        = 5

  http_health_check {
    request_path = "/health"
    port         = "80"
  }
}

# Health Check for API
resource "google_compute_health_check" "api" {
  name               = "prod-api-health-check"
  check_interval_sec = 10
  timeout_sec        = 5

  http_health_check {
    request_path = "/api/health"
    port         = "8080"
  }
}

# Backend Service for Web
resource "google_compute_backend_service" "web" {
  name                    = "prod-web-backend"
  protocol                = "HTTP"
  port_name              = "http"
  load_balancing_scheme  = "EXTERNAL"
  health_checks          = [google_compute_health_check.main.id]
  timeout_sec            = 30
  enable_cdn             = true
  custom_request_headers = ["X-Client-Region:{client_region}"]

  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    default_ttl       = 3600
    max_ttl           = 86400
    negative_caching  = true
  }

  session_affinity = "CLIENT_IP"
  affinity_cookie_ttl_sec = 3600

  backend {
    group           = google_compute_instance_group.web.self_link
    balancing_mode  = "RATE"
    max_rate        = 100
    capacity_scaler = 1.0
  }
}

# Backend Service for API
resource "google_compute_backend_service" "api" {
  name                   = "prod-api-backend"
  protocol               = "HTTP"
  port_name              = "api"
  load_balancing_scheme  = "EXTERNAL"
  health_checks          = [google_compute_health_check.api.id]
  timeout_sec            = 60
  enable_cdn             = false

  session_affinity = "NONE"

  backend {
    group          = google_compute_instance_group.api.self_link
    balancing_mode = "RATE"
    max_rate       = 200
  }
}

# Instance Group for Web Servers
resource "google_compute_instance_group" "web" {
  name      = "prod-web-ig"
  zone      = var.gcp_zone
  instances = var.web_instance_ids

  named_port {
    name = "http"
    port = 80
  }
}

# Instance Group for API Servers
resource "google_compute_instance_group" "api" {
  name      = "prod-api-ig"
  zone      = var.gcp_zone
  instances = var.api_instance_ids

  named_port {
    name = "api"
    port = 8080
  }
}

# Global Address for Load Balancer
resource "google_compute_global_address" "main" {
  name          = "prod-lb-ip"
  address_type  = "EXTERNAL"
  ip_version    = "IPV4"
  prefix_length = 32
}

# SSL Certificate
resource "google_compute_ssl_certificate" "main" {
  name            = "prod-ssl-cert"
  private_key     = file(var.ssl_key_path)
  certificate     = file(var.ssl_cert_path)

  lifecycle {
    create_before_destroy = true
  }
}

# URL Map for Routing
resource "google_compute_url_map" "main" {
  name            = "prod-url-map"
  default_service = google_compute_backend_service.web.id

  path_rule {
    paths   = ["/api", "/api/*"]
    service = google_compute_backend_service.api.id
  }

  host_rule {
    hosts        = ["api.example.com", "api.*.example.com"]
    path_matcher = "api"
  }
}

# Path Matcher for Host-based Routing
resource "google_compute_url_map" "main_with_host" {
  name            = "prod-url-map-host"
  default_service = google_compute_backend_service.web.id

  host_rule {
    hosts        = ["api.example.com"]
    path_matcher = "api-paths"
  }

  path_matcher {
    name            = "api-paths"
    default_service = google_compute_backend_service.api.id
  }
}

# HTTP to HTTPS Redirect
resource "google_compute_url_map" "https_redirect" {
  name = "prod-https-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query           = false
  }
}

# HTTP Proxy
resource "google_compute_target_http_proxy" "main" {
  name     = "prod-http-proxy"
  url_map  = google_compute_url_map.https_redirect.id
}

# HTTPS Proxy
resource "google_compute_target_https_proxy" "main" {
  name             = "prod-https-proxy"
  url_map          = google_compute_url_map.main_with_host.id
  ssl_certificates = [google_compute_ssl_certificate.main.id]
  ssl_policy       = google_compute_ssl_policy.main.id
}

# SSL Policy
resource "google_compute_ssl_policy" "main" {
  name            = "prod-ssl-policy"
  profile         = "RESTRICTED"
  min_tls_version = "TLS_1_2"
}

# Global Forwarding Rule - HTTP
resource "google_compute_global_forwarding_rule" "http" {
  name       = "prod-http-lb"
  target     = google_compute_target_http_proxy.main.id
  ip_address = google_compute_global_address.main.address
  port_range = "80"
}

# Global Forwarding Rule - HTTPS
resource "google_compute_global_forwarding_rule" "https" {
  name       = "prod-https-lb"
  target     = google_compute_target_https_proxy.main.id
  ip_address = google_compute_global_address.main.address
  port_range = "443"
}

# Cloud Monitoring Alert Policy
resource "google_monitoring_alert_policy" "unhealthy_backends" {
  display_name = "prod-unhealthy-backends"
  combiner     = "OR"

  conditions {
    display_name = "Backend Service Health"

    condition_threshold {
      filter          = "metric.type=\"compute.googleapis.com/https/backend_request_count\" AND resource.type=\"https_lb_rule\""
      duration        = "300s"
      comparison      = "COMPARISON_LT"
      threshold_value = 1
      aggregations {
        alignment_period  = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = var.notification_channels
}

# Outputs
output "global_ip" {
  description = "Global IP address of the load balancer"
  value       = google_compute_global_address.main.address
}

output "url_map_id" {
  description = "ID of the URL map"
  value       = google_compute_url_map.main_with_host.id
}

output "backend_service_web_id" {
  description = "ID of the web backend service"
  value       = google_compute_backend_service.web.id
}

output "backend_service_api_id" {
  description = "ID of the API backend service"
  value       = google_compute_backend_service.api.id
}

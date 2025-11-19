# Docker Deployment

Deploy the documentation site using Docker containers for easy distribution and management.

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy documentation
COPY docs/ ./docs/
COPY mkdocs.yml .

# Build static site
RUN mkdocs build

# Use nginx to serve
FROM nginx:1.25-alpine
COPY --from=0 /app/site /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

## Docker Compose

```yaml
version: '3.8'

services:
  docs:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:80"
    environment:
      - NGINX_HOST=docs.example.com
      - NGINX_PORT=80
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped
    networks:
      - docs-network

  # Optional: Add a reverse proxy
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-proxy.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - docs
    restart: unless-stopped
    networks:
      - docs-network

networks:
  docs-network:
    driver: bridge
```

## Build and Run

```bash
# Build the Docker image
docker build -t project-docs:latest .

# Run the container
docker run -p 8000:80 project-docs:latest

# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f docs

# Stop services
docker-compose down
```

## Multi-Stage Build

The Dockerfile uses multi-stage builds to:
1. Build the MkDocs site in a Python environment
2. Serve it with Nginx (smaller final image)

## Environment Variables

```bash
NGINX_HOST=docs.example.com
NGINX_PORT=80
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name docs.example.com;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
}
```

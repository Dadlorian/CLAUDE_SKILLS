# Deployment Guide for All Platforms

Complete deployment instructions for Docusaurus, MkDocs, Hugo, and VitePress.

## Quick Reference

| Platform | GitHub Pages | Docker | Vercel | Netlify |
|----------|---------|--------|--------|---------|
| Docusaurus | ✓ | ✓ | ✓ | ✓ |
| MkDocs | ✓ | ✓ | ✓ | ✓ |
| Hugo | ✓ | ✓ | ✓ | ✓ |
| VitePress | ✓ | ✓ | ✓ | ✓ |

## GitHub Pages

### Docusaurus

```bash
npm run deploy
```

Or manually:

```bash
npm run build
git add -A
git commit -m "docs: update"
git push
```

### MkDocs

```bash
mkdocs gh-deploy
```

### Hugo

```bash
hugo -D --baseURL https://username.github.io/project/
cd public
git subtree push --prefix public origin gh-pages
```

### VitePress

```bash
npm run docs:build
# Commit and push to gh-pages branch
```

## Docker Deployment

### Build Image

```bash
docker build -t docs:latest .
```

### Run Container

```bash
docker run -p 80:80 -d docs:latest
```

### Push to Registry

```bash
docker tag docs:latest username/docs:latest
docker push username/docs:latest
```

## Docker Compose

All platforms include `docker-compose.yml`:

```bash
docker-compose up -d
docker-compose down
docker-compose logs -f
```

## Kubernetes Deployment

### Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docs
spec:
  replicas: 2
  selector:
    matchLabels:
      app: docs
  template:
    metadata:
      labels:
        app: docs
    spec:
      containers:
      - name: docs
        image: username/docs:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
```

### Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: docs-service
spec:
  selector:
    app: docs
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## Vercel

### 1. Connect Repository

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your repository
4. Configure project

### 2. Configure Build

**Docusaurus**
- Build Command: `npm run build`
- Output Directory: `build`

**MkDocs**
- Build Command: `mkdocs build`
- Output Directory: `site`

**Hugo**
- Build Command: `hugo --minify`
- Output Directory: `public`

**VitePress**
- Build Command: `npm run docs:build`
- Output Directory: `docs/.vitepress/dist`

### 3. Deploy

```bash
vercel --prod
```

## Netlify

### 1. Connect Repository

1. Go to [netlify.com](https://netlify.com)
2. Click "New site from Git"
3. Select your repository

### 2. Configure Build

Create `netlify.toml`:

**Docusaurus**
```toml
[build]
  command = "npm run build"
  publish = "build"

[build.environment]
  NODE_VERSION = "18"
```

**MkDocs**
```toml
[build]
  command = "mkdocs build"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.11"
```

**Hugo**
```toml
[build]
  command = "hugo --minify"
  publish = "public"

[build.environment]
  HUGO_VERSION = "0.121.0"
```

**VitePress**
```toml
[build]
  command = "npm run docs:build"
  publish = "docs/.vitepress/dist"

[build.environment]
  NODE_VERSION = "18"
```

### 3. Deploy

```bash
netlify deploy --prod
```

## CloudFlare Pages

### 1. Connect Repository

1. Go to [pages.cloudflare.com](https://pages.cloudflare.com)
2. Create new site
3. Connect Git repository

### 2. Configure

**Docusaurus**
- Build: `npm run build`
- Output: `build`

**MkDocs**
- Build: `mkdocs build`
- Output: `site`

**Hugo**
- Build: `hugo --minify`
- Output: `public`

**VitePress**
- Build: `npm run docs:build`
- Output: `docs/.vitepress/dist`

## AWS S3 + CloudFront

### Build and Upload

```bash
# Build
npm run build  # or appropriate command

# Create S3 bucket
aws s3 mb s3://docs-bucket

# Upload files
aws s3 sync build/ s3://docs-bucket/

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name docs-bucket.s3.amazonaws.com \
  --default-root-object index.html
```

## GitHub Actions CI/CD

### Template for All Platforms

```yaml
name: Deploy Docs

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install
        run: npm install

      - name: Build
        run: npm run build

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

## SSL/HTTPS Configuration

### Let's Encrypt (Nginx)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d docs.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name docs.example.com;

    ssl_certificate /etc/letsencrypt/live/docs.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docs.example.com/privkey.pem;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Redirect to HTTPS
    error_page 497 https://$server_name$request_uri;
}
```

## Monitoring & Logging

### Application Monitoring

```bash
# Check logs
docker logs container-name

# Monitor performance
docker stats container-name

# Health checks
curl https://docs.example.com/health
```

### Log Aggregation

Configure in deployment:

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```

## Performance Optimization

### CDN Configuration

```nginx
# Enable caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### Image Optimization

```bash
# Hugo - Image processing
{{- $image.Resize "800x600 webp" -}}

# Docusaurus - Ideal Image plugin
plugins: ['@docusaurus/plugin-ideal-image']

# MkDocs - Image compression via plugins
mkdocs-image-optimization

# VitePress - Vite image optimization
```

## Rollback Procedures

### GitHub Pages

```bash
git revert <commit-hash>
git push
```

### Docker

```bash
docker pull username/docs:previous-tag
docker run -p 80:80 username/docs:previous-tag
```

### Vercel/Netlify

1. Go to deployment history
2. Click "Promote to Production" on previous version

## Cost Analysis

| Platform | Setup | Monthly | Year |
|----------|-------|---------|------|
| GitHub Pages | Free | Free | Free |
| Docker + VPS | $0 | $5-20 | $60-240 |
| Vercel | Free | Free | Free |
| Netlify | Free | Free | Free |
| CloudFlare | Free | Free | Free |
| AWS S3+CF | Free | $1-5 | $12-60 |

## Recommended Setup

**For Teams:**
- GitHub Pages for quick setup
- Vercel/Netlify for advanced features
- Docker for custom deployments

**For Production:**
- CloudFlare Pages (best free option)
- AWS S3 + CloudFront (scalable)
- Kubernetes (enterprise)

**For Enterprise:**
- Kubernetes with monitoring
- Multi-region deployment
- CDN integration
- Custom authentication

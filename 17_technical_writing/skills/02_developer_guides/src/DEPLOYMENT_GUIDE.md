# Complete Deployment Guide

Production-ready deployment instructions for all three projects.

## Table of Contents

1. [Complete API Integration Tutorial](#complete-api-integration-tutorial)
2. [Framework Integration Examples](#framework-integration-examples)
3. [Interactive Playground](#interactive-playground)
4. [Common Deployment Platforms](#common-deployment-platforms)
5. [Monitoring & Logging](#monitoring--logging)

---

## Complete API Integration Tutorial

### Prerequisites

- Node.js 16+
- npm or yarn
- Docker (optional, for containerization)
- Vercel account (optional, for Vercel deployment)

### Local Development

```bash
cd complete-api-integration-tutorial

# Install dependencies
npm install

# Start development server
npm run dev              # Frontend on http://localhost:3000

# In another terminal
npm run server           # API server on http://localhost:3001

# Run tests
npm test
npm run test:coverage
```

### Production Build

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview

# The dist/ folder is ready to deploy
```

### Docker Deployment

#### Using Docker Compose (Recommended)

```bash
# Build and run both frontend and API server
docker-compose up

# Background
docker-compose up -d

# Stop services
docker-compose down
```

**docker-compose.yml Configuration:**
- Frontend service on port 3000
- API service on port 3001
- Auto-restart on failure
- Volume mounts for development

#### Using Docker CLI

```bash
# Build image
docker build -t api-tutorial:latest .

# Run container
docker run -p 3000:3000 \
  -e VITE_API_URL=http://api:3001/api \
  api-tutorial:latest

# With custom API URL
docker run -p 3000:3000 \
  -e VITE_API_URL=https://api.example.com/api \
  api-tutorial:latest
```

#### Environment Variables for Docker

Create `.env` file:
```
VITE_API_URL=https://api.production.com/api
NODE_ENV=production
```

### Vercel Deployment

Vercel is the recommended platform (created by Next.js team).

#### Option 1: Git Integration (Recommended)

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Select your repository
5. Configure:
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variables:
     - `VITE_API_URL`: Your production API URL

#### Option 2: CLI Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

#### Vercel Configuration (vercel.json)

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "@api_url"
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "destination": "http://api-backend.com/api/$1"
    },
    {
      "src": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### AWS Deployment

#### Using S3 + CloudFront

```bash
# Build the app
npm run build

# Configure AWS credentials
aws configure

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name/

# Create CloudFront distribution for caching
```

#### Using AWS Amplify

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize
amplify init

# Deploy
amplify publish
```

### Netlify Deployment

#### Using Git Integration

1. Push to GitHub
2. Go to [netlify.com](https://netlify.com)
3. Click "New site from Git"
4. Select repository
5. Configure:
   - Build Command: `npm run build`
   - Publish Directory: `dist`
   - Environment: Add VITE_API_URL

#### Using Netlify CLI

```bash
# Install CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

### Environment Configuration

#### Development (.env.local)
```
VITE_API_URL=http://localhost:3001/api
```

#### Production (.env.production)
```
VITE_API_URL=https://api.production.com/api
```

#### Staging (.env.staging)
```
VITE_API_URL=https://api.staging.com/api
```

### Production Checklist

- [ ] Set appropriate API URL for environment
- [ ] Enable HTTPS
- [ ] Configure CORS headers
- [ ] Set security headers
- [ ] Enable compression
- [ ] Configure caching headers
- [ ] Set up error logging
- [ ] Configure monitoring
- [ ] Test error boundaries
- [ ] Verify form submissions
- [ ] Check performance metrics

---

## Framework Integration Examples

### Next.js Example

#### Development

```bash
cd framework-integration-examples/nextjs
npm install
npm run dev
```

#### Production Build

```bash
npm run build
npm run start
```

#### Vercel Deployment (Recommended for Next.js)

```bash
# Automatic deployment from GitHub
# or
npm install -g vercel
vercel deploy --prod
```

#### Docker Deployment

```bash
# Create Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Build and run
docker build -t nextjs-app .
docker run -p 3000:3000 nextjs-app
```

### Vue Example

#### Development

```bash
cd framework-integration-examples/vue
npm install
npm run dev
```

#### Production Build

```bash
npm run build
# dist/ folder is ready to deploy
```

#### Deployment Options

```bash
# Vercel
vercel deploy --prod

# Netlify
netlify deploy --prod --dir=dist

# GitHub Pages
npm run build
# Configure GitHub Pages to serve /dist
```

### Angular Example

#### Development

```bash
cd framework-integration-examples/angular
npm install
npm start
```

#### Production Build

```bash
npm run build
# dist/angular-api-integration/ is ready to deploy
```

#### Deployment

```bash
# Vercel
vercel deploy --prod

# Netlify
netlify deploy --prod --dir=dist/angular-api-integration

# Cloud Run (Google Cloud)
gcloud run deploy --source .
```

---

## Interactive Playground

### Development

```bash
cd interactive-playground
npm install
npm run dev
```

### Production Build

```bash
npm run build
# dist/ is ready to deploy
```

### Deployment Platforms

#### Vercel (Recommended)

```bash
vercel deploy --prod
```

#### Netlify

```bash
netlify deploy --prod --dir=dist
```

#### GitHub Pages

```bash
# Add to package.json:
"homepage": "https://username.github.io/repo-name"

# Deploy
npm run build
npm run deploy
```

#### Static Hosting (Any CDN)

```bash
# Build the app
npm run build

# Upload dist/ to your CDN
# Examples: CloudFlare Pages, Surge.sh, Firebase Hosting
```

---

## Common Deployment Platforms

### Vercel (Recommended)

**Pros:**
- Optimized for React/Next.js
- Zero-config deployment
- Automatic previews for PRs
- Excellent performance
- Free tier available

**Deploy:**
```bash
npm install -g vercel
vercel deploy --prod
```

### Netlify

**Pros:**
- Easy Git integration
- Built-in CI/CD
- Serverless functions support
- Free SSL
- Good free tier

**Deploy:**
```bash
netlify deploy --prod --dir=dist
```

### AWS

**Options:**
1. **S3 + CloudFront** - Static hosting with CDN
2. **Amplify** - Full-stack hosting
3. **Elastic Beanstalk** - Managed platform
4. **EC2** - Virtual servers

```bash
# Example: S3 + CloudFront
aws s3 sync dist/ s3://bucket-name/
aws cloudfront create-invalidation --distribution-id ID --paths "/*"
```

### Google Cloud

**Options:**
1. **Cloud Run** - Containerized apps
2. **Firebase Hosting** - Static hosting
3. **App Engine** - Managed platform

```bash
# Firebase Hosting
npm install -g firebase-tools
firebase deploy --only hosting

# Cloud Run
gcloud run deploy app --source .
```

### DigitalOcean

**Options:**
1. **App Platform** - Managed platform
2. **Droplets** - Virtual machines
3. **Spaces** - Object storage

```bash
# Using App Platform (via dashboard)
# Connect GitHub repo and configure
```

### Heroku (Free tier deprecated)

**Alternative:** Use Railway, Render, or Fly.io

```bash
# Railway
npm install -g railway
railway up

# Render
# Connect GitHub repo via dashboard
```

---

## Performance Optimization

### Pre-deployment Checklist

1. **Code Optimization**
   ```bash
   # Minify and bundle
   npm run build

   # Check bundle size
   npm run build:analyze
   ```

2. **Image Optimization**
   - Use appropriate image formats (WebP)
   - Compress images
   - Use CDN for image delivery

3. **Caching Strategy**
   - Set cache headers for assets
   - Use service workers
   - Implement cache busting

4. **Compression**
   - Enable gzip compression
   - Use brotli for modern browsers
   - Minify CSS and JavaScript

5. **Performance Monitoring**
   ```javascript
   // Add performance monitoring
   if ('PerformanceObserver' in window) {
     const observer = new PerformanceObserver((list) => {
       list.getEntries().forEach(entry => {
         console.log(`${entry.name}: ${entry.duration}ms`)
       })
     })
     observer.observe({ entryTypes: ['measure'] })
   }
   ```

---

## Monitoring & Logging

### Error Tracking

```javascript
// Sentry integration
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: "https://key@sentry.io/project",
  environment: "production",
  tracesSampleRate: 1.0,
})

// Automatic error reporting
```

### Performance Monitoring

```javascript
// Google Analytics
gtag('event', 'api_call', {
  method: 'GET',
  endpoint: '/api/users',
  duration: 234
})

// Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log)
getFID(console.log)
getFCP(console.log)
getLCP(console.log)
getTTFB(console.log)
```

### Server Logging

```javascript
// Express server logging
import morgan from 'morgan'

app.use(morgan('combined'))

app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).json({ error: 'Internal Server Error' })
})
```

### Database Monitoring

- Monitor query performance
- Track connection pool usage
- Alert on slow queries
- Regular backups

### Health Checks

```javascript
// Add health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date(),
    uptime: process.uptime()
  })
})

// Ping endpoint for monitoring
setInterval(() => {
  fetch('/api/health').catch(err => {
    console.error('Health check failed:', err)
    // Alert ops team
  })
}, 60000)
```

---

## Security Checklist

- [ ] HTTPS enabled
- [ ] Security headers set (CSP, X-Frame-Options, etc.)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on server
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF tokens
- [ ] Environment variables not exposed
- [ ] Dependencies up to date
- [ ] No hardcoded credentials
- [ ] Secure headers configured

---

## Troubleshooting Deployment

### 404 Errors on Refresh

**Solution:** Configure server to serve index.html for all routes

```javascript
// Express
app.get('/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/index.html'))
})

// Nginx
location / {
  try_files $uri /index.html;
}
```

### API CORS Errors

**Solution:** Configure CORS on backend

```javascript
import cors from 'cors'

app.use(cors({
  origin: process.env.FRONTEND_URL,
  credentials: true
}))
```

### Slow Performance

**Solutions:**
1. Enable compression
2. Use CDN
3. Optimize images
4. Implement caching
5. Code splitting
6. Lazy loading

### Environment Variables Not Working

**Solution:** Ensure prefix for client-side vars

```
# React/Vue/Angular (client-side)
VITE_API_URL=...
REACT_APP_API_URL=...
NG_APP_API_URL=...

# Next.js (can use without prefix on server)
NEXT_PUBLIC_API_URL=...
```

---

## Additional Resources

- [Vercel Deployment Docs](https://vercel.com/docs)
- [Netlify Deployment Docs](https://docs.netlify.com)
- [AWS Deployment Docs](https://aws.amazon.com/getting-started)
- [Docker Docs](https://docs.docker.com)
- [PM2 Process Manager](https://pm2.keymetrics.io)
- [Nginx Web Server](https://nginx.org)
- [Let's Encrypt SSL](https://letsencrypt.org)

---

## Getting Help

1. Check error logs
2. Review deployment platform documentation
3. Verify environment variables
4. Test locally in production mode
5. Check monitoring dashboards
6. Review security settings

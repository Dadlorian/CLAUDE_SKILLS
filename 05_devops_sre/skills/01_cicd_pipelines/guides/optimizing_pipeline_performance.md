# Optimizing CI/CD Pipeline Performance

## Introduction

Slow pipelines reduce developer productivity and delay deployments. This guide covers techniques to make your CI/CD pipelines faster, more efficient, and cost-effective.

## Table of Contents
- [Measuring Performance](#measuring-performance)
- [Caching Strategies](#caching-strategies)
- [Parallel Execution](#parallel-execution)
- [Artifact Management](#artifact-management)
- [Docker Optimization](#docker-optimization)
- [Resource Optimization](#resource-optimization)
- [Smart Testing](#smart-testing)
- [Network Optimization](#network-optimization)

## Measuring Performance

Before optimizing, measure your current performance.

### Key Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Total pipeline time** | < 10 min | Developer feedback loop |
| **Time to first feedback** | < 2 min | Fail fast principle |
| **Cache hit rate** | > 80% | Efficiency indicator |
| **Parallel job utilization** | > 70% | Resource efficiency |
| **Artifact size** | Minimal | Storage & transfer costs |

### GitHub Actions - View Metrics

```yaml
name: Pipeline Metrics

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start timer
        run: echo "START_TIME=$(date +%s)" >> $GITHUB_ENV

      - name: Build
        run: npm run build

      - name: Calculate duration
        run: |
          END_TIME=$(date +%s)
          DURATION=$((END_TIME - START_TIME))
          echo "Build took $DURATION seconds" >> $GITHUB_STEP_SUMMARY
```

### GitLab CI - Pipeline Analytics

GitLab provides built-in analytics at: Analytics → CI/CD Analytics

### Jenkins - Build Time Trend Plugin

Install "Build Time Trend" plugin to track performance over time.

## Caching Strategies

Caching is the most impactful optimization.

### 1. Package Manager Caching

#### GitHub Actions - Built-in Caching

```yaml
# Node.js with npm
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'  # Automatic caching

# Python with pip
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

# Java with Maven
- uses: actions/setup-java@v4
  with:
    java-version: '17'
    distribution: 'temurin'
    cache: 'maven'
```

#### GitHub Actions - Manual Caching

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      ~/.cache
      node_modules
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

#### GitLab CI - Efficient Caching

```yaml
variables:
  # Enable fast compression
  FF_USE_FASTZIP: "true"
  CACHE_COMPRESSION_LEVEL: "fast"

cache:
  key:
    files:
      - package-lock.json  # Cache key based on lockfile
  paths:
    - node_modules/
  policy: pull-push  # Default

install:
  script:
    - npm ci
  cache:
    policy: push  # Only upload cache

test:
  script:
    - npm test
  cache:
    policy: pull  # Only download cache
```

#### Jenkins - Cache Plugin

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                cache(maxCacheSize: 250, caches: [
                    arbitraryFileCache(
                        path: 'node_modules',
                        cacheValidityDecidingFile: 'package-lock.json'
                    )
                ]) {
                    sh 'npm ci'
                    sh 'npm run build'
                }
            }
        }
    }
}
```

### 2. Multi-Layer Caching

```yaml
# GitHub Actions - Layer your caches
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Layer 1: Global dependencies
      - uses: actions/cache@v4
        with:
          path: ~/.npm
          key: ${{ runner.os }}-npm-global-${{ hashFiles('package-lock.json') }}

      # Layer 2: Project dependencies
      - uses: actions/cache@v4
        with:
          path: node_modules
          key: ${{ runner.os }}-node-modules-${{ hashFiles('package-lock.json') }}

      # Layer 3: Build artifacts
      - uses: actions/cache@v4
        with:
          path: .next/cache
          key: ${{ runner.os }}-nextjs-${{ hashFiles('**.[jt]s', '**.[jt]sx') }}

      - run: npm ci
      - run: npm run build
```

### 3. Distributed Caching

#### GitLab CI - S3 Cache

```toml
# GitLab Runner config.toml
[[runners]]
  [runners.cache]
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "us-east-1"
```

## Parallel Execution

Run independent jobs concurrently.

### 1. Parallel Jobs

#### GitHub Actions

```yaml
jobs:
  test:
    strategy:
      matrix:
        test-suite: [unit, integration, e2e]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --suite=${{ matrix.test-suite }}

# Before: 15 minutes (sequential)
# After: 5 minutes (parallel)
```

#### GitLab CI

```yaml
test:
  parallel: 5
  script:
    - npm test -- --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
```

### 2. Split Tests Intelligently

```yaml
# GitHub Actions - Jest with sharding
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --shard=${{ matrix.shard }}/4
```

### 3. Pipeline Stages with Dependencies

```yaml
# GitHub Actions - Use needs strategically
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build

  # These run in parallel after build
  unit-test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:unit

  integration-test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:integration

  lint:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint

  # This waits for all tests
  deploy:
    needs: [unit-test, integration-test, lint]
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
```

## Artifact Management

Minimize artifact size and transfer time.

### 1. Selective Artifact Upload

```yaml
# Bad - Upload everything
- uses: actions/upload-artifact@v4
  with:
    name: all-files
    path: .  # DON'T DO THIS

# Good - Upload only what's needed
- uses: actions/upload-artifact@v4
  with:
    name: production-build
    path: |
      dist/
      !dist/**/*.map  # Exclude source maps
      !dist/**/*.md   # Exclude docs
```

### 2. Artifact Compression

```yaml
# GitLab CI - Fast compression
variables:
  FF_USE_FASTZIP: "true"
  ARTIFACT_COMPRESSION_LEVEL: "fast"  # fast, default, slow

artifacts:
  paths:
    - dist/
  expire_in: 1 day  # Auto-cleanup
```

### 3. Avoid Unnecessary Artifact Downloads

```yaml
# GitLab CI - Selective dependencies
test:
  dependencies:
    - build  # Only download from build job

deploy:
  dependencies: []  # Don't download any artifacts
  script:
    - aws s3 sync s3://bucket/artifacts ./dist
    - ./deploy.sh
```

```yaml
# GitHub Actions - Skip artifact in some jobs
jobs:
  build:
    steps:
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  test:
    needs: build
    steps:
      # Don't download artifact, test source instead
      - uses: actions/checkout@v4
      - run: npm test

  deploy:
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
      - run: ./deploy.sh
```

## Docker Optimization

Docker operations can be slow. Optimize them.

### 1. Multi-Stage Builds

```dockerfile
# Bad - Single stage (slow)
FROM node:18
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run build
CMD ["npm", "start"]

# Good - Multi-stage (fast)
# Stage 1: Build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --only=production
CMD ["node", "dist/index.js"]
```

### 2. Layer Caching

```dockerfile
# Bad - Invalidates cache on any file change
FROM node:18
WORKDIR /app
COPY . .
RUN npm ci

# Good - Leverage layer caching
FROM node:18
WORKDIR /app

# Copy package files first (changes less frequently)
COPY package*.json ./
RUN npm ci

# Copy source code last (changes most frequently)
COPY . .
RUN npm run build
```

### 3. Build Cache

```yaml
# GitHub Actions - Docker buildx with cache
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myapp:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

```yaml
# GitLab CI - Docker layer caching
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_DRIVER: overlay2
    DOCKER_BUILDKIT: 1
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker pull $CI_REGISTRY_IMAGE:latest || true
    - docker build --cache-from $CI_REGISTRY_IMAGE:latest -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### 4. Use Smaller Base Images

```dockerfile
# Bad - Large image (1.1 GB)
FROM node:18

# Better - Slim variant (300 MB)
FROM node:18-slim

# Best - Alpine variant (180 MB)
FROM node:18-alpine
```

### 5. .dockerignore

```
# .dockerignore
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.vscode
.idea
dist
coverage
*.log
```

## Resource Optimization

### 1. Choose Right Runner Size

```yaml
# GitHub Actions - Use appropriate runners
jobs:
  small-job:
    runs-on: ubuntu-latest  # 2 CPU, 7 GB RAM (free)

  large-job:
    runs-on: ubuntu-latest-8-cores  # 8 CPU, 32 GB RAM (paid)

  # Use self-hosted for better control
  custom-job:
    runs-on: self-hosted
```

### 2. Resource Limits (GitLab)

```yaml
job:
  tags:
    - docker
  variables:
    KUBERNETES_CPU_REQUEST: "1"
    KUBERNETES_CPU_LIMIT: "2"
    KUBERNETES_MEMORY_REQUEST: "1Gi"
    KUBERNETES_MEMORY_LIMIT: "2Gi"
```

### 3. Concurrency Control

```yaml
# GitHub Actions - Limit concurrent builds
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel outdated builds

# GitLab CI
workflow:
  auto_cancel:
    on_new_commit: interruptible
    on_job_failure: none
```

## Smart Testing

Run only necessary tests.

### 1. Changed Files Detection

```yaml
# GitHub Actions - Test only changed code
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            backend:
              - 'backend/**'
            frontend:
              - 'frontend/**'

  test-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: npm test -- backend/

  test-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: npm test -- frontend/
```

### 2. Test Impact Analysis

```bash
# Jest - Run only affected tests
npm test -- --onlyChanged --changedSince=origin/main
```

### 3. Fail Fast

```yaml
# GitHub Actions
strategy:
  fail-fast: true  # Stop all jobs if one fails
  matrix:
    test-suite: [unit, integration, e2e]

# GitLab CI
test:
  parallel: 5
  script:
    - npm test || exit 1  # Fail immediately
```

### 4. Test Prioritization

```yaml
# Run fast tests first
jobs:
  quick-tests:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:unit  # 2 minutes

  slow-tests:
    needs: quick-tests  # Only run if quick tests pass
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:e2e  # 15 minutes
```

## Network Optimization

### 1. Shallow Clones

```yaml
# GitHub Actions - Shallow clone
- uses: actions/checkout@v4
  with:
    fetch-depth: 1  # Only latest commit

# For operations needing history
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full history
```

```yaml
# GitLab CI
variables:
  GIT_DEPTH: 1  # Shallow clone
  GIT_STRATEGY: fetch  # fetch (default), clone, or none
```

### 2. Use Mirrors/Proxies

```yaml
# npm registry mirror
- name: Use npm mirror
  run: |
    npm config set registry https://registry.npmmirror.com
    npm ci
```

### 3. Parallel Downloads

```bash
# npm - parallel package downloads
npm ci --prefer-offline --no-audit --progress=false
```

## Advanced Optimization Techniques

### 1. Incremental Builds

```yaml
# Next.js - Cache build output
- uses: actions/cache@v4
  with:
    path: ${{ github.workspace }}/.next/cache
    key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('**.[jt]s', '**.[jt]sx') }}

- run: npm run build  # Reuses cached builds
```

### 2. Pre-built Docker Images

```yaml
# Instead of installing tools every time
FROM node:18
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++

# Publish as your base image
# Then use in pipeline
FROM myorg/node-build-base:latest
COPY . .
RUN npm ci && npm run build
```

### 3. Workspace Splitting (Monorepo)

```yaml
# Only build changed workspaces
- name: Build changed packages
  run: |
    npx lerna run build --since origin/main --include-dependencies
```

### 4. Remote Caching (Turborepo, Nx)

```yaml
# Turborepo with remote caching
- name: Build with Turborepo
  env:
    TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
    TURBO_TEAM: ${{ secrets.TURBO_TEAM }}
  run: npx turbo run build --cache-dir=.turbo
```

## Monitoring & Continuous Improvement

### 1. Track Pipeline Duration

```yaml
# GitHub Actions - Export metrics
- name: Export metrics
  if: always()
  run: |
    echo "pipeline_duration_seconds{job=\"${{ github.job }}\"} $SECONDS" > metrics.txt

- uses: actions/upload-artifact@v4
  with:
    name: metrics
    path: metrics.txt
```

### 2. Set Performance Budgets

```yaml
# Fail if pipeline takes too long
- name: Check duration
  run: |
    if [ $SECONDS -gt 600 ]; then
      echo "Pipeline exceeded 10-minute budget!"
      exit 1
    fi
```

### 3. Regular Performance Reviews

Schedule monthly reviews:
- Analyze slowest pipelines
- Check cache hit rates
- Review artifact sizes
- Identify bottlenecks

## Before & After Examples

### Example 1: Node.js Application

**Before (12 minutes):**
```yaml
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install  # 3 min
      - run: npm run lint  # 1 min
      - run: npm test  # 5 min
      - run: npm run build  # 3 min
```

**After (4 minutes):**
```yaml
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci  # 30 sec (cached)

  lint:
    needs: install
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci  # 10 sec (cached)
      - run: npm run lint  # 1 min

  test:
    needs: install
    strategy:
      matrix:
        shard: [1, 2, 3]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci  # 10 sec (cached)
      - run: npm test -- --shard=${{ matrix.shard }}/3  # 2 min parallel

  build:
    needs: install
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci  # 10 sec (cached)
      - run: npm run build  # 2 min (cached build artifacts)
```

**Optimizations:**
- Caching: 3 min → 30 sec install
- Parallel tests: 5 min → 2 min
- Total: 12 min → 4 min (67% faster)

## Quick Wins Checklist

- [ ] Enable package manager caching
- [ ] Use shallow git clones (fetch-depth: 1)
- [ ] Run independent jobs in parallel
- [ ] Optimize Docker layer caching
- [ ] Use smaller Docker base images
- [ ] Add .dockerignore
- [ ] Set artifact expiration
- [ ] Only upload necessary artifacts
- [ ] Cancel outdated builds (concurrency control)
- [ ] Split large test suites
- [ ] Use fail-fast for quick feedback
- [ ] Monitor and measure performance
- [ ] Review and optimize monthly

## Resources

- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices-for-github-actions)
- [GitLab CI/CD Best Practices](https://docs.gitlab.com/ee/ci/pipelines/pipeline_efficiency.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Turborepo Remote Caching](https://turbo.build/repo/docs/core-concepts/remote-caching)

## Conclusion

Pipeline optimization is an ongoing process. Start with quick wins (caching, parallelization), measure the impact, and iterate. A faster pipeline means:

- Happier developers
- Faster time to production
- Lower infrastructure costs
- Better overall productivity

Remember: **Measure, optimize, measure again.**

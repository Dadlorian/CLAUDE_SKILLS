# GitHub Actions Reference

## Table of Contents
- [Workflow Basics](#workflow-basics)
- [Workflow Syntax](#workflow-syntax)
- [Events & Triggers](#events--triggers)
- [Jobs](#jobs)
- [Steps](#steps)
- [Contexts & Expressions](#contexts--expressions)
- [Environment Variables](#environment-variables)
- [Secrets & Security](#secrets--security)
- [Marketplace Actions](#marketplace-actions)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Workflow Basics

### File Location
```
.github/workflows/
├── ci.yml
├── deploy.yml
└── release.yml
```

### Basic Workflow Structure
```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run build
        run: npm run build
```

## Workflow Syntax

### name
Workflow name (displayed in GitHub UI).

```yaml
name: CI/CD Pipeline
```

### on (Events)
Define when workflow runs.

```yaml
# Single event
on: push

# Multiple events
on: [push, pull_request]

# Event with configuration
on:
  push:
    branches:
      - main
      - 'releases/**'
    tags:
      - v*
    paths:
      - 'src/**'
      - '!src/docs/**'

  pull_request:
    branches:
      - main
    types:
      - opened
      - synchronize
      - reopened

  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

  workflow_dispatch:  # Manual trigger
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

  repository_dispatch:  # External trigger
    types: [custom-event]
```

### env
Global environment variables.

```yaml
env:
  NODE_VERSION: '16'
  DEPLOY_ENV: production
  API_URL: https://api.example.com
```

### defaults
Default settings for all jobs.

```yaml
defaults:
  run:
    shell: bash
    working-directory: ./src
```

### concurrency
Control concurrent workflow runs.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel previous runs
```

### permissions
Set GITHUB_TOKEN permissions.

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
  packages: write
```

## Events & Triggers

### Push Event
```yaml
on:
  push:
    branches:
      - main
      - 'feature/**'
      - '!experimental'  # Exclude branches
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'  # Semantic version tags
    paths:
      - 'src/**'
      - 'tests/**'
      - '!**.md'  # Exclude markdown files
    paths-ignore:
      - 'docs/**'
```

### Pull Request Event
```yaml
on:
  pull_request:
    types:
      - opened
      - synchronize  # New commits pushed
      - reopened
      - ready_for_review
      - labeled
    branches:
      - main
    paths:
      - 'src/**'
```

### Schedule Event
```yaml
on:
  schedule:
    # Cron syntax: minute hour day month weekday
    - cron: '30 5 * * 1,3'  # 5:30 AM UTC on Monday & Wednesday
    - cron: '0 0 * * *'     # Daily at midnight UTC
    - cron: '0 */6 * * *'   # Every 6 hours
```

### Workflow Dispatch (Manual)
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - production
      version:
        description: 'Version to deploy'
        required: false
        type: string
      debug:
        description: 'Enable debug mode'
        required: false
        type: boolean
        default: false
```

### Workflow Call (Reusable)
```yaml
on:
  workflow_call:
    inputs:
      config-path:
        required: true
        type: string
    secrets:
      token:
        required: true
    outputs:
      build-id:
        description: 'Build ID'
        value: ${{ jobs.build.outputs.build-id }}
```

### Other Events
```yaml
on:
  # Repository events
  issues:
    types: [opened, labeled]

  issue_comment:
    types: [created]

  release:
    types: [published]

  # Workflow events
  workflow_run:
    workflows: [Build]
    types: [completed]

  # Registry events
  registry_package:
    types: [published]

  # Branch protection
  check_run:
    types: [rerequested, requested_action]
```

## Jobs

### Basic Job Structure
```yaml
jobs:
  job-name:
    # Runner type (required)
    runs-on: ubuntu-latest

    # Job name (displayed in UI)
    name: Build Application

    # Dependencies
    needs: [previous-job]

    # Conditional execution
    if: github.event_name == 'push'

    # Permissions for this job
    permissions:
      contents: read

    # Environment
    environment:
      name: production
      url: https://prod.example.com

    # Timeout (default: 360 minutes)
    timeout-minutes: 30

    # Concurrency control
    concurrency:
      group: deploy-${{ github.ref }}
      cancel-in-progress: false

    # Environment variables
    env:
      JOB_VAR: value

    # Default settings
    defaults:
      run:
        shell: bash

    # Strategy (matrix/fail-fast)
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [14, 16, 18]
      fail-fast: false

    # Steps to execute
    steps:
      - uses: actions/checkout@v4
      - run: npm install

    # Outputs
    outputs:
      build-id: ${{ steps.build.outputs.id }}

    # Container to run job in
    container:
      image: node:16
      env:
        NODE_ENV: production
      volumes:
        - my-volume:/volume
      options: --cpus 2
```

### runs-on
Specify runner type.

```yaml
# GitHub-hosted runners
runs-on: ubuntu-latest        # Ubuntu (most common)
runs-on: ubuntu-22.04         # Specific Ubuntu version
runs-on: windows-latest       # Windows
runs-on: macos-latest         # macOS
runs-on: macos-13             # Specific macOS version

# Self-hosted runner
runs-on: self-hosted

# Runner with labels
runs-on: [self-hosted, linux, x64, gpu]

# Matrix strategy
runs-on: ${{ matrix.os }}
```

### needs
Define job dependencies.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build

  test:
    needs: build  # Runs after build
    runs-on: ubuntu-latest
    steps:
      - run: npm test

  deploy:
    needs: [build, test]  # Runs after both
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
```

### strategy.matrix
Run job with multiple configurations.

```yaml
jobs:
  test:
    strategy:
      matrix:
        # Simple matrix
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [14, 16, 18]

        # Include specific combinations
        include:
          - os: ubuntu-latest
            node: 20
            experimental: true

        # Exclude combinations
        exclude:
          - os: macos-latest
            node: 14

      # Don't cancel all jobs if one fails
      fail-fast: false

      # Maximum parallel jobs
      max-parallel: 2

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

### container
Run job in a Docker container.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: node:16-alpine
      env:
        NODE_ENV: test
      ports:
        - 3000:3000
      volumes:
        - my-docker-volume:/volume
      options: --cpus 2 --memory 4g

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - run: npm test
```

### environment
Deployment environment with protection rules.

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://prod.example.com

    steps:
      - run: ./deploy.sh

  # Dynamic environment
  deploy-review:
    environment:
      name: review-pr-${{ github.event.number }}
      url: https://pr-${{ github.event.number }}.example.com

    steps:
      - run: ./deploy-review.sh
```

### outputs
Pass data between jobs.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.set-version.outputs.version }}
      build-id: ${{ steps.build.outputs.id }}

    steps:
      - id: set-version
        run: echo "version=1.0.0" >> $GITHUB_OUTPUT

      - id: build
        run: |
          BUILD_ID=$(date +%s)
          echo "id=$BUILD_ID" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Deploying version ${{ needs.build.outputs.version }}"
          echo "Build ID: ${{ needs.build.outputs.build-id }}"
```

## Steps

### Basic Step Types

```yaml
steps:
  # Run shell command
  - run: echo "Hello World"

  # Multi-line command
  - run: |
      echo "Line 1"
      echo "Line 2"

  # Use marketplace action
  - uses: actions/checkout@v4

  # Use action with parameters
  - uses: actions/setup-node@v4
    with:
      node-version: '16'

  # Use local action
  - uses: ./.github/actions/my-action

  # Conditional step
  - if: github.event_name == 'push'
    run: echo "This is a push event"

  # Step with name
  - name: Build application
    run: npm run build

  # Step with environment variables
  - name: Deploy
    env:
      API_KEY: ${{ secrets.API_KEY }}
    run: ./deploy.sh

  # Step with working directory
  - name: Build
    working-directory: ./src
    run: npm run build

  # Step timeout
  - name: Long running task
    timeout-minutes: 10
    run: ./long-task.sh

  # Continue on error
  - name: Optional step
    continue-on-error: true
    run: ./flaky-script.sh

  # Step with ID (for outputs)
  - id: build-step
    run: echo "result=success" >> $GITHUB_OUTPUT
```

### run
Execute shell commands.

```yaml
steps:
  # Simple command
  - run: npm install

  # Multi-line script
  - run: |
      npm install
      npm run build
      npm test

  # Custom shell
  - shell: bash
    run: echo "Using bash"

  - shell: python
    run: |
      import sys
      print(sys.version)

  # Working directory
  - run: npm test
    working-directory: ./backend

  # Environment variables
  - run: echo "API URL: $API_URL"
    env:
      API_URL: https://api.example.com
```

### uses
Use actions from marketplace or local.

```yaml
steps:
  # Specific version (recommended)
  - uses: actions/checkout@v4

  # Specific commit SHA (most secure)
  - uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab

  # Branch (not recommended for security)
  - uses: actions/checkout@main

  # With parameters
  - uses: actions/setup-node@v4
    with:
      node-version: '16'
      cache: 'npm'

  # Local action
  - uses: ./.github/actions/custom-action
    with:
      parameter: value

  # Docker container action
  - uses: docker://alpine:3.8
    with:
      entrypoint: /bin/echo
      args: "Hello World"
```

### Checkout Step
```yaml
steps:
  # Basic checkout
  - uses: actions/checkout@v4

  # Checkout with options
  - uses: actions/checkout@v4
    with:
      # Fetch all history for all branches
      fetch-depth: 0

      # Checkout specific branch
      ref: develop

      # Checkout specific repository
      repository: owner/repo

      # Use PAT for private repos
      token: ${{ secrets.GITHUB_TOKEN }}

      # Checkout submodules
      submodules: recursive

      # LFS support
      lfs: true
```

## Contexts & Expressions

### Contexts
Access information about workflow run.

```yaml
steps:
  - name: Context examples
    run: |
      echo "Event: ${{ github.event_name }}"
      echo "Repository: ${{ github.repository }}"
      echo "Ref: ${{ github.ref }}"
      echo "SHA: ${{ github.sha }}"
      echo "Actor: ${{ github.actor }}"
      echo "Job status: ${{ job.status }}"
      echo "Runner OS: ${{ runner.os }}"
      echo "Secret: ${{ secrets.MY_SECRET }}"
      echo "Input: ${{ inputs.my-input }}"
```

### github Context
```yaml
${{ github.action }}              # Action name
${{ github.actor }}               # User who triggered workflow
${{ github.event_name }}          # Event type (push, pull_request, etc.)
${{ github.job }}                 # Job ID
${{ github.ref }}                 # Branch or tag ref
${{ github.ref_name }}            # Branch or tag name
${{ github.repository }}          # Owner/repo name
${{ github.repository_owner }}    # Repository owner
${{ github.run_id }}              # Unique workflow run ID
${{ github.run_number }}          # Unique run number
${{ github.sha }}                 # Commit SHA
${{ github.workflow }}            # Workflow name
${{ github.workspace }}           # Workspace directory path
```

### env Context
```yaml
${{ env.MY_VARIABLE }}            # Environment variable
```

### job Context
```yaml
${{ job.status }}                 # Job status (success, failure, cancelled)
${{ job.container.id }}           # Container ID
```

### steps Context
```yaml
${{ steps.step-id.outputs.name }} # Step output
${{ steps.step-id.conclusion }}   # Step conclusion
${{ steps.step-id.outcome }}      # Step outcome
```

### runner Context
```yaml
${{ runner.name }}                # Runner name
${{ runner.os }}                  # OS (Linux, Windows, macOS)
${{ runner.arch }}                # Architecture (X64, ARM64)
${{ runner.temp }}                # Temp directory
${{ runner.tool_cache }}          # Tool cache directory
```

### secrets Context
```yaml
${{ secrets.MY_SECRET }}          # Repository/organization secret
```

### inputs Context
```yaml
${{ inputs.my-input }}            # Workflow dispatch input
```

### Expressions
```yaml
# Comparison operators
if: github.ref == 'refs/heads/main'
if: github.event_name != 'pull_request'

# Logical operators
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
if: "!cancelled()"

# Status check functions
if: success()      # Previous steps succeeded
if: failure()      # Previous step failed
if: always()       # Always run
if: cancelled()    # Workflow was cancelled

# Comparison functions
if: contains(github.ref, 'feature/')
if: startsWith(github.ref, 'refs/tags/')
if: endsWith(github.ref, '-beta')

# JSON/Object functions
if: toJSON(github.event)
if: fromJSON('{"name": "value"}')

# Format function
${{ format('Hello {0} {1}', 'World', '!') }}

# Join function
${{ join(matrix.os, '-') }}
```

## Environment Variables

### Setting Environment Variables

```yaml
# Workflow level
env:
  WORKFLOW_VAR: value

jobs:
  job1:
    # Job level
    env:
      JOB_VAR: value

    steps:
      # Step level
      - env:
          STEP_VAR: value
        run: echo $STEP_VAR

      # Set for subsequent steps
      - run: echo "MY_VAR=value" >> $GITHUB_ENV

      # Set output for other jobs
      - id: set-output
        run: echo "output-var=value" >> $GITHUB_OUTPUT

      # Multiline value
      - run: |
          echo "JSON_DATA<<EOF" >> $GITHUB_ENV
          echo '{"key": "value"}' >> $GITHUB_ENV
          echo "EOF" >> $GITHUB_ENV
```

### Default Environment Variables

```yaml
# GitHub environment variables
GITHUB_ACTION          # Action name
GITHUB_ACTOR           # Username of person/app that triggered
GITHUB_REF             # Branch or tag ref
GITHUB_REPOSITORY      # Owner/repo
GITHUB_SHA             # Commit SHA
GITHUB_WORKSPACE       # Workspace directory
GITHUB_TOKEN           # Automatically provided token

# Runner environment variables
RUNNER_OS              # OS (Linux, Windows, macOS)
RUNNER_ARCH            # Architecture
RUNNER_NAME            # Runner name
RUNNER_TEMP            # Temp directory
```

## Secrets & Security

### Using Secrets
```yaml
jobs:
  deploy:
    steps:
      # In environment variable
      - env:
          API_KEY: ${{ secrets.API_KEY }}
        run: ./deploy.sh

      # Direct in command (be careful with logging)
      - run: echo "::add-mask::${{ secrets.TOKEN }}"

      # With action
      - uses: some/action@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
```

### GITHUB_TOKEN
Automatically provided token.

```yaml
permissions:
  contents: write      # Push to repository
  pull-requests: write # Comment on PRs
  issues: write        # Create/update issues
  packages: write      # Publish packages
  deployments: write   # Create deployments

jobs:
  job:
    steps:
      # Use in API calls
      - run: |
          curl -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
            https://api.github.com/repos/${{ github.repository }}

      # Use with actions
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
```

### Secure Practices
```yaml
steps:
  # Mask sensitive values
  - run: echo "::add-mask::${{ secrets.PASSWORD }}"

  # Don't echo secrets
  - run: ./script.sh  # Good
  - run: echo "${{ secrets.API_KEY }}"  # Bad - appears in logs

  # Use environment variables
  - env:
      SECRET_KEY: ${{ secrets.SECRET_KEY }}
    run: |
      # SECRET_KEY available but not logged
      ./deploy.sh
```

## Marketplace Actions

### Essential Actions

#### Checkout
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
    submodules: recursive
```

#### Setup Languages
```yaml
# Node.js
- uses: actions/setup-node@v4
  with:
    node-version: '16'
    cache: 'npm'

# Python
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

# Java
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'
    cache: 'maven'

# Go
- uses: actions/setup-go@v5
  with:
    go-version: '1.21'
    cache: true
```

#### Cache
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-
```

#### Upload/Download Artifacts
```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: build-artifacts
    path: |
      dist/
      build/
    retention-days: 5
    if-no-files-found: error

# Download
- uses: actions/download-artifact@v4
  with:
    name: build-artifacts
    path: ./artifacts
```

#### GitHub CLI
```yaml
- run: |
    gh pr comment ${{ github.event.number }} \
      --body "Deployment complete!"
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### Docker Actions
```yaml
# Build and push
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: user/app:latest

# Login to registry
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

## Best Practices

### 1. Pin Actions to Full SHA
```yaml
# Good (secure)
- uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab

# OK (version tag)
- uses: actions/checkout@v4

# Bad (mutable reference)
- uses: actions/checkout@main
```

### 2. Use Concurrency Control
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 3. Cache Dependencies
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### 4. Use Matrix Strategy
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node: [16, 18, 20]
  fail-fast: false
```

### 5. Set Timeouts
```yaml
jobs:
  build:
    timeout-minutes: 30
    steps:
      - name: Long task
        timeout-minutes: 10
        run: ./task.sh
```

### 6. Use Environments for Deployments
```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://prod.example.com
    steps:
      - run: ./deploy.sh
```

### 7. Minimize Secret Exposure
```yaml
# Good
- env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./script.sh

# Bad
- run: echo "${{ secrets.API_KEY }}" | ./script.sh
```

### 8. Use Reusable Workflows
```yaml
# .github/workflows/reusable.yml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string

# .github/workflows/main.yml
jobs:
  call-workflow:
    uses: ./.github/workflows/reusable.yml
    with:
      environment: production
```

### 9. Conditional Job Execution
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
```

### 10. Use Job Summaries
```yaml
- run: |
    echo "## Build Summary" >> $GITHUB_STEP_SUMMARY
    echo "Version: 1.0.0" >> $GITHUB_STEP_SUMMARY
    echo "Status: ✅ Success" >> $GITHUB_STEP_SUMMARY
```

## Common Patterns

### CI Pattern
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '16'
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run lint
```

### CD Pattern
```yaml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://prod.example.com
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
```

### Monorepo Pattern
```yaml
on:
  push:
    paths:
      - 'apps/frontend/**'
      - 'apps/backend/**'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.filter.outputs.frontend }}
      backend: ${{ steps.filter.outputs.backend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            frontend:
              - 'apps/frontend/**'
            backend:
              - 'apps/backend/**'

  build-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: npm run build:frontend

  build-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: npm run build:backend
```

### Release Pattern
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - run: npm run build
      - uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Awesome Actions](https://github.com/sdras/awesome-actions)

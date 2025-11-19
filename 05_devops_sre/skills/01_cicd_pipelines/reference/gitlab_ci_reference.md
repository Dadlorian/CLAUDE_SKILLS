# GitLab CI/CD Reference

## Table of Contents
- [Pipeline Configuration](#pipeline-configuration)
- [Jobs](#jobs)
- [Keywords Reference](#keywords-reference)
- [Predefined Variables](#predefined-variables)
- [GitLab Runners](#gitlab-runners)
- [Best Practices](#best-practices)
- [Advanced Features](#advanced-features)
- [Common Patterns](#common-patterns)

## Pipeline Configuration

### Basic Structure
```yaml
# .gitlab-ci.yml

# Define stages (order matters)
stages:
  - build
  - test
  - deploy

# Define jobs
build-job:
  stage: build
  script:
    - echo "Building the application"
    - npm install
    - npm run build

test-job:
  stage: test
  script:
    - echo "Running tests"
    - npm run test

deploy-job:
  stage: deploy
  script:
    - echo "Deploying application"
    - ./deploy.sh
```

### Default Settings
```yaml
default:
  # Default image for all jobs
  image: node:16-alpine

  # Default before_script for all jobs
  before_script:
    - echo "Running default before_script"

  # Default after_script for all jobs
  after_script:
    - echo "Running default after_script"

  # Default tags for all jobs
  tags:
    - docker

  # Default cache settings
  cache:
    paths:
      - node_modules/

  # Default retry settings
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure

  # Default timeout
  timeout: 1h

  # Default artifacts settings
  artifacts:
    expire_in: 1 week
```

### Global Variables
```yaml
variables:
  # Simple variable
  DEPLOY_ENV: "production"

  # Multiple variables
  DATABASE_URL: "postgres://localhost/db"
  API_VERSION: "v2"

  # Git settings
  GIT_DEPTH: "5"  # Shallow clone
  GIT_STRATEGY: "fetch"  # fetch, clone, or none
  GIT_SUBMODULE_STRATEGY: "recursive"

  # Pipeline settings
  FF_USE_FASTZIP: "true"  # Faster artifact compression
  ARTIFACT_COMPRESSION_LEVEL: "fast"
  CACHE_COMPRESSION_LEVEL: "fast"
```

## Jobs

### Basic Job Structure
```yaml
job-name:
  # Stage (required if stages are defined)
  stage: build

  # Docker image
  image: alpine:latest

  # Services (Docker-in-Docker, databases, etc.)
  services:
    - docker:dind
    - postgres:13

  # Variables specific to this job
  variables:
    POSTGRES_DB: mydb
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password

  # Commands to run before main script
  before_script:
    - apk add --no-cache git

  # Main script (required)
  script:
    - echo "Running main script"
    - ./build.sh

  # Commands to run after main script
  after_script:
    - echo "Cleanup"

  # Artifacts to preserve
  artifacts:
    paths:
      - build/
    expire_in: 1 week

  # Cache directories
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/

  # Dependencies (jobs to download artifacts from)
  dependencies:
    - build-job

  # Needs (jobs that must complete first)
  needs:
    - build-job

  # Tags for runner selection
  tags:
    - docker
    - linux

  # Rules for when to run
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

  # Retry configuration
  retry:
    max: 2
    when: script_failure

  # Timeout
  timeout: 30m

  # Allow failure
  allow_failure: false

  # When to run (on_success, on_failure, always, manual, delayed)
  when: on_success

  # Environment
  environment:
    name: production
    url: https://prod.example.com
```

## Keywords Reference

### image
Specify Docker image to use.

```yaml
# String format
image: node:16

# Extended format
image:
  name: node:16-alpine
  entrypoint: [""]  # Override entrypoint

# Different images for different jobs
job1:
  image: node:16
  script:
    - npm install

job2:
  image: python:3.9
  script:
    - pip install -r requirements.txt
```

### services
Start additional Docker containers.

```yaml
test-job:
  image: node:16
  services:
    - name: postgres:13
      alias: db
    - name: redis:6
      alias: cache
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password
  script:
    - npm run test:integration
```

### script
Main commands to execute (required).

```yaml
# Simple format
script:
  - echo "Command 1"
  - echo "Command 2"

# Multiline commands
script:
  - |
    if [ "$DEPLOY_ENV" == "production" ]; then
      ./deploy-prod.sh
    else
      ./deploy-dev.sh
    fi

# With error handling
script:
  - set -e  # Exit on error
  - command1
  - command2
```

### before_script & after_script
```yaml
job:
  before_script:
    - echo "Setup"
    - apt-get update

  script:
    - echo "Main execution"

  after_script:
    - echo "Cleanup (runs even if job fails)"
```

### artifacts
Save files/directories for later use.

```yaml
build:
  script:
    - npm run build
  artifacts:
    # Paths to save
    paths:
      - dist/
      - build/

    # Exclude patterns
    exclude:
      - dist/**/*.map

    # How long to keep
    expire_in: 1 week  # or: 30 mins, 2 hrs, 3 days, 1 month, never

    # Save on success/failure/always
    when: on_success

    # Make available for download
    expose_as: 'Build Artifacts'

    # Reports (special artifact types)
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
      dotenv: build.env  # Load variables from file

    # Public artifacts (accessible without authentication)
    public: true

    # Untracked files
    untracked: false

    # Job name prefix
    name: "$CI_JOB_NAME-$CI_COMMIT_REF_SLUG"
```

### cache
Cache files between pipeline runs.

```yaml
# Global cache
cache:
  # Cache key
  key: ${CI_COMMIT_REF_SLUG}

  # Alternative key strategies
  # key: ${CI_COMMIT_REF_SLUG}-${CI_COMMIT_SHA}  # Per commit
  # key: ${CI_PROJECT_NAME}  # Per project
  # key:
  #   files:
  #     - package-lock.json  # Based on file checksum

  # Paths to cache
  paths:
    - node_modules/
    - .npm/
    - vendor/

  # Policy: pull-push (default), pull, push
  policy: pull-push

  # Untracked files
  untracked: false

  # When to save cache
  when: on_success

# Job-specific cache override
job:
  cache:
    key: custom-key
    paths:
      - custom-cache/
    policy: pull  # Only download, don't upload
```

### dependencies & needs
Control job execution order and artifact downloads.

```yaml
# Sequential execution with artifacts
build:
  stage: build
  script:
    - make build
  artifacts:
    paths:
      - build/

test:
  stage: test
  dependencies:
    - build  # Download artifacts from build job
  script:
    - make test

# Parallel execution with explicit dependencies
build:
  stage: build
  script:
    - make build
  artifacts:
    paths:
      - build/

unit-test:
  stage: test
  needs: [build]  # Start as soon as build completes
  script:
    - make unit-test

integration-test:
  stage: test
  needs: [build]  # Also starts after build
  script:
    - make integration-test

# Needs with artifacts control
deploy:
  stage: deploy
  needs:
    - job: build
      artifacts: true  # Download artifacts (default)
    - job: unit-test
      artifacts: false  # Don't download artifacts
  script:
    - deploy.sh

# Cross-pipeline dependencies
downstream-job:
  needs:
    - project: group/project
      job: build-job
      ref: main
      artifacts: true
```

### rules
Conditionally run jobs (replaces only/except).

```yaml
# Basic rules
job:
  rules:
    # Run on main branch
    - if: '$CI_COMMIT_BRANCH == "main"'

    # Run on merge requests
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

    # Run on tags
    - if: '$CI_COMMIT_TAG'

    # Run on schedules
    - if: '$CI_PIPELINE_SOURCE == "schedule"'

    # Multiple conditions (AND)
    - if: '$CI_COMMIT_BRANCH == "main" && $DEPLOY_ENABLED == "true"'

    # Change when/allow_failure based on condition
    - if: '$CI_COMMIT_BRANCH == "develop"'
      when: manual
      allow_failure: true

    # File changes
    - changes:
        - Dockerfile
        - docker/**/*
      when: on_success

# Complex rules with workflow
workflow:
  rules:
    # Don't run on branches with "wip" prefix
    - if: '$CI_COMMIT_BRANCH =~ /^wip-/'
      when: never

    # Run on merge requests
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

    # Run on main branch
    - if: '$CI_COMMIT_BRANCH == "main"'

job:
  rules:
    # Inherit workflow rules, then add job-specific rules
    - if: '$CUSTOM_VARIABLE == "true"'
      when: manual
```

### only & except (legacy, use rules instead)
```yaml
# Only run on main branch
job:
  only:
    - main
  script:
    - deploy.sh

# Run on all branches except develop
job:
  except:
    - develop
  script:
    - test.sh

# Multiple conditions
job:
  only:
    - branches
    - tags
  except:
    - /^wip-/
```

### when
Control when a job runs.

```yaml
# Run on success (default)
when: on_success

# Run on failure
when: on_failure

# Always run
when: always

# Manual trigger
when: manual

# Delayed execution
when: delayed
start_in: 30 minutes  # or: 1 hour, 1 day, 1 week
```

### environment
Define deployment environments.

```yaml
deploy-prod:
  stage: deploy
  script:
    - deploy.sh
  environment:
    # Environment name
    name: production

    # Environment URL
    url: https://prod.example.com

    # Dynamic environment
    # name: review/$CI_COMMIT_REF_SLUG
    # url: https://$CI_COMMIT_REF_SLUG.example.com

    # Auto-stop environment
    on_stop: stop-review
    auto_stop_in: 1 day

    # Deployment tier
    deployment_tier: production  # production, staging, testing, development, other

    # Kubernetes namespace
    kubernetes:
      namespace: production

stop-review:
  stage: deploy
  script:
    - stop-environment.sh
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  when: manual
```

### parallel
Run job multiple times in parallel.

```yaml
# Run 5 parallel instances
test:
  script:
    - bundle exec rspec
  parallel: 5

# Matrix build
test:
  parallel:
    matrix:
      - PROVIDER: [aws, gcp, azure]
        STACK: [monitoring, app-backend, app-frontend]
  script:
    - ./test.sh $PROVIDER $STACK

# Variables accessible as:
# $CI_NODE_INDEX (1-5) and $CI_NODE_TOTAL (5)
```

### trigger
Trigger downstream pipelines.

```yaml
# Trigger another project
trigger-downstream:
  stage: deploy
  trigger:
    project: group/downstream-project
    branch: main

# Multi-project pipeline with variables
trigger-job:
  trigger:
    project: group/project
    strategy: depend  # Wait for downstream pipeline
  variables:
    DEPLOY_ENV: production

# Parent-child pipeline
trigger-child:
  trigger:
    include: path/to/child-pipeline.yml
    strategy: depend
```

### include
Include external YAML files.

```yaml
# Include from same repository
include:
  - local: '/templates/build.yml'
  - local: '/templates/deploy.yml'

# Include from another project
include:
  - project: 'group/project'
    ref: main
    file: '/templates/ci-template.yml'

# Include from URL
include:
  - remote: 'https://example.com/ci-template.yml'

# Include template
include:
  - template: 'Auto-DevOps.gitlab-ci.yml'

# Conditional include
include:
  - local: '/templates/production.yml'
    rules:
      - if: '$CI_COMMIT_BRANCH == "main"'
```

### extends
Inherit configuration from another job.

```yaml
.base-job:
  image: alpine:latest
  before_script:
    - apk add --no-cache git
  retry: 2

job1:
  extends: .base-job
  script:
    - echo "Job 1"

job2:
  extends: .base-job
  script:
    - echo "Job 2"

# Multiple inheritance
job3:
  extends:
    - .base-job
    - .deploy-config
  script:
    - deploy.sh
```

## Predefined Variables

### Pipeline Variables
```yaml
CI_PIPELINE_ID              # Pipeline ID
CI_PIPELINE_IID             # Pipeline IID (internal ID)
CI_PIPELINE_URL             # Pipeline URL
CI_PIPELINE_SOURCE          # Pipeline source (push, merge_request_event, schedule, etc.)
CI_PIPELINE_CREATED_AT      # Pipeline creation timestamp
```

### Commit Variables
```yaml
CI_COMMIT_SHA               # Full commit SHA
CI_COMMIT_SHORT_SHA         # Short commit SHA (8 chars)
CI_COMMIT_REF_NAME          # Branch or tag name
CI_COMMIT_REF_SLUG          # Branch/tag name (slugified)
CI_COMMIT_BRANCH            # Branch name (empty for tags)
CI_COMMIT_TAG               # Tag name (empty for branches)
CI_COMMIT_MESSAGE           # Full commit message
CI_COMMIT_TITLE             # Commit title (first line)
CI_COMMIT_DESCRIPTION       # Commit description (after first line)
CI_COMMIT_AUTHOR            # Commit author
CI_COMMIT_TIMESTAMP         # Commit timestamp
```

### Job Variables
```yaml
CI_JOB_ID                   # Job ID
CI_JOB_NAME                 # Job name
CI_JOB_STAGE                # Job stage
CI_JOB_STATUS               # Job status
CI_JOB_URL                  # Job URL
CI_JOB_STARTED_AT           # Job start time
CI_JOB_TOKEN                # Job token (for API calls)
```

### Project Variables
```yaml
CI_PROJECT_ID               # Project ID
CI_PROJECT_NAME             # Project name
CI_PROJECT_PATH             # Project path (namespace/project)
CI_PROJECT_URL              # Project URL
CI_PROJECT_DIR              # Project directory
CI_PROJECT_NAMESPACE        # Project namespace
CI_PROJECT_ROOT_NAMESPACE   # Root namespace
```

### Merge Request Variables
```yaml
CI_MERGE_REQUEST_IID        # MR internal ID
CI_MERGE_REQUEST_ID         # MR global ID
CI_MERGE_REQUEST_TITLE      # MR title
CI_MERGE_REQUEST_SOURCE_BRANCH_NAME     # Source branch
CI_MERGE_REQUEST_TARGET_BRANCH_NAME     # Target branch
CI_MERGE_REQUEST_DIFF_BASE_SHA          # Base SHA for diff
```

### Environment Variables
```yaml
CI                          # Always "true"
CI_SERVER                   # Always "yes"
GITLAB_CI                   # Always "true"
CI_SERVER_VERSION           # GitLab version
CI_SERVER_REVISION          # GitLab revision
```

## GitLab Runners

### Runner Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Shared** | Available to all projects | General purpose |
| **Group** | Available to group projects | Team-specific |
| **Specific** | Project-specific | Project requirements |

### Executor Types

| Executor | Description | Best For |
|----------|-------------|----------|
| **shell** | Runs on host machine | Simple builds |
| **docker** | Runs in Docker container | Isolated environments |
| **kubernetes** | Runs in Kubernetes pod | Cloud-native apps |
| **docker+machine** | Auto-scales Docker hosts | High load |

### Runner Configuration
```toml
# /etc/gitlab-runner/config.toml

concurrent = 4  # Max concurrent jobs

[[runners]]
  name = "docker-runner"
  url = "https://gitlab.com"
  token = "RUNNER_TOKEN"
  executor = "docker"

  [runners.docker]
    image = "alpine:latest"
    privileged = false
    volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]
    pull_policy = "if-not-present"
    shm_size = 0

  [runners.cache]
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "us-east-1"
```

### Runner Tags
```yaml
# Use specific runner with tags
job:
  tags:
    - docker
    - linux
    - high-memory
  script:
    - make build
```

## Best Practices

### 1. Use Templates and Extends
```yaml
# Define base template
.base-test:
  image: node:16
  before_script:
    - npm ci
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/

# Extend template
unit-test:
  extends: .base-test
  script:
    - npm run test:unit

integration-test:
  extends: .base-test
  script:
    - npm run test:integration
```

### 2. Use Anchors for DRY Configuration
```yaml
# Define anchor
.node-cache: &node-cache
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/

# Use anchor
job1:
  <<: *node-cache
  script:
    - npm install
```

### 3. Leverage Parallel Execution
```yaml
test:
  parallel: 5
  script:
    - bundle exec rspec --tag ~slow
```

### 4. Optimize with needs
```yaml
# Traditional (sequential)
stages:
  - build
  - test
  - deploy

# Optimized (parallel where possible)
build:
  stage: build
  script: make build

unit-test:
  stage: test
  needs: [build]  # Starts immediately after build
  script: make unit-test

integration-test:
  stage: test
  needs: [build]  # Also starts immediately after build
  script: make integration-test
```

### 5. Use Rules Instead of only/except
```yaml
# Good (rules)
deploy:
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_TAG'
  script:
    - deploy.sh

# Deprecated (only/except)
deploy:
  only:
    - main
    - tags
  script:
    - deploy.sh
```

### 6. Secure Variables
```yaml
# Mark sensitive variables as protected/masked in GitLab UI
# Reference in pipeline:
deploy:
  script:
    - echo "$API_KEY" | docker login -u user --password-stdin
  only:
    - main  # Protected variables only available on protected branches
```

### 7. Use Artifacts Wisely
```yaml
# Don't artifact everything
build:
  script:
    - npm run build
  artifacts:
    paths:
      - dist/  # Only production build
    expire_in: 1 week  # Auto-cleanup
    exclude:
      - dist/**/*.map  # Exclude source maps
```

### 8. Cache Dependencies
```yaml
# Cache package dependencies
cache:
  key:
    files:
      - package-lock.json  # Cache key based on file
  paths:
    - node_modules/
  policy: pull-push

# Per-job cache policy
install:
  cache:
    policy: push  # Only upload cache

test:
  cache:
    policy: pull  # Only download cache
```

### 9. Use Workflow Rules
```yaml
# Control entire pipeline execution
workflow:
  rules:
    # Don't run pipelines for draft MRs
    - if: '$CI_MERGE_REQUEST_TITLE =~ /^Draft:/'
      when: never

    # Run on merge requests
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

    # Run on main branch
    - if: '$CI_COMMIT_BRANCH == "main"'

    # Otherwise don't run
    - when: never
```

### 10. Version Control Pipeline
```yaml
# Include version in artifacts
build:
  script:
    - echo "VERSION=$CI_COMMIT_SHORT_SHA" > version.txt
    - make build
  artifacts:
    paths:
      - version.txt
      - dist/
    reports:
      dotenv: version.txt  # Load VERSION as environment variable
```

## Advanced Features

### Multi-Project Pipelines
```yaml
# Parent pipeline
trigger-backend:
  stage: trigger
  trigger:
    project: group/backend
    strategy: depend

trigger-frontend:
  stage: trigger
  trigger:
    project: group/frontend
    strategy: depend
```

### Parent-Child Pipelines
```yaml
# Parent .gitlab-ci.yml
generate-config:
  stage: build
  script:
    - ./generate-ci-config.sh > child-pipeline.yml
  artifacts:
    paths:
      - child-pipeline.yml

trigger-child:
  stage: deploy
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: generate-config
    strategy: depend
```

### Dynamic Child Pipelines
```yaml
# Automatically create pipelines for each microservice
generate-pipelines:
  stage: prepare
  script:
    - |
      for service in services/*; do
        cat > "pipeline-$(basename $service).yml" <<EOF
      test-$(basename $service):
        script:
          - cd $service
          - npm test
      EOF
      done
  artifacts:
    paths:
      - pipeline-*.yml

trigger-service-pipelines:
  stage: test
  needs: [generate-pipelines]
  trigger:
    include:
      - artifact: pipeline-*.yml
        job: generate-pipelines
```

### Container Registry
```yaml
build-docker:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG
```

### Pages Deployment
```yaml
pages:
  stage: deploy
  script:
    - npm run build
    - mv dist public
  artifacts:
    paths:
      - public
  only:
    - main
```

## Common Patterns

### Monorepo Pattern
```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

.detect-changes: &detect-changes
  - |
    if git diff --name-only $CI_MERGE_REQUEST_DIFF_BASE_SHA $CI_COMMIT_SHA | grep -q "^backend/"; then
      echo "BACKEND_CHANGED=true" >> build.env
    fi
    if git diff --name-only $CI_MERGE_REQUEST_DIFF_BASE_SHA $CI_COMMIT_SHA | grep -q "^frontend/"; then
      echo "FRONTEND_CHANGED=true" >> build.env
    fi

detect-changes:
  stage: .pre
  script:
    - *detect-changes
  artifacts:
    reports:
      dotenv: build.env

test-backend:
  stage: test
  rules:
    - if: '$BACKEND_CHANGED == "true"'
  script:
    - cd backend && npm test

test-frontend:
  stage: test
  rules:
    - if: '$FRONTEND_CHANGED == "true"'
  script:
    - cd frontend && npm test
```

### Review Apps Pattern
```yaml
review:
  stage: deploy
  script:
    - kubectl create namespace review-$CI_COMMIT_REF_SLUG || true
    - helm upgrade --install review-$CI_COMMIT_REF_SLUG ./chart
        --namespace review-$CI_COMMIT_REF_SLUG
        --set image.tag=$CI_COMMIT_SHORT_SHA
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://review-$CI_COMMIT_REF_SLUG.example.com
    on_stop: stop-review
    auto_stop_in: 1 week
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

stop-review:
  stage: deploy
  script:
    - helm uninstall review-$CI_COMMIT_REF_SLUG --namespace review-$CI_COMMIT_REF_SLUG
    - kubectl delete namespace review-$CI_COMMIT_REF_SLUG
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  when: manual
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

### Versioning Pattern
```yaml
variables:
  VERSION: "1.0.${CI_PIPELINE_IID}"

build:
  script:
    - echo "Building version $VERSION"
    - docker build -t myapp:$VERSION .

release:
  stage: deploy
  script:
    - docker tag myapp:$VERSION myapp:latest
    - docker push myapp:$VERSION
    - docker push myapp:latest
    - git tag -a "v$VERSION" -m "Release $VERSION"
    - git push origin "v$VERSION"
  only:
    - main
```

## Resources

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [.gitlab-ci.yml Reference](https://docs.gitlab.com/ee/ci/yaml/)
- [GitLab CI/CD Examples](https://docs.gitlab.com/ee/ci/examples/)
- [GitLab Runner Documentation](https://docs.gitlab.com/runner/)

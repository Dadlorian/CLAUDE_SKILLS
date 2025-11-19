# CI/CD Pipeline Patterns

## Table of Contents
- [Basic Patterns](#basic-patterns)
- [Advanced Patterns](#advanced-patterns)
- [Deployment Patterns](#deployment-patterns)
- [Testing Patterns](#testing-patterns)
- [Release Patterns](#release-patterns)
- [Monorepo Patterns](#monorepo-patterns)
- [Security Patterns](#security-patterns)
- [Performance Patterns](#performance-patterns)

## Basic Patterns

### 1. Simple CI Pipeline
**Pattern**: Build → Test → Report

#### Jenkins
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        stage('Report') {
            steps {
                junit '**/test-results.xml'
                publishHTML([reportDir: 'coverage', reportFiles: 'index.html', reportName: 'Coverage'])
            }
        }
    }
}
```

#### GitLab CI
```yaml
stages:
  - build
  - test
  - report

build:
  stage: build
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  script:
    - npm test
  artifacts:
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
```

#### GitHub Actions
```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '16'
      - run: npm install
      - run: npm run build
      - run: npm test
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/
```

### 2. Multi-Stage Pipeline
**Pattern**: Build → Unit Test → Integration Test → Deploy

#### Jenkins
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        stage('Unit Tests') {
            steps {
                sh 'mvn test'
            }
        }
        stage('Integration Tests') {
            steps {
                sh 'mvn verify -P integration-tests'
            }
        }
        stage('Deploy to Dev') {
            when {
                branch 'develop'
            }
            steps {
                sh './deploy.sh dev'
            }
        }
    }
}
```

#### GitLab CI
```yaml
stages:
  - build
  - unit-test
  - integration-test
  - deploy

build:
  stage: build
  script:
    - mvn clean package -DskipTests
  artifacts:
    paths:
      - target/*.jar

unit-test:
  stage: unit-test
  script:
    - mvn test

integration-test:
  stage: integration-test
  script:
    - mvn verify -P integration-tests

deploy-dev:
  stage: deploy
  script:
    - ./deploy.sh dev
  only:
    - develop
```

#### GitHub Actions
```yaml
name: Multi-Stage Pipeline

on:
  push:
    branches: [develop, main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: mvn clean package -DskipTests
      - uses: actions/upload-artifact@v4
        with:
          name: jar-file
          path: target/*.jar

  unit-test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: mvn test

  integration-test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: mvn verify -P integration-tests

  deploy:
    needs: [unit-test, integration-test]
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh dev
```

## Advanced Patterns

### 3. Parallel Execution Pattern
**Pattern**: Run independent jobs concurrently

#### Jenkins
```groovy
pipeline {
    agent any
    stages {
        stage('Parallel Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit'
                    }
                }
                stage('Integration Tests') {
                    steps {
                        sh 'npm run test:integration'
                    }
                }
                stage('E2E Tests') {
                    steps {
                        sh 'npm run test:e2e'
                    }
                }
                stage('Lint') {
                    steps {
                        sh 'npm run lint'
                    }
                }
            }
        }
    }
}
```

#### GitLab CI
```yaml
stages:
  - test

unit-tests:
  stage: test
  script:
    - npm run test:unit

integration-tests:
  stage: test
  script:
    - npm run test:integration

e2e-tests:
  stage: test
  script:
    - npm run test:e2e

lint:
  stage: test
  script:
    - npm run lint
```

#### GitHub Actions
```yaml
jobs:
  test:
    strategy:
      matrix:
        test-type: [unit, integration, e2e]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run test:${{ matrix.test-type }}

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run lint
```

### 4. Matrix Build Pattern
**Pattern**: Test across multiple environments

#### Jenkins
```groovy
pipeline {
    agent none
    stages {
        stage('Matrix Build') {
            matrix {
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'linux', 'windows', 'macos'
                    }
                    axis {
                        name 'NODE_VERSION'
                        values '16', '18', '20'
                    }
                }
                agent {
                    label "${PLATFORM}"
                }
                stages {
                    stage('Build & Test') {
                        steps {
                            sh "nvm use ${NODE_VERSION}"
                            sh 'npm install'
                            sh 'npm test'
                        }
                    }
                }
            }
        }
    }
}
```

#### GitLab CI
```yaml
test:
  parallel:
    matrix:
      - PLATFORM: [ubuntu, windows, macos]
        NODE_VERSION: ['16', '18', '20']
  tags:
    - $PLATFORM
  script:
    - nvm use $NODE_VERSION
    - npm install
    - npm test
```

#### GitHub Actions
```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [16, 18, 20]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm install
      - run: npm test
```

### 5. Conditional Pipeline Pattern
**Pattern**: Different flows based on branch/conditions

#### Jenkins
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        stage('Deploy Dev') {
            when {
                branch 'develop'
            }
            steps {
                sh './deploy.sh dev'
            }
        }
        stage('Deploy Staging') {
            when {
                branch 'release/*'
            }
            steps {
                sh './deploy.sh staging'
            }
        }
        stage('Deploy Production') {
            when {
                allOf {
                    branch 'main'
                    expression { currentBuild.result == 'SUCCESS' }
                }
            }
            steps {
                input message: 'Deploy to production?'
                sh './deploy.sh production'
            }
        }
    }
}
```

#### GitLab CI
```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH == "develop"'
    - if: '$CI_COMMIT_BRANCH =~ /^release\/.*$/'

stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - npm run build

test:
  stage: test
  script:
    - npm test

deploy-dev:
  stage: deploy
  script:
    - ./deploy.sh dev
  rules:
    - if: '$CI_COMMIT_BRANCH == "develop"'

deploy-staging:
  stage: deploy
  script:
    - ./deploy.sh staging
  rules:
    - if: '$CI_COMMIT_BRANCH =~ /^release\/.*$/'

deploy-production:
  stage: deploy
  script:
    - ./deploy.sh production
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  when: manual
```

#### GitHub Actions
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  deploy-dev:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh dev

  deploy-staging:
    needs: test
    if: startsWith(github.ref, 'refs/heads/release/')
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh staging

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
    steps:
      - run: ./deploy.sh production
```

## Deployment Patterns

### 6. Blue-Green Deployment
**Pattern**: Deploy to inactive environment, then switch traffic

```groovy
// Jenkins
pipeline {
    agent any
    environment {
        BLUE_ENV = 'production-blue'
        GREEN_ENV = 'production-green'
        ACTIVE_ENV = sh(script: 'get-active-env.sh', returnStdout: true).trim()
        TARGET_ENV = "${ACTIVE_ENV == 'blue' ? GREEN_ENV : BLUE_ENV}"
    }
    stages {
        stage('Deploy to Inactive') {
            steps {
                sh "./deploy.sh ${TARGET_ENV}"
            }
        }
        stage('Health Check') {
            steps {
                sh "./health-check.sh ${TARGET_ENV}"
            }
        }
        stage('Switch Traffic') {
            steps {
                input message: "Switch traffic to ${TARGET_ENV}?"
                sh "./switch-traffic.sh ${TARGET_ENV}"
            }
        }
        stage('Verify') {
            steps {
                sh './verify-production.sh'
            }
        }
    }
    post {
        failure {
            sh "./rollback.sh ${ACTIVE_ENV}"
        }
    }
}
```

### 7. Canary Deployment
**Pattern**: Gradually roll out to subset of users

```yaml
# GitLab CI
stages:
  - build
  - deploy-canary
  - verify
  - deploy-full
  - rollback

deploy-canary:
  stage: deploy-canary
  script:
    - kubectl set image deployment/myapp myapp=$IMAGE_TAG
    - kubectl scale deployment/myapp-canary --replicas=2
  environment:
    name: production-canary

verify-canary:
  stage: verify
  script:
    - ./monitor-metrics.sh canary 10m
    - ./check-error-rate.sh canary

deploy-full:
  stage: deploy-full
  when: manual
  script:
    - kubectl set image deployment/myapp myapp=$IMAGE_TAG
    - kubectl scale deployment/myapp --replicas=10
  environment:
    name: production

rollback-canary:
  stage: rollback
  when: on_failure
  script:
    - kubectl scale deployment/myapp-canary --replicas=0
```

### 8. Rolling Deployment
**Pattern**: Update instances one by one

```yaml
# GitHub Actions
jobs:
  rolling-deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        instance: [1, 2, 3, 4, 5]
      max-parallel: 1
    steps:
      - name: Deploy to instance ${{ matrix.instance }}
        run: |
          ./deploy-to-instance.sh ${{ matrix.instance }}
          ./health-check.sh ${{ matrix.instance }}
          sleep 30
```

## Testing Patterns

### 9. Test Pyramid Pattern
**Pattern**: Unit → Integration → E2E with appropriate coverage

```yaml
# GitLab CI
stages:
  - unit-tests
  - integration-tests
  - e2e-tests

unit-tests:
  stage: unit-tests
  parallel: 5  # Fast, lots of tests
  script:
    - npm run test:unit
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'

integration-tests:
  stage: integration-tests
  parallel: 2  # Medium speed
  services:
    - postgres:13
    - redis:6
  script:
    - npm run test:integration

e2e-tests:
  stage: e2e-tests
  # No parallel - expensive, few tests
  script:
    - npm run test:e2e
  allow_failure: true  # Don't block on flaky E2E
```

### 10. Contract Testing Pattern
**Pattern**: Verify API contracts between services

```groovy
// Jenkins
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Provider Contract Tests') {
            steps {
                sh 'mvn test -Dtest=ProviderContractTest'
                publishHTML([
                    reportDir: 'target/pact',
                    reportFiles: 'index.html',
                    reportName: 'Pact Verification'
                ])
            }
        }
        stage('Publish Contracts') {
            steps {
                sh '''
                    curl -X PUT \
                      -H "Content-Type: application/json" \
                      -d @target/pacts/consumer-provider.json \
                      http://pact-broker/pacts/provider/MyService/consumer/MyConsumer/version/${BUILD_NUMBER}
                '''
            }
        }
    }
}
```

## Release Patterns

### 11. Semantic Versioning Pattern
**Pattern**: Auto-increment version based on commits

```yaml
# GitHub Actions
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Semantic Release
        uses: cycjimmy/semantic-release-action@v4
        with:
          extra_plugins: |
            @semantic-release/changelog
            @semantic-release/git
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### 12. Tag-Based Release Pattern
**Pattern**: Trigger release on version tag

```groovy
// Jenkins
pipeline {
    agent any
    when {
        tag pattern: 'v\\d+\\.\\d+\\.\\d+', comparator: 'REGEXP'
    }
    environment {
        VERSION = "${TAG_NAME.substring(1)}"  // Remove 'v' prefix
    }
    stages {
        stage('Build') {
            steps {
                sh "mvn versions:set -DnewVersion=${VERSION}"
                sh 'mvn clean package'
            }
        }
        stage('Create Release') {
            steps {
                sh '''
                    gh release create ${TAG_NAME} \
                      target/*.jar \
                      --title "Release ${VERSION}" \
                      --notes-file CHANGELOG.md
                '''
            }
        }
        stage('Publish Artifacts') {
            steps {
                sh 'mvn deploy'
            }
        }
    }
}
```

## Monorepo Patterns

### 13. Selective Build Pattern
**Pattern**: Build only changed packages

```yaml
# GitLab CI
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

detect-changes:
  stage: .pre
  script:
    - |
      if git diff --name-only ${CI_MERGE_REQUEST_DIFF_BASE_SHA} ${CI_COMMIT_SHA} | grep -q "^packages/api/"; then
        echo "API_CHANGED=true" >> build.env
      fi
      if git diff --name-only ${CI_MERGE_REQUEST_DIFF_BASE_SHA} ${CI_COMMIT_SHA} | grep -q "^packages/web/"; then
        echo "WEB_CHANGED=true" >> build.env
      fi
      if git diff --name-only ${CI_MERGE_REQUEST_DIFF_BASE_SHA} ${CI_COMMIT_SHA} | grep -q "^packages/mobile/"; then
        echo "MOBILE_CHANGED=true" >> build.env
      fi
  artifacts:
    reports:
      dotenv: build.env

build-api:
  stage: build
  rules:
    - if: '$API_CHANGED == "true"'
  script:
    - cd packages/api
    - npm run build

build-web:
  stage: build
  rules:
    - if: '$WEB_CHANGED == "true"'
  script:
    - cd packages/web
    - npm run build

build-mobile:
  stage: build
  rules:
    - if: '$MOBILE_CHANGED == "true"'
  script:
    - cd packages/mobile
    - npm run build
```

### 14. Dependency-Aware Build Pattern
**Pattern**: Build packages in dependency order

```yaml
# GitHub Actions
jobs:
  # Build shared utilities first
  build-utils:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build --workspace=@myapp/utils
      - uses: actions/upload-artifact@v4
        with:
          name: utils-dist
          path: packages/utils/dist

  # Build API (depends on utils)
  build-api:
    needs: build-utils
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: utils-dist
          path: packages/utils/dist
      - run: npm run build --workspace=@myapp/api
      - uses: actions/upload-artifact@v4
        with:
          name: api-dist
          path: packages/api/dist

  # Build web (depends on utils)
  build-web:
    needs: build-utils
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: utils-dist
          path: packages/utils/dist
      - run: npm run build --workspace=@myapp/web
      - uses: actions/upload-artifact@v4
        with:
          name: web-dist
          path: packages/web/dist
```

## Security Patterns

### 15. Security Scanning Pattern
**Pattern**: Multiple security checks in pipeline

```groovy
// Jenkins
pipeline {
    agent any
    stages {
        stage('Security Scans') {
            parallel {
                stage('SAST') {
                    steps {
                        sh 'sonar-scanner'
                    }
                }
                stage('Dependency Check') {
                    steps {
                        sh 'npm audit --audit-level=moderate'
                        sh 'snyk test'
                    }
                }
                stage('Secret Scanning') {
                    steps {
                        sh 'gitleaks detect --source=. --verbose'
                    }
                }
                stage('Container Scan') {
                    steps {
                        sh 'trivy image myapp:${BUILD_NUMBER}'
                    }
                }
                stage('License Check') {
                    steps {
                        sh 'license-checker --production --onlyAllow "MIT;Apache-2.0;BSD-3-Clause"'
                    }
                }
            }
        }
        stage('DAST') {
            steps {
                sh 'docker run -t owasp/zap2docker-stable zap-baseline.py -t http://staging.example.com'
            }
        }
    }
}
```

### 16. Signed Commits & Artifacts Pattern
**Pattern**: Verify code integrity

```yaml
# GitLab CI
stages:
  - verify
  - build
  - sign

verify-commit:
  stage: verify
  script:
    - git verify-commit ${CI_COMMIT_SHA}

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/

sign-artifacts:
  stage: sign
  script:
    - |
      for file in dist/*; do
        gpg --detach-sign --armor $file
        sha256sum $file > $file.sha256
      done
  artifacts:
    paths:
      - dist/*.asc
      - dist/*.sha256
```

## Performance Patterns

### 17. Cache Optimization Pattern
**Pattern**: Maximize cache hits

```yaml
# GitHub Actions
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Layer 1: Node.js cache
      - uses: actions/setup-node@v4
        with:
          node-version: '16'
          cache: 'npm'

      # Layer 2: Dependencies cache
      - uses: actions/cache@v4
        id: npm-cache
        with:
          path: node_modules
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-

      # Only install if cache miss
      - if: steps.npm-cache.outputs.cache-hit != 'true'
        run: npm ci

      # Layer 3: Build cache
      - uses: actions/cache@v4
        with:
          path: .next/cache
          key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx') }}
          restore-keys: |
            ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-

      - run: npm run build
```

### 18. Artifact Management Pattern
**Pattern**: Efficient artifact handling

```yaml
# GitLab CI
variables:
  # Enable fast compression
  FF_USE_FASTZIP: "true"
  ARTIFACT_COMPRESSION_LEVEL: "fast"
  CACHE_COMPRESSION_LEVEL: "fast"

build:
  stage: build
  script:
    - npm run build
  artifacts:
    name: "build-${CI_COMMIT_SHORT_SHA}"
    expire_in: 1 week
    paths:
      - dist/
    exclude:
      - dist/**/*.map  # Exclude source maps
      - dist/**/*.md   # Exclude documentation

test:
  stage: test
  dependencies:
    - build  # Only download artifacts from build job
  script:
    - npm test

deploy:
  stage: deploy
  dependencies: []  # Don't download any artifacts
  script:
    - aws s3 sync s3://artifacts/build-${CI_COMMIT_SHORT_SHA} ./dist
    - ./deploy.sh
```

### 19. Dynamic Pipeline Generation
**Pattern**: Generate pipeline configuration dynamically

```yaml
# GitLab CI - Parent pipeline
generate-child-pipeline:
  stage: generate
  script:
    - |
      cat > child-pipeline.yml <<EOF
      stages:
        - test
      EOF

      for service in services/*/; do
        service_name=$(basename $service)
        cat >> child-pipeline.yml <<EOF

      test-${service_name}:
        stage: test
        script:
          - cd services/${service_name}
          - npm test
      EOF
      done
  artifacts:
    paths:
      - child-pipeline.yml

trigger-child:
  stage: trigger
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: generate-child-pipeline
    strategy: depend
```

### 20. Failure Recovery Pattern
**Pattern**: Automatic retry and recovery

```groovy
// Jenkins
pipeline {
    agent any
    options {
        retry(3)
    }
    stages {
        stage('Deploy') {
            steps {
                script {
                    try {
                        timeout(time: 10, unit: 'MINUTES') {
                            sh './deploy.sh'
                            sh './health-check.sh'
                        }
                    } catch (Exception e) {
                        echo "Deployment failed, attempting rollback"
                        sh './rollback.sh'

                        // Retry with exponential backoff
                        retry(3) {
                            sleep(time: 30, unit: 'SECONDS')
                            sh './deploy.sh'
                        }
                    }
                }
            }
        }
    }
    post {
        failure {
            script {
                // Capture diagnostics
                sh 'kubectl get pods > diagnostics.log'
                sh 'kubectl logs deployment/myapp >> diagnostics.log'
                archiveArtifacts 'diagnostics.log'

                // Notify team
                emailext body: """
                    Deployment failed after retries.
                    See diagnostics: ${env.BUILD_URL}artifact/diagnostics.log
                """,
                subject: "Deployment Failed - ${env.JOB_NAME}",
                to: 'devops@example.com'
            }
        }
    }
}
```

## Summary

### Pattern Selection Guide

| Use Case | Recommended Pattern |
|----------|-------------------|
| Simple project | Simple CI Pipeline (#1) |
| Microservices | Multi-Stage Pipeline (#2) |
| Multiple platforms | Matrix Build (#4) |
| Zero-downtime deploy | Blue-Green (#6) or Canary (#7) |
| Large test suite | Parallel Execution (#3), Test Pyramid (#9) |
| Monorepo | Selective Build (#13), Dependency-Aware (#14) |
| Security-critical | Security Scanning (#15), Signed Artifacts (#16) |
| Slow builds | Cache Optimization (#17) |
| Complex workflows | Dynamic Pipeline (#19) |

### Best Practices Across Patterns

1. **Always include health checks** after deployments
2. **Implement rollback mechanisms** for all deployment patterns
3. **Use parallel execution** where jobs are independent
4. **Cache dependencies** to improve build times
5. **Set appropriate timeouts** for all stages
6. **Collect and archive diagnostics** on failures
7. **Implement proper retry logic** for flaky operations
8. **Use semantic versioning** for releases
9. **Verify security** at multiple stages
10. **Monitor and measure** pipeline performance

### Anti-Patterns to Avoid

- Building on every commit to feature branches (use PR checks instead)
- Deploying directly from feature branches
- Hardcoding credentials in pipeline files
- Not setting timeouts (can hang forever)
- Downloading all artifacts when only some are needed
- Running expensive E2E tests on every commit
- Not caching dependencies
- Ignoring security scan failures
- Not implementing rollback strategies
- Deploying without health checks

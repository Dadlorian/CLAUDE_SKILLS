# Jenkins Pipeline Reference

## Table of Contents
- [Pipeline Syntax](#pipeline-syntax)
- [Declarative vs Scripted](#declarative-vs-scripted)
- [Pipeline Sections](#pipeline-sections)
- [Directives](#directives)
- [Steps](#steps)
- [Essential Plugins](#essential-plugins)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Pipeline Syntax

### Basic Declarative Pipeline Structure
```groovy
pipeline {
    agent any

    environment {
        // Environment variables
    }

    stages {
        stage('Build') {
            steps {
                // Build steps
            }
        }
    }

    post {
        // Post-build actions
    }
}
```

### Basic Scripted Pipeline Structure
```groovy
node {
    stage('Build') {
        // Build steps
    }
    stage('Test') {
        // Test steps
    }
}
```

## Declarative vs Scripted

| Feature | Declarative | Scripted |
|---------|-------------|----------|
| **Syntax** | Structured, opinionated | Flexible, Groovy-based |
| **Learning Curve** | Easier | Steeper |
| **Flexibility** | Limited to directives | Full Groovy power |
| **Error Handling** | Built-in with `post` | Manual try-catch |
| **Recommendation** | Preferred for most cases | Complex workflows |

## Pipeline Sections

### Agent
Defines where the pipeline or stage executes.

```groovy
// Execute anywhere
agent any

// Execute on specific label
agent { label 'linux' }

// Execute in Docker container
agent {
    docker {
        image 'maven:3.8.1-jdk-11'
        args '-v $HOME/.m2:/root/.m2'
    }
}

// Execute in Kubernetes pod
agent {
    kubernetes {
        yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.8.1-jdk-11
    command: ['cat']
    tty: true
        '''
    }
}

// No agent (must specify in each stage)
agent none
```

### Environment
Defines environment variables.

```groovy
environment {
    // Simple variable
    VERSION = '1.0.0'

    // Using credentials
    AWS_CREDENTIALS = credentials('aws-credentials-id')

    // Credential subtypes
    DOCKER_CREDS = credentials('docker-hub')
    // Creates: DOCKER_CREDS_USR, DOCKER_CREDS_PSW

    // Dynamic value
    BUILD_TIME = sh(script: 'date +%Y%m%d-%H%M%S', returnStdout: true).trim()

    // PATH modification
    PATH = "${WORKSPACE}/bin:${env.PATH}"
}
```

### Stages & Steps
Define the sequential work of the pipeline.

```groovy
stages {
    stage('Parallel Build') {
        parallel {
            stage('Build Backend') {
                steps {
                    sh 'mvn clean package'
                }
            }
            stage('Build Frontend') {
                steps {
                    sh 'npm run build'
                }
            }
        }
    }

    stage('Sequential Deploy') {
        stages {
            stage('Deploy Dev') {
                steps {
                    echo 'Deploying to dev'
                }
            }
            stage('Deploy Prod') {
                steps {
                    echo 'Deploying to prod'
                }
            }
        }
    }
}
```

### Post Section
Runs after pipeline/stage completion.

```groovy
post {
    always {
        // Always run
        junit '**/target/surefire-reports/*.xml'
        cleanWs()
    }
    success {
        // Only on success
        slackSend color: 'good', message: "Build ${env.BUILD_NUMBER} succeeded"
    }
    failure {
        // Only on failure
        slackSend color: 'danger', message: "Build ${env.BUILD_NUMBER} failed"
        emailext body: "${currentBuild.result}", subject: "Build Failed", to: 'dev-team@example.com'
    }
    unstable {
        // When marked unstable
        echo 'Build is unstable'
    }
    changed {
        // When state changes from previous build
        echo 'Build state changed'
    }
    fixed {
        // When build was failing but now succeeds
        echo 'Build is fixed!'
    }
    regression {
        // When build was succeeding but now fails
        echo 'Build regressed'
    }
    aborted {
        // When manually aborted
        echo 'Build was aborted'
    }
    cleanup {
        // Always runs last, even if other post sections fail
        deleteDir()
    }
}
```

## Directives

### Options
Configure pipeline-wide settings.

```groovy
options {
    // Keep only last 10 builds
    buildDiscarder(logRotator(numToKeepStr: '10'))

    // Disable concurrent builds
    disableConcurrentBuilds()

    // Skip default checkout
    skipDefaultCheckout()

    // Timeout for entire pipeline
    timeout(time: 1, unit: 'HOURS')

    // Add timestamps to console output
    timestamps()

    // Retry entire pipeline on failure
    retry(3)

    // Disable automatic resume
    disableResume()

    // Quiet period before build starts
    quietPeriod(30)

    // Preserve stashes
    preserveStashes(buildCount: 5)
}
```

### Parameters
Define build parameters.

```groovy
parameters {
    string(name: 'DEPLOY_ENV', defaultValue: 'dev', description: 'Deployment environment')

    choice(name: 'BUILD_TYPE', choices: ['snapshot', 'release'], description: 'Build type')

    booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run tests?')

    text(name: 'RELEASE_NOTES', defaultValue: '', description: 'Release notes')

    password(name: 'API_KEY', defaultValue: '', description: 'API key')

    file(name: 'CONFIG_FILE', description: 'Configuration file')
}
```

### Triggers
Automate pipeline execution.

```groovy
triggers {
    // Poll SCM every 5 minutes
    pollSCM('H/5 * * * *')

    // Cron schedule (run at 2 AM daily)
    cron('0 2 * * *')

    // Trigger from upstream job
    upstream(upstreamProjects: 'job1,job2', threshold: hudson.model.Result.SUCCESS)

    // GitHub webhook trigger
    githubPush()
}
```

### Tools
Auto-install and configure tools.

```groovy
tools {
    maven 'Maven-3.8.1'
    jdk 'JDK-11'
    nodejs 'NodeJS-16'
    gradle 'Gradle-7.0'
}
```

### When
Conditional stage execution.

```groovy
stage('Deploy to Production') {
    when {
        // Multiple conditions (all must be true)
        allOf {
            branch 'main'
            environment name: 'DEPLOY_ENV', value: 'prod'
        }

        // Any condition (at least one must be true)
        anyOf {
            branch 'main'
            branch 'release/*'
        }

        // Negate condition
        not {
            branch 'develop'
        }

        // Build successful
        expression { currentBuild.result == 'SUCCESS' }

        // Tag event
        tag 'v*'

        // Change request (PR)
        changeRequest()

        // Specific commit author
        changelog '.*\\[deploy\\].*'

        // Evaluate before agent allocation
        beforeAgent true
    }
    steps {
        echo 'Deploying to production'
    }
}
```

### Input
Request manual approval or input.

```groovy
stage('Deploy to Production') {
    input {
        message "Deploy to production?"
        ok "Deploy"
        submitter "admin,ops-team"
        parameters {
            choice(name: 'REGION', choices: ['us-east-1', 'eu-west-1'], description: 'AWS Region')
        }
    }
    steps {
        echo "Deploying to ${REGION}"
    }
}
```

## Steps

### Common Steps

```groovy
// Shell command
sh 'mvn clean install'
sh(script: 'ls -la', returnStdout: true)

// Batch (Windows)
bat 'dir'

// PowerShell
powershell 'Get-ChildItem'

// Echo
echo 'Hello, World!'

// Error
error 'Build failed due to missing dependencies'

// Retry
retry(3) {
    sh 'curl https://api.example.com'
}

// Timeout
timeout(time: 10, unit: 'MINUTES') {
    sh './long-running-script.sh'
}

// Wait until
waitUntil {
    script {
        def r = sh(script: 'curl -s http://localhost:8080', returnStatus: true)
        return r == 0
    }
}

// Sleep
sleep 30 // seconds

// Write file
writeFile file: 'config.json', text: '{"key": "value"}'

// Read file
def content = readFile 'config.json'

// File exists
fileExists('path/to/file')

// Directory
dir('subdir') {
    sh 'pwd'
}

// Delete directory
deleteDir()

// Archive artifacts
archiveArtifacts artifacts: '**/target/*.jar', fingerprint: true

// Stash files for later use
stash name: 'build-artifacts', includes: 'target/**'

// Unstash files
unstash 'build-artifacts'

// Publish test results
junit '**/target/surefire-reports/*.xml'

// Publish HTML reports
publishHTML([
    reportDir: 'coverage',
    reportFiles: 'index.html',
    reportName: 'Coverage Report'
])
```

### SCM Steps

```groovy
// Git checkout
checkout([
    $class: 'GitSCM',
    branches: [[name: '*/main']],
    userRemoteConfigs: [[
        url: 'https://github.com/example/repo.git',
        credentialsId: 'git-credentials'
    ]]
])

// Git operations
script {
    def gitCommit = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
    def gitBranch = env.GIT_BRANCH
    def gitAuthor = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
}
```

### Docker Steps

```groovy
// Build Docker image
script {
    docker.build("myapp:${env.BUILD_NUMBER}")
}

// Run in Docker container
docker.image('maven:3.8.1-jdk-11').inside {
    sh 'mvn clean package'
}

// Push to registry
script {
    docker.withRegistry('https://registry.example.com', 'docker-credentials') {
        def image = docker.build("myapp:${env.BUILD_NUMBER}")
        image.push()
        image.push('latest')
    }
}
```

### Credential Steps

```groovy
// Username/Password
withCredentials([usernamePassword(
    credentialsId: 'aws-creds',
    usernameVariable: 'AWS_ACCESS_KEY',
    passwordVariable: 'AWS_SECRET_KEY'
)]) {
    sh 'aws s3 ls'
}

// SSH Key
sshagent(['ssh-key-id']) {
    sh 'ssh user@server "command"'
}

// Secret text
withCredentials([string(credentialsId: 'api-token', variable: 'TOKEN')]) {
    sh 'curl -H "Authorization: Bearer $TOKEN" https://api.example.com'
}

// Secret file
withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
    sh 'kubectl get pods'
}
```

## Essential Plugins

### Core Plugins

| Plugin | Purpose | Usage |
|--------|---------|-------|
| **Pipeline** | Core pipeline functionality | Required |
| **Pipeline: Stage View** | Visualize pipeline stages | Recommended |
| **Pipeline: GitHub Groovy Libraries** | Shared libraries from GitHub | For reusable code |
| **Blue Ocean** | Modern UI for pipelines | Better visualization |

### SCM Plugins

| Plugin | Purpose |
|--------|---------|
| **Git** | Git repository integration |
| **GitHub** | GitHub-specific features |
| **GitLab** | GitLab integration |
| **Bitbucket** | Bitbucket integration |

### Build & Test Plugins

| Plugin | Purpose |
|--------|---------|
| **Maven Integration** | Maven builds |
| **Gradle** | Gradle builds |
| **NodeJS** | Node.js tool installer |
| **JUnit** | Test result publishing |
| **Cobertura** | Code coverage |
| **HTML Publisher** | Publish HTML reports |

### Deployment Plugins

| Plugin | Purpose |
|--------|---------|
| **Docker Pipeline** | Docker integration |
| **Kubernetes** | Kubernetes deployment |
| **AWS Steps** | AWS service integration |
| **Azure CLI** | Azure integration |
| **Terraform** | Infrastructure as Code |

### Notification Plugins

| Plugin | Purpose |
|--------|---------|
| **Slack Notification** | Slack integration |
| **Email Extension** | Advanced email notifications |
| **Teams Notification** | Microsoft Teams |

### Security Plugins

| Plugin | Purpose |
|--------|---------|
| **Credentials Binding** | Secure credential handling |
| **OWASP Dependency-Check** | Dependency vulnerability scanning |
| **SonarQube Scanner** | Code quality analysis |
| **Aqua Security Scanner** | Container security |

## Best Practices

### 1. Use Declarative Pipeline
```groovy
// Good: Declarative pipeline
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}

// Avoid: Scripted pipeline (unless necessary)
node {
    stage('Build') {
        sh 'mvn clean package'
    }
}
```

### 2. Define Agent at Stage Level
```groovy
// Good: Different agents for different stages
pipeline {
    agent none
    stages {
        stage('Build') {
            agent { docker 'maven:3.8.1-jdk-11' }
            steps {
                sh 'mvn package'
            }
        }
        stage('Deploy') {
            agent { label 'deploy-server' }
            steps {
                sh './deploy.sh'
            }
        }
    }
}
```

### 3. Use Shared Libraries
```groovy
// In Jenkinsfile
@Library('my-shared-library') _

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Call shared library function
                buildApplication()
            }
        }
    }
}
```

### 4. Externalize Configuration
```groovy
// Load configuration from file
def config = readJSON file: 'pipeline-config.json'

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh "mvn clean package -P${config.profile}"
            }
        }
    }
}
```

### 5. Implement Proper Error Handling
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    try {
                        sh 'mvn clean package'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        throw e
                    }
                }
            }
        }
    }
    post {
        failure {
            emailext body: "Build failed: ${env.BUILD_URL}",
                     subject: "Build #${env.BUILD_NUMBER} Failed",
                     to: 'team@example.com'
        }
    }
}
```

### 6. Use Parallel Execution
```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'mvn test'
                    }
                }
                stage('Integration Tests') {
                    steps {
                        sh 'mvn verify -P integration'
                    }
                }
                stage('UI Tests') {
                    steps {
                        sh 'npm run test:e2e'
                    }
                }
            }
        }
    }
}
```

### 7. Clean Workspace
```groovy
pipeline {
    agent any
    options {
        skipDefaultCheckout()
    }
    stages {
        stage('Checkout') {
            steps {
                cleanWs()
                checkout scm
            }
        }
    }
    post {
        cleanup {
            cleanWs()
        }
    }
}
```

### 8. Use Credentials Securely
```groovy
// Good: Use credential binding
withCredentials([string(credentialsId: 'api-key', variable: 'API_KEY')]) {
    sh 'curl -H "Authorization: $API_KEY" https://api.example.com'
}

// Bad: Never hardcode credentials
sh 'curl -H "Authorization: hardcoded-key" https://api.example.com'
```

### 9. Set Build Retention
```groovy
pipeline {
    agent any
    options {
        buildDiscarder(logRotator(
            numToKeepStr: '10',
            artifactNumToKeepStr: '5',
            daysToKeepStr: '30'
        ))
    }
}
```

### 10. Use Meaningful Stage Names
```groovy
// Good: Clear, descriptive names
stages {
    stage('Build Maven Artifacts') { }
    stage('Run Unit Tests') { }
    stage('Deploy to Staging') { }
}

// Bad: Vague names
stages {
    stage('Step 1') { }
    stage('Do stuff') { }
    stage('Deploy') { }
}
```

## Common Patterns

### Multi-Branch Pipeline Pattern
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
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
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?'
                sh './deploy.sh prod'
            }
        }
    }
}
```

### Matrix Build Pattern
```groovy
pipeline {
    agent none
    stages {
        stage('Build') {
            matrix {
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'linux', 'mac', 'windows'
                    }
                    axis {
                        name 'JAVA_VERSION'
                        values '8', '11', '17'
                    }
                }
                agent {
                    label "${PLATFORM}"
                }
                stages {
                    stage('Build') {
                        steps {
                            sh "mvn clean package -Djava.version=${JAVA_VERSION}"
                        }
                    }
                }
            }
        }
    }
}
```

### Deployment with Rollback Pattern
```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                script {
                    try {
                        sh './deploy.sh'
                        sh './health-check.sh'
                    } catch (Exception e) {
                        sh './rollback.sh'
                        error "Deployment failed, rolled back"
                    }
                }
            }
        }
    }
}
```

### Monorepo Pattern
```groovy
pipeline {
    agent any
    stages {
        stage('Detect Changes') {
            steps {
                script {
                    def changes = sh(
                        script: "git diff --name-only HEAD~1",
                        returnStdout: true
                    ).trim().split('\n')

                    env.BUILD_BACKEND = changes.any { it.startsWith('backend/') } ? 'true' : 'false'
                    env.BUILD_FRONTEND = changes.any { it.startsWith('frontend/') } ? 'true' : 'false'
                }
            }
        }
        stage('Build Backend') {
            when {
                expression { env.BUILD_BACKEND == 'true' }
            }
            steps {
                dir('backend') {
                    sh 'mvn clean package'
                }
            }
        }
        stage('Build Frontend') {
            when {
                expression { env.BUILD_FRONTEND == 'true' }
            }
            steps {
                dir('frontend') {
                    sh 'npm run build'
                }
            }
        }
    }
}
```

## Quick Reference Commands

```groovy
// Get build information
env.BUILD_NUMBER
env.BUILD_ID
env.BUILD_URL
currentBuild.result
currentBuild.duration

// Mark build as unstable
currentBuild.result = 'UNSTABLE'

// Get Git information
env.GIT_COMMIT
env.GIT_BRANCH
env.CHANGE_ID // PR number

// Workspace
env.WORKSPACE

// Get parameter values
params.PARAM_NAME

// Set build description
currentBuild.description = 'My custom description'

// Set build display name
currentBuild.displayName = "#${BUILD_NUMBER} - ${params.DEPLOY_ENV}"
```

## Resources

- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Pipeline Steps Reference](https://www.jenkins.io/doc/pipeline/steps/)
- [Pipeline Examples](https://www.jenkins.io/doc/pipeline/examples/)
- [Jenkins Plugin Index](https://plugins.jenkins.io/)

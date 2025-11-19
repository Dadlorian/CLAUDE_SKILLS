# IaC CI/CD Reference

## CI/CD Workflow Patterns

### GitOps Workflow
```
Developer → Git Push → CI Pipeline → Terraform Plan → PR Review → Merge → CD Pipeline → Terraform Apply → Monitor
```

### Pipeline Stages

1. **Validation**: Format, lint, validate syntax
2. **Security**: Scan for vulnerabilities and misconfigurations
3. **Plan**: Generate and review execution plan
4. **Policy**: Enforce organizational policies
5. **Approval**: Manual or automated approval gates
6. **Apply**: Execute infrastructure changes
7. **Test**: Verify deployment success
8. **Monitor**: Track infrastructure health

## GitHub Actions

### Complete Terraform Workflow

**.github/workflows/terraform.yml**
```yaml
name: Terraform CI/CD

on:
  pull_request:
    paths:
      - '**.tf'
      - '**.tfvars'
  push:
    branches:
      - main
      - develop

env:
  TF_VERSION: 1.6.0
  AWS_REGION: us-east-1

jobs:
  validate:
    name: Validate
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init -backend=false

      - name: Terraform Validate
        run: terraform validate

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Checkov Scan
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          output_format: sarif
          output_file_path: checkov.sarif

      - name: Upload Checkov results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: checkov.sarif

      - name: TFsec
        uses: aquasecurity/tfsec-pr-commenter-action@v1.2.0
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

  plan:
    name: Plan
    runs-on: ubuntu-latest
    needs: [validate, security]
    if: github.event_name == 'pull_request'
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan -out=tfplan -no-color
          terraform show -no-color tfplan > plan.txt

      - name: Comment Plan
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('plan.txt', 'utf8');
            const output = `#### Terraform Plan
            \`\`\`
            ${plan}
            \`\`\`
            `;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });

      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: tfplan

  apply:
    name: Apply
    runs-on: ubuntu-latest
    needs: plan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment:
      name: production
      url: https://console.aws.amazon.com
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Apply
        run: terraform apply -auto-approve

      - name: Notify Success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: 'Terraform apply completed successfully'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

      - name: Notify Failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: 'Terraform apply failed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Multi-Environment Workflow

```yaml
name: Multi-Environment Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod

jobs:
  deploy:
    name: Deploy to ${{ github.event.inputs.environment }}
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets[format('AWS_ROLE_ARN_{0}', github.event.inputs.environment)] }}
          aws-region: us-east-1

      - name: Terraform Init
        working-directory: ./environments/${{ github.event.inputs.environment }}
        run: terraform init

      - name: Terraform Plan
        working-directory: ./environments/${{ github.event.inputs.environment }}
        run: terraform plan -out=tfplan

      - name: Terraform Apply
        working-directory: ./environments/${{ github.event.inputs.environment }}
        run: terraform apply -auto-approve tfplan
```

## GitLab CI/CD

### .gitlab-ci.yml

```yaml
stages:
  - validate
  - security
  - plan
  - apply

variables:
  TF_VERSION: "1.6.0"
  TF_ROOT: ${CI_PROJECT_DIR}
  TF_ADDRESS: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/production

cache:
  key: "${CI_COMMIT_REF_SLUG}"
  paths:
    - ${TF_ROOT}/.terraform
    - ${TF_ROOT}/.terraform.lock.hcl

before_script:
  - cd ${TF_ROOT}
  - apk add --no-cache curl jq
  - wget https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip
  - unzip terraform_${TF_VERSION}_linux_amd64.zip
  - mv terraform /usr/local/bin/
  - terraform --version

validate:
  stage: validate
  script:
    - terraform fmt -check -recursive
    - terraform init -backend=false
    - terraform validate
  only:
    changes:
      - "**/*.tf"
      - "**/*.tfvars"

security:
  stage: security
  image: bridgecrew/checkov:latest
  script:
    - checkov -d . --framework terraform --output cli --output junitxml --output-file-path .
  artifacts:
    reports:
      junit: results_junitxml.xml
    paths:
      - results_checkov.json
  only:
    changes:
      - "**/*.tf"

plan:
  stage: plan
  script:
    - terraform init
    - terraform plan -out=tfplan
    - terraform show -json tfplan > tfplan.json
  artifacts:
    name: plan
    paths:
      - ${TF_ROOT}/tfplan
      - ${TF_ROOT}/tfplan.json
    expire_in: 1 week
  only:
    - merge_requests
    - main

apply:
  stage: apply
  script:
    - terraform init
    - terraform apply -auto-approve
  dependencies:
    - plan
  only:
    - main
  when: manual
  environment:
    name: production
    on_stop: destroy

destroy:
  stage: apply
  script:
    - terraform init
    - terraform destroy -auto-approve
  when: manual
  only:
    - main
  environment:
    name: production
    action: stop
```

### GitLab Terraform HTTP Backend

```hcl
terraform {
  backend "http" {
    address        = "https://gitlab.example.com/api/v4/projects/PROJECT_ID/terraform/state/STATE_NAME"
    lock_address   = "https://gitlab.example.com/api/v4/projects/PROJECT_ID/terraform/state/STATE_NAME/lock"
    unlock_address = "https://gitlab.example.com/api/v4/projects/PROJECT_ID/terraform/state/STATE_NAME/lock"
    username       = "gitlab-ci-token"
    password       = var.gitlab_token
    lock_method    = "POST"
    unlock_method  = "DELETE"
    retry_wait_min = 5
  }
}
```

## Azure DevOps

### azure-pipelines.yml

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - '**/*.tf'
      - '**/*.tfvars'

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: terraform-credentials
  - name: terraformVersion
    value: '1.6.0'

stages:
  - stage: Validate
    jobs:
      - job: Validate
        steps:
          - task: TerraformInstaller@0
            inputs:
              terraformVersion: $(terraformVersion)

          - task: Bash@3
            displayName: 'Terraform Format Check'
            inputs:
              targetType: 'inline'
              script: |
                terraform fmt -check -recursive

          - task: TerraformTaskV4@4
            displayName: 'Terraform Init'
            inputs:
              provider: 'azurerm'
              command: 'init'
              backendServiceArm: 'Azure Service Connection'
              backendAzureRmResourceGroupName: 'terraform-state-rg'
              backendAzureRmStorageAccountName: 'tfstate'
              backendAzureRmContainerName: 'tfstate'
              backendAzureRmKey: 'terraform.tfstate'

          - task: TerraformTaskV4@4
            displayName: 'Terraform Validate'
            inputs:
              provider: 'azurerm'
              command: 'validate'

  - stage: Security
    dependsOn: Validate
    jobs:
      - job: SecurityScan
        steps:
          - task: Bash@3
            displayName: 'Run Checkov'
            inputs:
              targetType: 'inline'
              script: |
                pip3 install checkov
                checkov -d . --framework terraform --output cli --output junitxml

          - task: PublishTestResults@2
            displayName: 'Publish Checkov Results'
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: 'results_junitxml.xml'

  - stage: Plan
    dependsOn: Security
    condition: and(succeeded(), ne(variables['Build.Reason'], 'PullRequest'))
    jobs:
      - job: Plan
        steps:
          - task: TerraformInstaller@0
            inputs:
              terraformVersion: $(terraformVersion)

          - task: TerraformTaskV4@4
            displayName: 'Terraform Init'
            inputs:
              provider: 'azurerm'
              command: 'init'
              backendServiceArm: 'Azure Service Connection'
              backendAzureRmResourceGroupName: 'terraform-state-rg'
              backendAzureRmStorageAccountName: 'tfstate'
              backendAzureRmContainerName: 'tfstate'
              backendAzureRmKey: 'terraform.tfstate'

          - task: TerraformTaskV4@4
            displayName: 'Terraform Plan'
            inputs:
              provider: 'azurerm'
              command: 'plan'
              environmentServiceNameAzureRM: 'Azure Service Connection'
              commandOptions: '-out=tfplan'

          - task: PublishPipelineArtifact@1
            displayName: 'Publish Plan'
            inputs:
              targetPath: '$(System.DefaultWorkingDirectory)/tfplan'
              artifact: 'terraform-plan'

  - stage: Apply
    dependsOn: Plan
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: Apply
        environment: 'Production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: DownloadPipelineArtifact@2
                  displayName: 'Download Plan'
                  inputs:
                    artifact: 'terraform-plan'

                - task: TerraformInstaller@0
                  inputs:
                    terraformVersion: $(terraformVersion)

                - task: TerraformTaskV4@4
                  displayName: 'Terraform Init'
                  inputs:
                    provider: 'azurerm'
                    command: 'init'
                    backendServiceArm: 'Azure Service Connection'
                    backendAzureRmResourceGroupName: 'terraform-state-rg'
                    backendAzureRmStorageAccountName: 'tfstate'
                    backendAzureRmContainerName: 'tfstate'
                    backendAzureRmKey: 'terraform.tfstate'

                - task: TerraformTaskV4@4
                  displayName: 'Terraform Apply'
                  inputs:
                    provider: 'azurerm'
                    command: 'apply'
                    environmentServiceNameAzureRM: 'Azure Service Connection'
                    commandOptions: '-auto-approve tfplan'
```

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any

    parameters {
        choice(
            name: 'ACTION',
            choices: ['plan', 'apply', 'destroy'],
            description: 'Terraform action to perform'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Environment to deploy to'
        )
    }

    environment {
        TF_VERSION = '1.6.0'
        AWS_REGION = 'us-east-1'
        TF_VAR_environment = "${params.ENVIRONMENT}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                script {
                    sh '''
                        wget https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip
                        unzip -o terraform_${TF_VERSION}_linux_amd64.zip
                        chmod +x terraform
                        mv terraform /usr/local/bin/
                    '''
                }
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    terraform fmt -check -recursive
                    terraform init -backend=false
                    terraform validate
                '''
            }
        }

        stage('Security Scan') {
            parallel {
                stage('Checkov') {
                    steps {
                        sh '''
                            pip3 install checkov
                            checkov -d . --framework terraform
                        '''
                    }
                }
                stage('TFsec') {
                    steps {
                        sh '''
                            curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
                            tfsec .
                        '''
                    }
                }
            }
        }

        stage('Initialize') {
            steps {
                withCredentials([
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: "aws-credentials-${params.ENVIRONMENT}"
                    ]
                ]) {
                    sh "terraform init"
                }
            }
        }

        stage('Plan') {
            when {
                expression { params.ACTION == 'plan' || params.ACTION == 'apply' }
            }
            steps {
                withCredentials([
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: "aws-credentials-${params.ENVIRONMENT}"
                    ]
                ]) {
                    script {
                        sh "terraform plan -out=tfplan"

                        // Save plan for review
                        sh "terraform show -no-color tfplan > tfplan.txt"
                        archiveArtifacts artifacts: 'tfplan.txt', allowEmptyArchive: false
                    }
                }
            }
        }

        stage('Approval') {
            when {
                expression { params.ACTION == 'apply' && params.ENVIRONMENT == 'prod' }
            }
            steps {
                script {
                    input message: 'Apply Terraform changes to production?',
                          ok: 'Apply',
                          submitter: 'approvers-group'
                }
            }
        }

        stage('Apply') {
            when {
                expression { params.ACTION == 'apply' }
            }
            steps {
                withCredentials([
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: "aws-credentials-${params.ENVIRONMENT}"
                    ]
                ]) {
                    sh "terraform apply -auto-approve tfplan"
                }
            }
        }

        stage('Destroy') {
            when {
                expression { params.ACTION == 'destroy' }
            }
            steps {
                script {
                    input message: "Destroy infrastructure in ${params.ENVIRONMENT}?",
                          ok: 'Destroy',
                          submitter: 'admin-group'
                }
                withCredentials([
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: "aws-credentials-${params.ENVIRONMENT}"
                    ]
                ]) {
                    sh "terraform destroy -auto-approve"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            slackSend(
                color: 'good',
                message: "Terraform ${params.ACTION} succeeded for ${params.ENVIRONMENT}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Terraform ${params.ACTION} failed for ${params.ENVIRONMENT}"
            )
        }
    }
}
```

## Atlantis

### atlantis.yaml

```yaml
version: 3

automerge: false
delete_source_branch_on_merge: true

projects:
  - name: production-vpc
    dir: environments/prod/vpc
    workspace: prod
    terraform_version: v1.6.0
    autoplan:
      when_modified:
        - "**/*.tf"
        - "**/*.tfvars"
      enabled: true
    apply_requirements:
      - approved
      - mergeable
    workflow: production

  - name: staging-vpc
    dir: environments/staging/vpc
    workspace: staging
    terraform_version: v1.6.0
    autoplan:
      when_modified:
        - "**/*.tf"
      enabled: true
    workflow: default

workflows:
  default:
    plan:
      steps:
        - init
        - plan

    apply:
      steps:
        - apply

  production:
    plan:
      steps:
        - init
        - run: terraform fmt -check
        - run: checkov -d .
        - plan:
            extra_args: ["-lock=true"]

    apply:
      steps:
        - run: echo "Applying to production..."
        - apply

policies:
  owners:
    users:
      - infrastructure-team
  policy_sets:
    - name: production-policies
      path: policies/production/
      source: local
```

### Atlantis Server Setup

```yaml
# docker-compose.yml
version: '3'

services:
  atlantis:
    image: ghcr.io/runatlantis/atlantis:latest
    ports:
      - "4141:4141"
    environment:
      - ATLANTIS_GH_USER=atlantis-bot
      - ATLANTIS_GH_TOKEN=${GITHUB_TOKEN}
      - ATLANTIS_GH_WEBHOOK_SECRET=${WEBHOOK_SECRET}
      - ATLANTIS_REPO_ALLOWLIST=github.com/organization/*
      - ATLANTIS_ATLANTIS_URL=https://atlantis.example.com
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./atlantis-data:/atlantis-data
    command: server
```

## Terraform Cloud

### Configuration

```hcl
terraform {
  cloud {
    organization = "my-org"

    workspaces {
      name = "production-infrastructure"
    }
  }
}
```

### API-Driven Workflow

```bash
#!/bin/bash

# Create workspace
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @payload.json \
  https://app.terraform.io/api/v2/organizations/my-org/workspaces

# Create configuration version
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @payload.json \
  https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/configuration-versions

# Upload configuration
tar -czf config.tar.gz *.tf
curl \
  --header "Content-Type: application/octet-stream" \
  --request PUT \
  --data-binary @config.tar.gz \
  $UPLOAD_URL

# Create run
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @payload.json \
  https://app.terraform.io/api/v2/runs

# Apply run
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  https://app.terraform.io/api/v2/runs/$RUN_ID/actions/apply
```

## Drift Detection

### Scheduled Drift Detection (GitHub Actions)

```yaml
name: Drift Detection

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - name: Terraform Init
        run: terraform init

      - name: Detect Drift
        id: drift
        run: |
          terraform plan -detailed-exitcode -no-color > plan.txt
          EXIT_CODE=$?
          echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT
        continue-on-error: true

      - name: Report Drift
        if: steps.drift.outputs.exit_code == '2'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('plan.txt', 'utf8');

            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Infrastructure Drift Detected',
              body: `## Drift Detection Alert\n\nDrift detected in infrastructure:\n\n\`\`\`\n${plan}\n\`\`\``,
              labels: ['infrastructure', 'drift']
            });

      - name: Notify Slack
        if: steps.drift.outputs.exit_code == '2'
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "Infrastructure drift detected!",
              attachments: [{
                color: 'danger',
                text: 'Drift has been detected in the infrastructure. Please review.'
              }]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Best Practices

### 1. Separate Plan and Apply
Always review plans before applying

### 2. Use Remote State
Store state remotely with locking

### 3. Implement Approval Gates
Require manual approval for production

### 4. Run Security Scans
Automated security scanning in every pipeline

### 5. Use Workspaces or Directories
Separate environments properly

### 6. Version Lock Files
Commit `.terraform.lock.hcl`

### 7. Implement Drift Detection
Regular scheduled drift detection

### 8. Use OIDC for Authentication
Avoid long-lived credentials

### 9. Comprehensive Logging
Log all changes and who made them

### 10. Rollback Strategy
Plan for failure scenarios

## Resources

- GitHub Actions: docs.github.com/actions
- GitLab CI/CD: docs.gitlab.com/ee/ci
- Azure DevOps: docs.microsoft.com/azure/devops
- Jenkins: jenkins.io/doc
- Atlantis: runatlantis.io
- Terraform Cloud: terraform.io/cloud

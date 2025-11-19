# Helm Charts Reference

## Helm Overview

Helm is the package manager for Kubernetes, providing templating, versioning, and lifecycle management for Kubernetes applications.

### Key Concepts

- **Chart**: Package containing Kubernetes resource definitions
- **Release**: Instance of a chart running in a cluster
- **Repository**: Collection of charts
- **Values**: Configuration data for customizing charts

### Helm 3 Changes
- No Tiller (server-side component removed)
- Three-way strategic merge patches
- Release namespaces
- Chart dependencies in Chart.yaml
- JSON Schema validation
- OCI registry support

## Installation

```bash
# Install Helm 3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Or via package manager
brew install helm  # macOS
choco install kubernetes-helm  # Windows
snap install helm --classic  # Linux

# Verify
helm version
```

## Basic Commands

### Repository Management

```bash
# Add repository
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami

# List repositories
helm repo list

# Update repositories
helm repo update

# Search for charts
helm search repo nginx
helm search hub nginx  # Search Artifact Hub

# Remove repository
helm repo remove bitnami
```

### Installing Charts

```bash
# Install chart
helm install myrelease bitnami/nginx

# Install with custom name
helm install my-nginx bitnami/nginx

# Install in specific namespace
helm install my-nginx bitnami/nginx -n production --create-namespace

# Install with custom values
helm install my-nginx bitnami/nginx --set replicaCount=3
helm install my-nginx bitnami/nginx -f custom-values.yaml

# Dry run (test without installing)
helm install my-nginx bitnami/nginx --dry-run --debug

# Generate manifest without installing
helm template my-nginx bitnami/nginx

# Install from local chart
helm install my-nginx ./nginx-chart
```

### Managing Releases

```bash
# List releases
helm list
helm list -n production
helm list --all-namespaces

# Get release status
helm status my-nginx

# Get release values
helm get values my-nginx
helm get values my-nginx --all

# Get release manifest
helm get manifest my-nginx

# Upgrade release
helm upgrade my-nginx bitnami/nginx
helm upgrade my-nginx bitnami/nginx --set replicaCount=5
helm upgrade my-nginx bitnami/nginx -f new-values.yaml

# Install or upgrade (atomic)
helm upgrade --install my-nginx bitnami/nginx

# Rollback release
helm rollback my-nginx
helm rollback my-nginx 1  # Rollback to revision 1

# Release history
helm history my-nginx

# Uninstall release
helm uninstall my-nginx
helm uninstall my-nginx --keep-history
```

## Chart Structure

### Directory Layout

```
mychart/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration values
├── values.schema.json  # JSON Schema for values validation
├── charts/             # Chart dependencies
├── templates/          # Template files
│   ├── NOTES.txt      # Usage notes (optional)
│   ├── _helpers.tpl   # Template helpers
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── tests/         # Test files
│       └── test-connection.yaml
└── .helmignore        # Files to ignore when packaging
```

### Chart.yaml

```yaml
apiVersion: v2
name: mychart
description: A Helm chart for my application
type: application  # or 'library'
version: 0.1.0  # Chart version (SemVer)
appVersion: "1.0.0"  # Application version

# Optional fields
keywords:
  - web
  - nginx
home: https://example.com
sources:
  - https://github.com/example/mychart
maintainers:
  - name: John Doe
    email: john@example.com
    url: https://example.com
icon: https://example.com/icon.png
deprecated: false
annotations:
  category: Web

# Dependencies
dependencies:
  - name: mysql
    version: "9.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: mysql.enabled
    tags:
      - database
  - name: redis
    version: "17.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

### values.yaml

```yaml
# Default values for mychart
replicaCount: 1

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: ""  # Overrides the image tag whose default is chart appVersion

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}
```

### values.schema.json

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    },
    "image": {
      "type": "object",
      "properties": {
        "repository": {
          "type": "string"
        },
        "tag": {
          "type": "string"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      },
      "required": ["repository"]
    }
  },
  "required": ["replicaCount", "image"]
}
```

## Template Syntax

### Basic Templating

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ .Release.Name }}-pod
  labels:
    app: {{ .Chart.Name }}
    version: {{ .Chart.Version }}
    release: {{ .Release.Name }}
spec:
  containers:
  - name: {{ .Chart.Name }}
    image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
    ports:
    - containerPort: {{ .Values.service.port }}
```

### Built-in Objects

```yaml
# .Release
{{ .Release.Name }}       # Release name
{{ .Release.Namespace }}  # Namespace
{{ .Release.Service }}    # Service (always "Helm")
{{ .Release.IsUpgrade }}  # True if upgrade/rollback
{{ .Release.IsInstall }}  # True if install

# .Chart
{{ .Chart.Name }}         # Chart name
{{ .Chart.Version }}      # Chart version
{{ .Chart.AppVersion }}   # App version

# .Values
{{ .Values.replicaCount }}
{{ .Values.image.repository }}

# .Capabilities
{{ .Capabilities.KubeVersion }}
{{ .Capabilities.APIVersions.Has "apps/v1" }}

# .Template
{{ .Template.Name }}      # Template file name
{{ .Template.BasePath }}  # Template directory path

# .Files
{{ .Files.Get "config.yaml" }}
{{ .Files.Glob "configs/*.yaml" }}
```

### Template Functions

**String Functions**:
```yaml
{{ .Values.name | upper }}  # UPPERCASE
{{ .Values.name | lower }}  # lowercase
{{ .Values.name | title }}  # Title Case
{{ .Values.name | trim }}   # Remove whitespace
{{ .Values.name | quote }}  # Add quotes
{{ .Values.name | default "default-value" }}
{{ .Values.name | required "name is required" }}
{{ printf "%s-%s" .Release.Name .Chart.Name }}
```

**Type Conversion**:
```yaml
{{ .Values.port | int }}
{{ .Values.enabled | toString }}
{{ .Values.data | toJson }}
{{ .Values.data | toYaml }}
{{ .Values.data | toPrettyJson }}
```

**Logic**:
```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
...
{{- end }}

{{- if and .Values.mysql.enabled .Values.redis.enabled }}
...
{{- end }}

{{- if or .Values.dev .Values.staging }}
...
{{- end }}

{{- if not .Values.production }}
...
{{- end }}
```

**Loops**:
```yaml
{{- range .Values.environments }}
- name: {{ . }}
{{- end }}

{{- range $key, $value := .Values.config }}
{{ $key }}: {{ $value }}
{{- end }}
```

**With (Scope)**:
```yaml
{{- with .Values.ingress }}
  {{- if .enabled }}
  annotations:
    {{- range $key, $value := .annotations }}
    {{ $key }}: {{ $value }}
    {{- end }}
  {{- end }}
{{- end }}
```

### Named Templates (_helpers.tpl)

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "mychart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "mychart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "mychart.labels" -}}
helm.sh/chart: {{ include "mychart.chart" . }}
{{ include "mychart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "mychart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

**Using Named Templates**:
```yaml
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
```

## Chart Dependencies

### Defining Dependencies

**Chart.yaml**:
```yaml
dependencies:
  - name: mysql
    version: "9.3.0"
    repository: https://charts.bitnami.com/bitnami
    condition: mysql.enabled
    tags:
      - database
  - name: redis
    version: "17.0.0"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
  - name: common
    version: "1.x.x"
    repository: https://charts.bitnami.com/bitnami
```

### Managing Dependencies

```bash
# Download dependencies
helm dependency update ./mychart

# List dependencies
helm dependency list ./mychart

# Build dependencies (creates charts/ directory)
helm dependency build ./mychart
```

### Overriding Dependency Values

**values.yaml**:
```yaml
mysql:
  enabled: true
  auth:
    rootPassword: "supersecret"
    database: "myapp"
  primary:
    persistence:
      enabled: true
      size: 10Gi

redis:
  enabled: true
  auth:
    enabled: false
  master:
    persistence:
      enabled: false
```

## Advanced Features

### Hooks

**Types**:
- `pre-install`, `post-install`
- `pre-delete`, `post-delete`
- `pre-upgrade`, `post-upgrade`
- `pre-rollback`, `post-rollback`
- `test`

**Example**:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "mychart.fullname" . }}-migration
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "1"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      containers:
      - name: migration
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        command: ["./migrate.sh"]
      restartPolicy: Never
```

### Tests

**templates/tests/test-connection.yaml**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "mychart.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
spec:
  containers:
  - name: wget
    image: busybox
    command: ['wget']
    args: ['{{ include "mychart.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

**Run Tests**:
```bash
helm test my-release
```

### Chart Development

```bash
# Create new chart
helm create mychart

# Lint chart
helm lint ./mychart

# Package chart
helm package ./mychart

# Install from package
helm install my-release ./mychart-0.1.0.tgz

# Verify chart
helm verify mychart-0.1.0.tgz

# Debug template rendering
helm template my-release ./mychart --debug
helm install my-release ./mychart --dry-run --debug
```

### Chart Repository

```bash
# Package chart
helm package ./mychart

# Generate index
helm repo index .

# Serve local repository
helm serve --address localhost:8879

# Add local repository
helm repo add myrepo http://localhost:8879
```

### OCI Registry (Helm 3.8+)

```bash
# Login to registry
echo $PASSWORD | helm registry login -u myuser --password-stdin myregistry.azurecr.io

# Save chart
helm chart save ./mychart myregistry.azurecr.io/helm/mychart:0.1.0

# Push chart
helm push ./mychart-0.1.0.tgz oci://myregistry.azurecr.io/helm

# Pull chart
helm pull oci://myregistry.azurecr.io/helm/mychart --version 0.1.0

# Install from OCI
helm install my-release oci://myregistry.azurecr.io/helm/mychart --version 0.1.0
```

## Best Practices

### Chart Design
- Use semantic versioning
- Provide sensible defaults
- Make resources configurable
- Follow Kubernetes naming conventions
- Use labels consistently
- Implement resource limits
- Add helpful NOTES.txt

### Templates
- Use `_helpers.tpl` for common templates
- Prefer `include` over `template`
- Use `nindent` for proper YAML indentation
- Add `-` to control whitespace ({{- -}})
- Use `required` for mandatory values
- Validate with schema (values.schema.json)

### Values
- Use flat structure when possible
- Group related values
- Provide clear documentation
- Use consistent naming
- Set secure defaults
- Make everything configurable

### Security
- Don't hardcode secrets
- Use secure defaults (non-root, read-only)
- Implement Pod Security Standards
- Add security contexts
- Use network policies
- Enable RBAC

### Documentation
- Comprehensive README.md
- Document all values
- Provide examples
- Add upgrade notes
- Include NOTES.txt for post-install instructions

## Popular Charts

### Bitnami Charts
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

# Databases
helm install mysql bitnami/mysql
helm install postgresql bitnami/postgresql
helm install mongodb bitnami/mongodb
helm install redis bitnami/redis

# Applications
helm install wordpress bitnami/wordpress
helm install drupal bitnami/drupal
helm install ghost bitnami/ghost

# Infrastructure
helm install nginx bitnami/nginx
helm install rabbitmq bitnami/rabbitmq
helm install kafka bitnami/kafka
```

### Other Popular Charts
```bash
# Prometheus/Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# NGINX Ingress
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx

# Cert-Manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager --set installCRDs=true

# ArgoCD
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd
```

## Troubleshooting

```bash
# Debug template rendering
helm template my-release ./mychart --debug

# Check values
helm get values my-release

# Check manifest
helm get manifest my-release

# List all releases (including failed)
helm list --all

# Get release history
helm history my-release

# Check hooks
helm get hooks my-release

# Verbose output
helm install my-release ./mychart --debug --dry-run

# Lint before install
helm lint ./mychart --strict
```

## References

- [Helm Documentation](https://helm.sh/docs/)
- [Artifact Hub](https://artifacthub.io/)
- [Helm Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Template Function List](https://helm.sh/docs/chart_template_guide/function_list/)

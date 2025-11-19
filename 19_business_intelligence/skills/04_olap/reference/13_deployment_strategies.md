# OLAP Deployment Strategies

## Overview

Comprehensive strategies for deploying OLAP solutions across environments, including automation, testing, and rollback procedures.

## Deployment Environments

### Environment Structure
```
Development:
- Rapid changes
- Sample/subset data
- Frequent processing
- Testing new features

Test/QA:
- Production-like configuration
- Full or representative data
- Performance testing
- User acceptance testing

Staging:
- Mirror of production
- Final validation
- Production data volume
- Pre-production testing

Production:
- Live system
- Full data
- Monitored closely
- Change-controlled
```

## Deployment Methods

### 1. SSAS Deployment Wizard

```powershell
# Deploy using Microsoft.AnalysisServices.Deployment.exe

$deploymentUtility = "C:\Program Files\Microsoft SQL Server\150\Tools\Binn\ManagementStudio\Microsoft.AnalysisServices.Deployment.exe"

# Generate deployment files in SSDT
# Then deploy

& $deploymentUtility `
    "/s:D:\Projects\SalesCube\bin\SalesCube.asdatabase" `
    "/t:Production Server" `
    "/d:SalesCube" `
    "/o:D:\Deployment\deployment.log"
```

### 2. XMLA Scripts

```xml
<!-- Deploy using XMLA -->
<Batch xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
  <Alter AllowCreate="true" ObjectExpansion="ExpandFull">
    <Object>
      <DatabaseID>SalesCube</DatabaseID>
    </Object>
    <ObjectDefinition>
      <Database xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <ID>SalesCube</ID>
        <Name>Sales Cube</Name>
        <!-- Full database definition -->
      </Database>
    </ObjectDefinition>
  </Alter>
</Batch>
```

```powershell
# Execute XMLA
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("ProductionServer")

$xmla = Get-Content "D:\Deployment\SalesCube.xmla"
$server.Execute($xmla)

$server.Disconnect()
```

### 3. TMSL (Tabular Model Scripting Language)

```json
// Create database
{
  "create": {
    "database": {
      "name": "SalesCube",
      "compatibilityLevel": 1500,
      "model": {
        "culture": "en-US",
        "dataSources": [...],
        "tables": [...],
        "relationships": [...]
      }
    }
  }
}
```

```powershell
# Execute TMSL
$tmsl = Get-Content "D:\Deployment\SalesCube.tmsl" -Raw

Invoke-ASCmd `
    -Server "ProductionServer" `
    -Query $tmsl `
    -ServicePrincipal `
    -TenantId $tenantId `
    -ApplicationId $appId `
    -CertificateThumbprint $thumbprint
```

### 4. AMO (Analysis Management Objects)

```csharp
using Microsoft.AnalysisServices;
using Microsoft.AnalysisServices.Tabular;

// Connect to server
Server server = new Server();
server.Connect("ProductionServer");

// Load database definition from file
Database db = JsonSerializer.Deserialize<Database>(
    File.ReadAllText("SalesCube.json")
);

// Deploy
if (server.Databases.Contains(db.Name))
{
    // Update existing
    server.Databases[db.Name].Update(UpdateOptions.ExpandFull);
}
else
{
    // Create new
    server.Databases.Add(db);
    db.Update(UpdateOptions.ExpandFull);
}

server.Disconnect();
```

### 5. Power BI Deployment

```powershell
# Install Power BI cmdlets
Install-Module -Name MicrosoftPowerBIMgmt

# Connect
Connect-PowerBIServiceAccount

# Deploy PBIX
New-PowerBIReport `
    -Path "D:\Reports\SalesReport.pbix" `
    -WorkspaceId "12345678-1234-1234-1234-123456789012" `
    -ConflictAction CreateOrOverwrite

# Update dataset refresh
$datasetId = (Get-PowerBIDataset -WorkspaceId $workspaceId -Name "Sales").Id

Invoke-PowerBIRestMethod `
    -Url "datasets/$datasetId/refreshes" `
    -Method Post `
    -Body "{}"
```

## Deployment Automation

### CI/CD Pipeline (Azure DevOps)

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'windows-latest'

variables:
  solution: '**/*.sln'
  buildPlatform: 'Any CPU'
  buildConfiguration: 'Release'

stages:
- stage: Build
  jobs:
  - job: BuildCube
    steps:
    - task: MSBuild@1
      inputs:
        solution: '$(solution)'
        platform: '$(buildPlatform)'
        configuration: '$(buildConfiguration)'

    - task: PublishBuildArtifacts@1
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'drop'

- stage: DeployDev
  dependsOn: Build
  condition: eq(variables['Build.SourceBranch'], 'refs/heads/develop')
  jobs:
  - deployment: DeployToDev
    environment: 'Development'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: PowerShell@2
            inputs:
              targetType: 'filePath'
              filePath: '$(Pipeline.Workspace)/drop/Deploy-SSAS.ps1'
              arguments: '-Server "DevServer" -Database "SalesCube"'

- stage: DeployProd
  dependsOn: Build
  condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')
  jobs:
  - deployment: DeployToProd
    environment: 'Production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: PowerShell@2
            inputs:
              targetType: 'filePath'
              filePath: '$(Pipeline.Workspace)/drop/Deploy-SSAS.ps1'
              arguments: '-Server "ProdServer" -Database "SalesCube"'

          - task: PowerShell@2
            displayName: 'Process Database'
            inputs:
              targetType: 'inline'
              script: |
                Invoke-ProcessASDatabase `
                  -Server "ProdServer" `
                  -Database "SalesCube" `
                  -ProcessType "ProcessFull"
```

### Deployment Script

```powershell
# Deploy-SSAS.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$Server,

    [Parameter(Mandatory=$true)]
    [string]$Database,

    [string]$BackupPath = "D:\Backup",
    [switch]$BackupBeforeDeploy,
    [switch]$ProcessAfterDeploy
)

# Load assemblies
[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices")

try {
    Write-Host "Connecting to $Server..."
    $srv = New-Object Microsoft.AnalysisServices.Server
    $srv.Connect($Server)

    # Backup existing database
    if ($BackupBeforeDeploy -and $srv.Databases.Contains($Database)) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = Join-Path $BackupPath "$Database_$timestamp.abf"

        Write-Host "Creating backup: $backupFile"
        $srv.Databases[$Database].Backup($backupFile, $true)
    }

    # Deploy database
    Write-Host "Deploying $Database..."

    $xmla = Get-Content "$PSScriptRoot\$Database.xmla" -Raw
    $results = $srv.Execute($xmla)

    # Check for errors
    foreach ($result in $results) {
        foreach ($message in $result.Messages) {
            if ($message.GetType().Name -eq "XmlaError") {
                throw "Deployment error: $($message.Description)"
            }
        }
    }

    Write-Host "Deployment successful"

    # Process database
    if ($ProcessAfterDeploy) {
        Write-Host "Processing database..."
        $db = $srv.Databases[$Database]
        $db.Process([Microsoft.AnalysisServices.ProcessType]::ProcessFull)
        Write-Host "Processing complete"
    }

    $srv.Disconnect()
    Write-Host "Deployment completed successfully"
}
catch {
    Write-Error "Deployment failed: $_"
    throw
}
```

## Configuration Management

### Environment-Specific Settings

```xml
<!-- ConfigurationSettings.dev.xml -->
<ConfigurationSettings>
  <Database>
    <DataSourceImpersonationInfo>
      <ImpersonationMode>ImpersonateServiceAccount</ImpersonationMode>
    </DataSourceImpersonationInfo>
    <ProcessingOption>ParallelOptions>
      <MaxParallel>4</MaxParallel>
    </ProcessingOption>
  </Database>
</ConfigurationSettings>

<!-- ConfigurationSettings.prod.xml -->
<ConfigurationSettings>
  <Database>
    <DataSourceImpersonationInfo>
      <ImpersonationMode>ImpersonateAccount</ImpersonationMode>
      <Account>DOMAIN\SSASService</Account>
    </DataSourceImpersonationInfo>
    <ProcessingOption>
      <ParallelOptions>
        <MaxParallel>16</MaxParallel>
      </ParallelOptions>
    </ProcessingOption>
  </Database>
</ConfigurationSettings>
```

### Apply Configuration

```powershell
# Apply environment-specific configuration
param(
    [string]$Environment = "dev"
)

$configFile = "ConfigurationSettings.$Environment.xml"
[xml]$config = Get-Content $configFile

$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("localhost")

$db = $server.Databases["SalesCube"]

# Apply data source settings
foreach ($ds in $db.DataSources) {
    $ds.ImpersonationInfo.ImpersonationMode =
        $config.ConfigurationSettings.Database.DataSourceImpersonationInfo.ImpersonationMode

    if ($config.ConfigurationSettings.Database.DataSourceImpersonationInfo.Account) {
        $ds.ImpersonationInfo.Account =
            $config.ConfigurationSettings.Database.DataSourceImpersonationInfo.Account
    }

    $ds.Update()
}

$server.Disconnect()
```

## Testing Strategy

### Pre-Deployment Testing

```powershell
# Test-Deployment.ps1
function Test-Deployment {
    param(
        [string]$Server,
        [string]$Database
    )

    $testResults = @()

    # Test 1: Connection
    try {
        $srv = New-Object Microsoft.AnalysisServices.Server
        $srv.Connect($Server)
        $testResults += @{Test="Connection"; Result="Pass"}
        $srv.Disconnect()
    }
    catch {
        $testResults += @{Test="Connection"; Result="Fail"; Error=$_.Exception.Message}
        return $testResults
    }

    # Test 2: Database exists
    $srv.Connect($Server)
    if ($srv.Databases.Contains($Database)) {
        $testResults += @{Test="DatabaseExists"; Result="Pass"}
    }
    else {
        $testResults += @{Test="DatabaseExists"; Result="Fail"}
        return $testResults
    }

    # Test 3: All dimensions exist
    $db = $srv.Databases[$Database]
    $requiredDimensions = @("Date", "Product", "Customer", "Geography")
    $missingDimensions = @()

    foreach ($dim in $requiredDimensions) {
        if (-not $db.Dimensions.Contains($dim)) {
            $missingDimensions += $dim
        }
    }

    if ($missingDimensions.Count -eq 0) {
        $testResults += @{Test="Dimensions"; Result="Pass"}
    }
    else {
        $testResults += @{Test="Dimensions"; Result="Fail"; Missing=$missingDimensions}
    }

    # Test 4: Measure groups exist
    $cube = $db.Cubes[0]
    if ($cube.MeasureGroups.Count -gt 0) {
        $testResults += @{Test="MeasureGroups"; Result="Pass"; Count=$cube.MeasureGroups.Count}
    }
    else {
        $testResults += @{Test="MeasureGroups"; Result="Fail"}
    }

    # Test 5: Run test query
    try {
        $result = $srv.ExecuteCaptureLog("
            SELECT
                [Measures].[Sales Amount] ON 0
            FROM [Sales]
        ", $true)

        $testResults += @{Test="Query"; Result="Pass"}
    }
    catch {
        $testResults += @{Test="Query"; Result="Fail"; Error=$_.Exception.Message}
    }

    $srv.Disconnect()
    return $testResults
}

# Run tests
$results = Test-Deployment -Server "TestServer" -Database "SalesCube"
$results | Format-Table -Auto

# Fail deployment if any tests fail
if ($results | Where-Object { $_.Result -eq "Fail" }) {
    throw "Deployment tests failed"
}
```

### Data Validation

```sql
-- Validate row counts match
DECLARE @CubeCount BIGINT
DECLARE @SourceCount BIGINT

-- Get cube count (execute via XMLA/MDX)
-- SELECT COUNT(*) FROM FactSales should match

SET @SourceCount = (SELECT COUNT(*) FROM FactSales)

IF @CubeCount <> @SourceCount
    RAISERROR('Row count mismatch: Cube=%d, Source=%d', 16, 1, @CubeCount, @SourceCount)

-- Validate measure totals
DECLARE @CubeSalesTotal MONEY
DECLARE @SourceSalesTotal MONEY

SET @SourceSalesTotal = (SELECT SUM(SalesAmount) FROM FactSales)

IF ABS(@CubeSalesTotal - @SourceSalesTotal) > 0.01
    RAISERROR('Sales total mismatch', 16, 1)
```

## Rollback Procedures

### Automated Rollback

```powershell
# Rollback-Deployment.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$Server,

    [Parameter(Mandatory=$true)]
    [string]$Database,

    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

try {
    Write-Host "Rolling back $Database from $BackupFile"

    $srv = New-Object Microsoft.AnalysisServices.Server
    $srv.Connect($Server)

    # Delete current database
    if ($srv.Databases.Contains($Database)) {
        $srv.Databases[$Database].Drop()
    }

    # Restore from backup
    $restoreInfo = New-Object Microsoft.AnalysisServices.RestoreInfo
    $restoreInfo.File = $BackupFile
    $restoreInfo.AllowOverwrite = $true
    $restoreInfo.DatabaseName = $Database

    $srv.Restore($restoreInfo)

    Write-Host "Rollback successful"
    $srv.Disconnect()
}
catch {
    Write-Error "Rollback failed: $_"
    throw
}
```

## Blue-Green Deployment

### Strategy

```
Blue Environment (Current Production):
- SalesCube_Blue
- Currently serving users
- Stable, tested

Green Environment (New Version):
- SalesCube_Green
- Deploy and test new version
- Process and validate

Cutover:
1. Deploy to Green
2. Process Green
3. Test Green thoroughly
4. Switch users to Green
5. Blue becomes standby
6. On next deployment, swap roles
```

### Implementation

```powershell
# Blue-Green-Deploy.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Blue", "Green")]
    [string]$TargetEnvironment,

    [Parameter(Mandatory=$true)]
    [string]$Server
)

$inactiveDb = "SalesCube_$TargetEnvironment"
$activeDb = if ($TargetEnvironment -eq "Blue") { "SalesCube_Green" } else { "SalesCube_Blue" }
$aliasDb = "SalesCube"

# Deploy to inactive environment
Write-Host "Deploying to $inactiveDb..."
& Deploy-SSAS.ps1 -Server $Server -Database $inactiveDb -ProcessAfterDeploy

# Run tests
Write-Host "Running tests..."
$testResults = Test-Deployment -Server $Server -Database $inactiveDb

if ($testResults | Where-Object { $_.Result -eq "Fail" }) {
    throw "Tests failed - aborting cutover"
}

# Create backup of current active
Write-Host "Backing up $activeDb..."
Backup-ASDatabase -Server $Server -Database $activeDb

# Switch alias
Write-Host "Switching to $inactiveDb..."
$srv = New-Object Microsoft.AnalysisServices.Server
$srv.Connect($Server)

# Update database alias/synonym or use role definition
# Implementation depends on your architecture

$srv.Disconnect()

Write-Host "Cutover complete - $inactiveDb is now active"
```

## Monitoring Post-Deployment

```powershell
# Monitor-Deployment.ps1
param(
    [string]$Server,
    [string]$Database,
    [int]$MonitorDurationMinutes = 60
)

$startTime = Get-Date
$endTime = $startTime.AddMinutes($MonitorDurationMinutes)

$srv = New-Object Microsoft.AnalysisServices.Server
$srv.Connect($Server)

while ((Get-Date) -lt $endTime) {
    # Check active sessions
    $sessions = $srv.CaptureXml("
        SELECT * FROM `$SYSTEM.DISCOVER_SESSIONS
        WHERE SESSION_ELAPSED_TIME_MS > 10000
    ", $false)

    # Check for errors
    $errors = $srv.CaptureXml("
        SELECT * FROM `$SYSTEM.DISCOVER_TRACES
        WHERE ERROR_NUMBER <> 0
    ", $false)

    # Check memory usage
    $memory = $srv.CaptureXml("
        SELECT * FROM `$SYSTEM.DISCOVER_MEMORYUSAGE
    ", $false)

    # Alert if issues found
    if ($errors.Length -gt 0) {
        Send-Alert "Errors detected in $Database"
    }

    Start-Sleep -Seconds 60
}

$srv.Disconnect()
```

## Best Practices

### 1. Version Control
```
✓ Store all cube definitions in source control
✓ Use meaningful commit messages
✓ Tag releases
✓ Branch strategy (main, develop, feature branches)
✓ Code review process
```

### 2. Automated Testing
```
✓ Unit tests for calculations
✓ Integration tests for data loading
✓ Performance tests
✓ Regression tests
✓ User acceptance tests
```

### 3. Deployment Checklist
```
□ Code reviewed and approved
□ Tests passing
□ Backup created
□ Deployment script tested
□ Rollback plan ready
□ Stakeholders notified
□ Maintenance window scheduled
□ Monitoring in place
```

### 4. Documentation
```
✓ Deployment procedures
✓ Configuration settings per environment
✓ Rollback procedures
✓ Contact information
✓ Known issues and workarounds
```

### 5. Communication
```
✓ Notify users of deployment schedule
✓ Communicate expected downtime
✓ Provide status updates
✓ Document changes and new features
✓ Post-deployment summary
```

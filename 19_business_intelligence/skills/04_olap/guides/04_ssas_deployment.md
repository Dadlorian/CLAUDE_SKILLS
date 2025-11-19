# Analysis Services Deployment Guide

## Prerequisites

### System Requirements
- SQL Server Analysis Services installed
- Visual Studio with SSDT (SQL Server Data Tools)
- Appropriate permissions on target server
- Source database accessible

### Preparation Checklist
- [ ] Cube developed and tested in development
- [ ] Data source connections verified
- [ ] Security roles defined
- [ ] Processing strategy determined
- [ ] Backup of production (if updating)
- [ ] Maintenance window scheduled

## Deployment Methods

### Method 1: Deployment Wizard (Recommended for Production)

1. **Generate Deployment Files**
   - In Visual Studio SSDT, right-click project
   - Select "Build" to create deployment files
   - Files generated in project's bin folder

2. **Configure Deployment Options**
   Edit `.deploymentoptions` file:
   ```xml
   <DeploymentOptions>
     <ProcessingOption>DoNotProcess</ProcessingOption>
     <TransactionalDeployment>false</TransactionalDeployment>
     <PartitionDeployment>DeployPartitions</PartitionDeployment>
     <RoleDeployment>DeployRolesRetainMembers</RoleDeployment>
     <OptimizationSettings>-1</OptimizationSettings>
   </DeploymentOptions>
   ```

3. **Run Deployment Wizard**
   ```cmd
   "C:\Program Files\Microsoft SQL Server\150\Tools\Binn\ManagementStudio\Microsoft.AnalysisServices.Deployment.exe"
   ```

   Follow wizard steps:
   - Specify .asdatabase file
   - Select target server
   - Review partition and role settings
   - Deploy

### Method 2: PowerShell Automation

```powershell
# Load AMO
[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices")

# Connection parameters
$serverName = "ProductionServer"
$databaseName = "SalesCube"
$xmlaFile = "C:\Deploy\SalesCube.xmla"

# Connect
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect($serverName)

try {
    # Backup existing database
    if ($server.Databases.Contains($databaseName)) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "C:\Backup\${databaseName}_${timestamp}.abf"
        $server.Databases[$databaseName].Backup($backupFile)
        Write-Host "Backup created: $backupFile"
    }

    # Deploy
    $xmla = Get-Content $xmlaFile -Raw
    $results = $server.Execute($xmla)

    # Check for errors
    foreach ($result in $results) {
        foreach ($message in $result.Messages) {
            if ($message -is [Microsoft.AnalysisServices.XmlaError]) {
                throw "Deployment failed: $($message.Description)"
            }
        }
    }

    Write-Host "Deployment successful"

    # Process database
    $db = $server.Databases[$databaseName]
    $db.Process([Microsoft.AnalysisServices.ProcessType]::ProcessFull)
    Write-Host "Processing complete"
}
catch {
    Write-Error "Error during deployment: $_"
    throw
}
finally {
    $server.Disconnect()
}
```

### Method 3: SSMS (Development/Testing)

1. In SQL Server Management Studio
2. Connect to Analysis Services
3. Right-click "Databases"
4. Select "Deploy Database"
5. Browse to .asdatabase file
6. Configure options
7. Deploy

## Post-Deployment Tasks

### 1. Verify Deployment
```mdx
-- Test basic query
SELECT
  [Measures].[Sales Amount] ON 0
FROM [Sales]
```

### 2. Configure Processing
```powershell
# Set up processing schedule using SQL Agent
$jobName = "Process Sales Cube"
$jobStep = @"
Invoke-ProcessASDatabase `
  -Server 'ProductionServer' `
  -Database 'SalesCube' `
  -ProcessType ProcessFull
"@

# Create SQL Agent job (simplified)
# Use SQL Server Management Studio for full configuration
```

### 3. Test Security
```powershell
# Impersonate user to test security
EXECUTE AS LOGIN = 'DOMAIN\TestUser'

# Run test queries
# ...

REVERT
```

### 4. Monitor Performance
- Set up query logging
- Configure performance counters
- Establish baselines

## Troubleshooting Common Issues

### Connection Failures
```
Error: Unable to connect to server
Solution:
- Verify server name and port
- Check firewall rules
- Verify service is running
- Test with ssms
```

### Permission Errors
```
Error: User does not have permission
Solution:
- Add user to server administrators
- Check database roles
- Verify impersonation settings
```

### Processing Errors
```
Error: Processing failed
Solution:
- Check data source connectivity
- Verify source queries
- Review error logs
- Check memory/disk space
```

## Rollback Procedure

```powershell
# Restore from backup
$backupFile = "C:\Backup\SalesCube_20240115_120000.abf"
$serverName = "ProductionServer"

$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect($serverName)

try {
    # Drop current database
    if ($server.Databases.Contains("SalesCube")) {
        $server.Databases["SalesCube"].Drop()
    }

    # Restore
    $restoreInfo = New-Object Microsoft.AnalysisServices.RestoreInfo
    $restoreInfo.File = $backupFile
    $restoreInfo.AllowOverwrite = $true

    $server.Restore($restoreInfo)
    Write-Host "Rollback complete"
}
finally {
    $server.Disconnect()
}
```

## Best Practices

1. **Always backup** before deployment
2. **Test in non-production** first
3. **Deploy during maintenance windows**
4. **Document all changes**
5. **Have rollback plan ready**
6. **Monitor after deployment**
7. **Communicate with stakeholders**

# Partition Maintenance Script
# Automates partition creation and archival

param(
    [Parameter(Mandatory=$true)]
    [string]$Server,
    
    [Parameter(Mandatory=$true)]
    [string]$Database,
    
    [int]$ArchiveMonthsOld = 24,
    [switch]$CreateNextMonthPartition
)

[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices") | Out-Null

function Create-MonthlyPartition {
    param($MeasureGroup, $Year, $Month)
    
    $partitionName = "Sales_${Year}_$(${Month}.ToString('00'))"
    
    if ($MeasureGroup.Partitions.Contains($partitionName)) {
        Write-Host "Partition $partitionName already exists"
        return
    }
    
    $partition = New-Object Microsoft.AnalysisServices.Partition
    $partition.Name = $partitionName
    $partition.ID = $partitionName
    $partition.StorageMode = [Microsoft.AnalysisServices.StorageMode]::Molap
    
    $startDate = Get-Date -Year $Year -Month $Month -Day 1
    $endDate = $startDate.AddMonths(1)
    
    $startDateKey = $startDate.ToString("yyyyMMdd")
    $endDateKey = $endDate.ToString("yyyyMMdd")
    
    $queryBinding = New-Object Microsoft.AnalysisServices.QueryBinding
    $queryBinding.DataSourceID = "SalesDB"
    $queryBinding.QueryDefinition = @"
SELECT *
FROM FactSales
WHERE DateKey >= $startDateKey
  AND DateKey < $endDateKey
"@
    
    $partition.Source = $queryBinding
    $MeasureGroup.Partitions.Add($partition)
    $partition.Update()
    
    Write-Host "Created partition: $partitionName"
}

try {
    $srv = New-Object Microsoft.AnalysisServices.Server
    $srv.Connect($Server)
    
    $db = $srv.Databases[$Database]
    $cube = $db.Cubes["Sales"]
    $mg = $cube.MeasureGroups["Sales"]
    
    # Create next month partition if requested
    if ($CreateNextMonthPartition) {
        $nextMonth = (Get-Date).AddMonths(1)
        Create-MonthlyPartition -MeasureGroup $mg -Year $nextMonth.Year -Month $nextMonth.Month
    }
    
    # Archive old partitions
    $archiveDate = (Get-Date).AddMonths(-$ArchiveMonthsOld)
    $oldPartitions = $mg.Partitions | Where-Object {
        $_.Name -match 'Sales_(\d{4})_(\d{2})'
        $year = [int]$Matches[1]
        $month = [int]$Matches[2]
        $partDate = Get-Date -Year $year -Month $month -Day 1
        $partDate -lt $archiveDate
    }
    
    foreach ($partition in $oldPartitions) {
        Write-Host "Archiving partition: $($partition.Name)"
        
        # Optional: Backup before dropping
        # $backupFile = "C:\Archive\$($partition.Name).abf"
        # $partition.Backup($backupFile)
        
        $partition.Drop()
    }
    
    $srv.Disconnect()
    Write-Host "Partition maintenance completed"
}
catch {
    Write-Error "Partition maintenance failed: $_"
}

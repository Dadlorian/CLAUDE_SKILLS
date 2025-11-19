# Partition Management Guide

## Partition Strategy

### Monthly Partitioning

Best for:
- Daily/weekly data loads
- 1-2 years of detailed data
- Balanced partition sizes

Implementation:
```powershell
$year = 2024
for ($month = 1; $month -le 12; $month++) {
    $partitionName = "Sales_${year}_$(${month}.ToString('00'))"
    $startDate = Get-Date -Year $year -Month $month -Day 1
    $endDate = $startDate.AddMonths(1)
    
    Create-Partition -Name $partitionName -StartDate $startDate -EndDate $endDate
}
```

### Rolling Window

Current + Recent + Historical:
- Current: Last 30 days (ROLAP, real-time)
- Recent: Last 3 months (MOLAP, daily refresh)
- Historical: Older data (MOLAP, monthly aggregated)

##Processing Strategies

### Full Process
```powershell
$partition.Process([Microsoft.AnalysisServices.ProcessType]::ProcessFull)
```

### Incremental Process
```powershell
$queryBinding = New-Object Microsoft.AnalysisServices.QueryBinding
$queryBinding.QueryDefinition = "SELECT * FROM FactSales WHERE LoadDate > '$lastProcessDate'"
$partition.Process([Microsoft.AnalysisServices.ProcessType]::ProcessAdd, $queryBinding)
```

### Parallel Processing
```powershell
$partitions | ForEach-Object -Parallel {
    $_.Process([Microsoft.AnalysisServices.ProcessType]::ProcessFull)
} -ThrottleLimit 4
```

## Maintenance

### Merge Old Partitions
```powershell
# Merge monthly into quarterly
$q1Partition = $mg.Partitions["Sales_2024_Q1"]
$monthlyPartitions = @("Sales_2024_01", "Sales_2024_02", "Sales_2024_03")

foreach ($partName in $monthlyPartitions) {
    $q1Partition.Merge($mg.Partitions[$partName])
}
```

### Archive Old Data
```powershell
# Backup and drop old partitions
$oldPartitions = $mg.Partitions | Where-Object { $_.Name -like "Sales_2020_*" }

foreach ($partition in $oldPartitions) {
    # Backup
    $backupFile = "Archive\$($partition.Name).abf"
    $partition.Backup($backupFile)
    
    # Drop
    $partition.Drop()
}
```

# Aggregation Design Script
# Automated aggregation optimization

param(
    [Parameter(Mandatory=$true)]
    [string]$Server,
    
    [Parameter(Mandatory=$true)]
    [string]$Database,
    
    [int]$PerformanceTarget = 35,
    [switch]$UsageBasedOptimization
)

[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices") | Out-Null

try {
    $srv = New-Object Microsoft.AnalysisServices.Server
    $srv.Connect($Server)
    
    $db = $srv.Databases[$Database]
    $cube = $db.Cubes[0]
    
    foreach ($mg in $cube.MeasureGroups) {
        Write-Host "Designing aggregations for: $($mg.Name)"
        
        # Create or update aggregation design
        $aggDesignName = "$($mg.Name)_Aggregations"
        $aggDesign = $mg.AggregationDesigns[$aggDesignName]
        
        if ($null -eq $aggDesign) {
            $aggDesign = $mg.AggregationDesigns.Add($aggDesignName)
        }
        else {
            # Clear existing aggregations
            $aggDesign.Aggregations.Clear()
        }
        
        # Design aggregations
        if ($UsageBasedOptimization) {
            Write-Host "Using query log for optimization"
            $aggDesign.DesignAggregations(
                0,                  # Performance optimization
                $PerformanceTarget,
                $null               # Use query log
            )
        }
        else {
            Write-Host "Using estimated usage"
            $aggDesign.DesignAggregations(
                0,
                $PerformanceTarget,
                $null
            )
        }
        
        $aggDesign.Update()
        Write-Host "Created $($aggDesign.Aggregations.Count) aggregations"
        
        # Assign to partitions
        foreach ($partition in $mg.Partitions) {
            $partition.AggregationDesignID = $aggDesign.ID
            $partition.Update()
        }
    }
    
    $srv.Disconnect()
    Write-Host "Aggregation design completed"
}
catch {
    Write-Error "Aggregation design failed: $_"
    if ($srv -and $srv.Connected) {
        $srv.Disconnect()
    }
}

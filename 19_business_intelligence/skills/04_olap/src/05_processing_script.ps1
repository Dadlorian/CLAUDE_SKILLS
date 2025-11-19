# SSAS Cube Processing Script
# Production-grade processing automation

param(
    [Parameter(Mandatory=$true)]
    [string]$Server,
    
    [Parameter(Mandatory=$true)]
    [string]$Database,
    
    [ValidateSet("Full", "Incremental", "Update")]
    [string]$ProcessType = "Incremental",
    
    [string]$LogPath = "C:\Logs\SSAS",
    [switch]$ParallelProcessing
)

# Load AMO
[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices") | Out-Null

$startTime = Get-Date
$logFile = Join-Path $LogPath "Process_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Tee-Object -FilePath $logFile -Append
}

try {
    Write-Log "Starting processing: $ProcessType on $Server\$Database"
    
    # Connect to server
    $srv = New-Object Microsoft.AnalysisServices.Server
    $srv.Connect($Server)
    Write-Log "Connected to server: $Server"
    
    $db = $srv.Databases[$Database]
    if ($null -eq $db) {
        throw "Database $Database not found"
    }
    
    # Determine process type
    $processTypeEnum = switch ($ProcessType) {
        "Full" { [Microsoft.AnalysisServices.ProcessType]::ProcessFull }
        "Incremental" { [Microsoft.AnalysisServices.ProcessType]::ProcessAdd }
        "Update" { [Microsoft.AnalysisServices.ProcessType]::ProcessUpdate }
    }
    
    if ($ParallelProcessing) {
        Write-Log "Processing partitions in parallel"
        
        foreach ($cube in $db.Cubes) {
            foreach ($mg in $cube.MeasureGroups) {
                $partitions = $mg.Partitions | Where-Object { $_.State -eq "Unprocessed" -or $ProcessType -eq "Full" }
                
                $jobs = @()
                foreach ($partition in $partitions) {
                    $scriptBlock = {
                        param($serverName, $dbName, $cubeName, $mgName, $partName, $procType)
                        
                        [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices") | Out-Null
                        $s = New-Object Microsoft.AnalysisServices.Server
                        $s.Connect($serverName)
                        
                        $p = $s.Databases[$dbName].Cubes[$cubeName].MeasureGroups[$mgName].Partitions[$partName]
                        $p.Process($procType)
                        
                        $s.Disconnect()
                    }
                    
                    $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $Server, $Database, $cube.Name, $mg.Name, $partition.Name, $processTypeEnum
                    $jobs += $job
                    Write-Log "Started processing partition: $($partition.Name)"
                }
                
                # Wait for all jobs
                $jobs | Wait-Job | Receive-Job
                $jobs | Remove-Job
            }
        }
    }
    else {
        Write-Log "Processing database sequentially"
        $db.Process($processTypeEnum)
    }
    
    $duration = (Get-Date) - $startTime
    Write-Log "Processing completed successfully in $($duration.TotalMinutes) minutes"
    
    # Verify processing
    $db.Refresh()
    Write-Log "Database state: $($db.State)"
    Write-Log "Last processed: $($db.LastProcessed)"
    
    $srv.Disconnect()
    exit 0
}
catch {
    Write-Log "ERROR: $_"
    Write-Log $_.ScriptStackTrace
    
    if ($srv -and $srv.Connected) {
        $srv.Disconnect()
    }
    
    exit 1
}

# SSAS Backup Script
# Automated database backup with retention

param(
    [Parameter(Mandatory=$true)]
    [string]$Server,
    
    [Parameter(Mandatory=$true)]
    [string]$Database,
    
    [string]$BackupPath = "D:\Backup\SSAS",
    [int]$RetentionDays = 30,
    [switch]$ApplyCompression
)

[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices") | Out-Null

try {
    # Ensure backup directory exists
    if (!(Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force
    }
    
    # Connect to server
    $srv = New-Object Microsoft.AnalysisServices.Server
    $srv.Connect($Server)
    
    $db = $srv.Databases[$Database]
    
    # Create backup
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = Join-Path $BackupPath "${Database}_${timestamp}.abf"
    
    Write-Host "Creating backup: $backupFile"
    $db.Backup($backupFile, $ApplyCompression)
    
    Write-Host "Backup completed successfully"
    
    # Cleanup old backups
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem $BackupPath -Filter "${Database}_*.abf" |
        Where-Object { $_.LastWriteTime -lt $cutoffDate } |
        ForEach-Object {
            Write-Host "Deleting old backup: $($_.Name)"
            Remove-Item $_.FullName -Force
        }
    
    $srv.Disconnect()
}
catch {
    Write-Error "Backup failed: $_"
}

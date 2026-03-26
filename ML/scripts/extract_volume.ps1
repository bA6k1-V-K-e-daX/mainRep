# extract_volume.ps1 - Export volume from Docker container

param(
    [string]$QueryId = "3",
    [string]$Container = "ml",
    [string]$OutputDir = ".\extracted_volume"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Volume Export from Container" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Container: $Container"
Write-Host "Query ID:  $QueryId"
Write-Host "Output:    $OutputDir"
Write-Host ""

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$localPath = Join-Path $OutputDir "volume"

Write-Host "Copying /app/volume to $localPath" -ForegroundColor Gray
Write-Host ""

# Copy files from container
docker cp "$Container`:/app/volume" $localPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "Export completed!" -ForegroundColor Green
    Write-Host ""
    
    # Show contents
    $queryPath = Join-Path $localPath "$QueryId"
    
    if (Test-Path $queryPath) {
        Write-Host "Contents of folder ${QueryId}:" -ForegroundColor Cyan
        Write-Host ""
        
        # Source files
        $sourcePath = Join-Path $queryPath "source"
        if (Test-Path $sourcePath) {
            Write-Host "source/ (original images):" -ForegroundColor Yellow
            Get-ChildItem $sourcePath -File | ForEach-Object {
                $size = [math]::Round($_.Length / 1KB, 1)
                Write-Host "   $($_.Name) - ${size} KB" -ForegroundColor Gray
            }
            Write-Host ""
        }
        
        # Result files
        $resultPath = Join-Path $queryPath "result"
        if (Test-Path $resultPath) {
            Write-Host "result/ (processed images):" -ForegroundColor Yellow
            $resultFiles = Get-ChildItem $resultPath -File -ErrorAction SilentlyContinue
            if ($resultFiles) {
                $resultFiles | ForEach-Object {
                    $size = [math]::Round($_.Length / 1KB, 1)
                    Write-Host "   $($_.Name) - ${size} KB" -ForegroundColor Gray
                }
            } else {
                Write-Host "   (empty - no results yet)" -ForegroundColor Gray
            }
            Write-Host ""
        }
        
        # Output files
        $outputPath = Join-Path $queryPath "output"
        if (Test-Path $outputPath) {
            Write-Host "output/ (metadata/JSON):" -ForegroundColor Yellow
            $outputFiles = Get-ChildItem $outputPath -File -ErrorAction SilentlyContinue
            if ($outputFiles) {
                $outputFiles | ForEach-Object {
                    $size = [math]::Round($_.Length / 1KB, 1)
                    Write-Host "   $($_.Name) - ${size} KB" -ForegroundColor Gray
                }
            } else {
                Write-Host "   (empty)" -ForegroundColor Gray
            }
            Write-Host ""
        }
        
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Open folder in Explorer:" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Command: explorer.exe `"$localPath`"" -ForegroundColor Gray
    }
} else {
    Write-Host "Export failed!" -ForegroundColor Red
    Write-Host "Check container is running:" -ForegroundColor Gray
    Write-Host "   docker compose ps ml" -ForegroundColor Gray
}

Write-Host ""
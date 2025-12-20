# copy_all_contents.ps1
$containerName = "ml_service_container"
$archiveRoot = "..\..\results_container"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$exportFolder = "results${timestamp}"
$destinationFolder = "$archiveRoot\$exportFolder"

Write-Host "Getting ALL contents from container: $containerName" -ForegroundColor Cyan
Write-Host "Exporting to: $exportFolder" -ForegroundColor Yellow

# Create folder
New-Item -ItemType Directory -Force -Path $destinationFolder -ErrorAction SilentlyContinue | Out-Null

# Copy ALL contents from /app/results folder (NOT the folder itself)
Write-Host "Copying files..." -ForegroundColor Gray
docker cp "${containerName}:/app/results/." $destinationFolder

# Check results
Start-Sleep -Milliseconds 500  # Wait for copy to complete
$allItems = Get-ChildItem -Path $destinationFolder -Force
$files = $allItems | Where-Object { !$_.PSIsContainer }
$folders = $allItems | Where-Object { $_.PSIsContainer }

Write-Host ""
Write-Host "=== COPY RESULTS ===" -ForegroundColor Cyan
Write-Host "Destination: $destinationFolder" -ForegroundColor Yellow
Write-Host "Total items: $($allItems.Count)" -ForegroundColor Green
Write-Host "Files: $($files.Count)" -ForegroundColor Green
Write-Host "Subfolders: $($folders.Count)" -ForegroundColor Green

# Show what was copied
if ($files.Count -gt 0) {
    Write-Host ""
    Write-Host "Files copied:" -ForegroundColor Gray
    $files | Select-Object -First 10 | ForEach-Object {
        $size = ""
        if ($_.Length -gt 1MB) {
            $size = "$([Math]::Round($_.Length/1MB, 2)) MB"
        } elseif ($_.Length -gt 1KB) {
            $size = "$([Math]::Round($_.Length/1KB, 2)) KB"
        } else {
            $size = "$($_.Length) bytes"
        }
        Write-Host "   - $($_.Name) ($size)" -ForegroundColor DarkGray
    }
    if ($files.Count -gt 10) {
        Write-Host "   ... and $($files.Count - 10) more files" -ForegroundColor DarkGray
    }
}

if ($folders.Count -gt 0) {
    Write-Host ""
    Write-Host "Subfolders:" -ForegroundColor Gray
    $folders | ForEach-Object {
        $itemsCount = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "   - $($_.Name) ($itemsCount files inside)" -ForegroundColor DarkCyan
    }
}

# Open folder
Write-Host ""
Write-Host "Opening folder..." -ForegroundColor Cyan
Start-Sleep -Milliseconds 500
explorer $destinationFolder
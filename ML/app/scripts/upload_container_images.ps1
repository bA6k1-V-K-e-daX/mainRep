# copy_volume.ps1
# Exports /app/volume content from container 'ml' to local folder 'cont_volume'

param(
    [string]$ContainerName = "ml",
    [string]$ContainerPath = "/app/volume",
    [string]$LocalDest = "./cont_volume",
    [switch]$WithTimestamp,
    [switch]$OpenAfter
)

# Generate destination folder name
if ($WithTimestamp) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $destinationFolder = "${LocalDest}_${timestamp}"
} else {
    $destinationFolder = $LocalDest
}

Write-Host "Docker Volume Export" -ForegroundColor Cyan
Write-Host "Container: $ContainerName" -ForegroundColor Gray
Write-Host "Source: ${ContainerPath}/." -ForegroundColor Gray
Write-Host "Destination: $destinationFolder" -ForegroundColor Yellow
Write-Host ""

# Check if container is running
$containerStatus = docker ps --filter "name=^${ContainerName}$" --format "{{.Status}}" -a
if (-not $containerStatus) {
    Write-Host "ERROR: Container '$ContainerName' not found!" -ForegroundColor Red
    Write-Host "Available containers:" -ForegroundColor DarkGray
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    exit 1
}

# Create destination folder
New-Item -ItemType Directory -Force -Path $destinationFolder -ErrorAction SilentlyContinue | Out-Null

# Copy contents (note the /. at end - copies content, not the folder itself)
Write-Host "Copying files..." -ForegroundColor Gray
docker cp "${ContainerName}:${ContainerPath}/." $destinationFolder

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Copy failed!" -ForegroundColor Red
    exit 1
}

# Wait for I/O to complete
Start-Sleep -Milliseconds 500

# === Statistics ===
$allItems = Get-ChildItem -Path $destinationFolder -Force -ErrorAction SilentlyContinue
$files = $allItems | Where-Object { !$_.PSIsContainer }
$folders = $allItems | Where-Object { $_.PSIsContainer }

Write-Host ""
Write-Host "Copy completed!" -ForegroundColor Green
Write-Host "Path: $(Resolve-Path $destinationFolder)" -ForegroundColor Yellow
Write-Host "Total items: $($allItems.Count)" -ForegroundColor Green
Write-Host "Files: $($files.Count)" -ForegroundColor Green
Write-Host "Folders: $($folders.Count)" -ForegroundColor Green

# File details (top 10)
if ($files.Count -gt 0) {
    Write-Host ""
    Write-Host "Files (first 10):" -ForegroundColor DarkGray
    $files | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | ForEach-Object {
        $size = if ($_.Length -gt 1GB) { "$([Math]::Round($_.Length/1GB, 2)) GB" }
                elseif ($_.Length -gt 1MB) { "$([Math]::Round($_.Length/1MB, 2)) MB" }
                elseif ($_.Length -gt 1KB) { "$([Math]::Round($_.Length/1KB, 2)) KB" }
                else { "$($_.Length) B" }
        Write-Host "   - $($_.Name) ($size)" -ForegroundColor DarkGray
    }
    if ($files.Count -gt 10) {
        Write-Host "   ... and $($files.Count - 10) more files" -ForegroundColor DarkGray
    }
}

# Folder details
if ($folders.Count -gt 0) {
    Write-Host ""
    Write-Host "Subfolders:" -ForegroundColor DarkGray
    $folders | ForEach-Object {
        $count = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "   - $($_.Name) ($count files inside)" -ForegroundColor DarkCyan
    }
}

# Open folder in Explorer
if ($OpenAfter) {
    Write-Host ""
    Write-Host "Opening folder..." -ForegroundColor Cyan
    Start-Sleep -Milliseconds 300
    Invoke-Item (Resolve-Path $destinationFolder)
}
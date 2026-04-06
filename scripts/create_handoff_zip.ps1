param(
    [string]$OutputName = "MetaHackathon_OpenEnv_Handoff.zip"
)

$ErrorActionPreference = "Stop"

$repoDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$outputPath = Join-Path $repoDir $OutputName
$tempDir = Join-Path $env:TEMP ("openenv_handoff_" + [guid]::NewGuid().ToString("N"))

New-Item -ItemType Directory -Path $tempDir | Out-Null

$exclude = @(
    ".venv",
    ".pytest_cache",
    "__pycache__",
    ".git",
    "*.pyc",
    "*.pyo",
    "*.zip"
)

Write-Host "[INFO] Creating clean handoff folder..."

Get-ChildItem -Path $repoDir -Force | ForEach-Object {
    $name = $_.Name
    foreach ($pattern in $exclude) {
        if ($name -like $pattern) {
            return
        }
    }

    $dest = Join-Path $tempDir $name
    if ($_.PSIsContainer) {
        Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
    }
    else {
        Copy-Item -Path $_.FullName -Destination $dest -Force
    }
}

if (Test-Path $outputPath) {
    Remove-Item -Path $outputPath -Force
}

Write-Host "[INFO] Creating zip: $outputPath"
Compress-Archive -Path (Join-Path $tempDir "*") -DestinationPath $outputPath -Force

Remove-Item -Path $tempDir -Recurse -Force

Write-Host "[PASS] Handoff zip created: $outputPath"

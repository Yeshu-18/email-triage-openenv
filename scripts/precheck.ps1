param(
    [string]$SpaceUrl = "",
    [int]$DockerBuildTimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"

function Write-Info([string]$Message) {
    Write-Host "[INFO] $Message"
}

function Write-Pass([string]$Message) {
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Write-Fail([string]$Message) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    exit 1
}

$repoDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Info "Repository: $repoDir"

if ($SpaceUrl -ne "") {
    Write-Info "Step 1/3: Checking HF Space reset endpoint"
    try {
        $resetUrl = "$SpaceUrl/reset"
        $body = @{ task_id = "email_easy" } | ConvertTo-Json
        $response = Invoke-WebRequest -Uri $resetUrl -Method Post -ContentType "application/json" -Body $body -TimeoutSec 60
        if ($response.StatusCode -eq 200) {
            Write-Pass "HF Space /reset returned 200"
        }
        else {
            Write-Fail "HF Space /reset returned HTTP $($response.StatusCode)"
        }
    }
    catch {
        Write-Fail "HF Space check failed: $($_.Exception.Message)"
    }
}
else {
    Write-Info "Step 1/3: Skipped Space check (use -SpaceUrl to enable)"
}

Write-Info "Step 2/3: Running docker build"
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Fail "docker command not found"
}

Push-Location $repoDir
try {
    docker build .
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "docker build failed"
    }
    Write-Pass "Docker build succeeded"
}
finally {
    Pop-Location
}

Write-Info "Step 3/3: Running openenv validate"

$openenvExe = Join-Path $env:LOCALAPPDATA "Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\openenv.exe"
$openenvCmd = Get-Command openenv -ErrorAction SilentlyContinue

Push-Location $repoDir
try {
    if ($openenvCmd) {
        openenv validate
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "openenv validate failed"
        }
    }
    elseif (Test-Path $openenvExe) {
        & $openenvExe validate
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "openenv validate failed"
        }
    }
    else {
        Write-Fail "openenv command not found. Install with: python -m pip install openenv-core"
    }

    Write-Pass "openenv validate passed"
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "========================================"
Write-Host " All checks passed. Ready to submit."
Write-Host "========================================"

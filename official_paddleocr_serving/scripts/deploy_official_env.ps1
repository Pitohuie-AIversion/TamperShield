param(
    [string]$EnvName = "paddleocr_official",
    [string]$PythonVersion = "3.10",
    [switch]$SkipCondaCreate
)

# One-click environment deployment for the official PaddleOCR/PaddleX demo.
# This script installs dependencies only. It does not start long-running services.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Resolve-Path (Join-Path $ScriptDir "..")
$Requirements = Join-Path $ProjectDir "requirements_official.txt"

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "conda was not found in PATH. Please install Anaconda/Miniconda first."
}

if (-not (Test-Path $Requirements)) {
    throw "requirements_official.txt not found: $Requirements"
}

Push-Location $ProjectDir
try {
    Write-Host "Official PaddleOCR serving deployment"
    Write-Host "Project directory: $ProjectDir"
    Write-Host "Conda environment: $EnvName"
    Write-Host "Python version: $PythonVersion"

    $envList = conda env list
    $envExists = $false
    foreach ($line in $envList) {
        if ($line -match "^\s*$([regex]::Escape($EnvName))\s+") {
            $envExists = $true
            break
        }
    }

    if ($envExists) {
        Write-Host "Conda environment already exists, reusing: $EnvName"
    } elseif ($SkipCondaCreate) {
        Write-Host "Skipping conda environment creation because -SkipCondaCreate was provided."
    } else {
        Write-Host "Creating conda environment: $EnvName"
        conda create -n $EnvName "python=$PythonVersion" -y
    }

    Write-Host "Installing Python dependencies..."
    conda run -n $EnvName python -m pip install -r $Requirements

    Write-Host "Installing PaddleX serving plugin..."
    conda run -n $EnvName paddlex --install serving -y

    Write-Host "Running environment check..."
    conda run -n $EnvName python scripts/check_environment.py

    Write-Host ""
    Write-Host "Deployment completed."
    Write-Host "Next commands:"
    Write-Host "  conda activate $EnvName"
    Write-Host "  .\scripts\start_ocr_service.ps1"
    Write-Host "  .\scripts\start_ppstructure_service.ps1"
    Write-Host "  .\scripts\start_table_service.ps1 -Pipeline table_recognition_v2"
}
finally {
    Pop-Location
}

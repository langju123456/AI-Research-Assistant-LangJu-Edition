<#
Run development environment for the LangJu AI project (Windows PowerShell).

Usage:
  # from repository root
  .\run_dev.ps1

  # re-install dependencies before run
  .\run_dev.ps1 -Reinstall

What it does:
  - ensures current working directory is repo root
  - creates/activates .venv if missing
  - optionally installs requirements (when -Reinstall passed)
  - sets PYTHONPATH to the repo root for the current session
  - starts Streamlit using the project's entry script
#>

param(
    [switch]$Reinstall = $false
)

try {
    $RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $RepoRoot
} catch {
    Write-Error "Failed to determine script location. Run this script from the repository root."
    exit 1
}

Write-Host "Repository root: $RepoRoot"

# Create venv if missing
if (-not (Test-Path "$RepoRoot\.venv\Scripts\Activate.ps1")) {
    Write-Host ".venv not found — creating virtual environment..."
    python -m venv .venv
}

Write-Host "Activating .venv..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

if ($Reinstall) {
    Write-Host "Installing requirements.txt... (this may take a while)"
    pip install -r requirements.txt
}

# Ensure repo root is on PYTHONPATH for this session so `import app` works
$env:PYTHONPATH = $RepoRoot
Write-Host "PYTHONPATH set to: $env:PYTHONPATH"

Write-Host "Starting Streamlit (app/main.py)"
python -m streamlit run app/main.py

# To run the API server instead, uncomment the following line
# python -m uvicorn app.server:app --reload --port 8000

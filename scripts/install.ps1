# Garant MCP Server - Windows Installation Script
# Run with PowerShell: .\install.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Garant MCP Server Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.11+"
}

Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists. Skipping..." -ForegroundColor Gray
} else {
    python -m venv .venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install development dependencies (optional)
Write-Host ""
Write-Host "Installing development dependencies..." -ForegroundColor Yellow
pip install -r requirements-dev.txt

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "Creating .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file already exists. Skipping..." -ForegroundColor Gray
} else {
    Copy-Item .env.example .env
    Write-Host ".env file created!" -ForegroundColor Green
    Write-Host "IMPORTANT: Please edit .env file and add your Garant API token!" -ForegroundColor Red
}

# Create directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path logs, exports, .cache | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file and add your GARANT_TOKEN"
Write-Host "2. Run tests: .\scripts\test.ps1"
Write-Host "3. Start server: .\scripts\run.ps1"
Write-Host ""

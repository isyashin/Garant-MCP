# Garant MCP Server - Test Script
# Run with PowerShell: .\scripts\test.ps1

$ErrorActionPreference = "Stop"

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Error "Virtual environment not found. Please run .\scripts\install.ps1 first"
}

# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Set environment variables
$env:PYTHONPATH = "$PSScriptRoot\..\src"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Garant MCP Server Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run tests with coverage
pytest --cov=src\garant_mcp --cov-report=html --cov-report=term-missing tests\ -v

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Coverage report saved to: htmlcov\index.html" -ForegroundColor Yellow

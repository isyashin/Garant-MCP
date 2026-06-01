# Garant MCP Server - Run Script
# Run with PowerShell: .\scripts\run.ps1

$ErrorActionPreference = "Stop"

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Error "Virtual environment not found. Please run .\scripts\install.ps1 first"
}

# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Set environment variables
$env:PYTHONPATH = "$PSScriptRoot\..\src"

# Create necessary directories
New-Item -ItemType Directory -Force -Path logs, exports, .cache | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Garant MCP Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server is running with STDIO transport" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Run the server
python -m garant_mcp.server

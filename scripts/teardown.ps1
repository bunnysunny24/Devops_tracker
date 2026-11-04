# PowerShell Teardown Script
Write-Host "Stopping and cleaning up containers, networks, and volumes..." -ForegroundColor Yellow
docker compose down -v --remove-orphans
Write-Host "Cleanup complete!" -ForegroundColor Green

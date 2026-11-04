# PowerShell Setup Script for Windows
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "⚡ Automated Cloud-Native Application Deployment & Monitoring" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Docker status
Write-Host "`n[1/4] Checking Docker Engine..." -ForegroundColor Green
try {
    $dockerCheck = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Docker daemon might not be running. Starting or checking Docker Desktop..."
    } else {
        Write-Host "Docker is up and operational!" -ForegroundColor Green
    }
} catch {
    Write-Warning "Docker is not detected in current session path."
}

# 2. Build and run containers via Docker Compose
Write-Host "`n[2/4] Starting Full Observability Stack with Docker Compose..." -ForegroundColor Green
docker compose down --remove-orphans 2>$null
docker compose up -d --build

# 3. Check service health
Write-Host "`n[3/4] Verifying Stack Health..." -ForegroundColor Green
Start-Sleep -Seconds 4
docker compose ps

# 4. Display service access points
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "🎉 Cloud-Native Observability Stack is Ready!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🌐 Application Dashboard   : http://localhost:8000" -ForegroundColor White
Write-Host "📊 Prometheus UI            : http://localhost:9090" -ForegroundColor White
Write-Host "📈 Grafana Dashboards       : http://localhost:3000 (User: admin / Pass: admin)" -ForegroundColor White
Write-Host "🔔 Alertmanager             : http://localhost:9093" -ForegroundColor White
Write-Host "🖥️ Node Exporter            : http://localhost:9100" -ForegroundColor White
Write-Host "`nTo generate live test traffic and observe dashboards:" -ForegroundColor Yellow
Write-Host "  python scripts\simulate_traffic.py" -ForegroundColor Yellow
Write-Host "==========================================================`n" -ForegroundColor Cyan

#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "⚡ Automated Cloud-Native Application Deployment & Monitoring"
echo "=========================================================="

echo -e "\n[1/3] Building and starting containers via Docker Compose..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build

echo -e "\n[2/3] Waiting for services to initialize..."
sleep 5
docker compose ps

echo -e "\n=========================================================="
echo "🎉 Cloud-Native Observability Stack is Ready!"
echo "=========================================================="
echo "🌐 Application Dashboard   : http://localhost:8000"
echo "📊 Prometheus UI            : http://localhost:9090"
echo "📈 Grafana Dashboards       : http://localhost:3000 (User: admin / Pass: admin)"
echo "🔔 Alertmanager             : http://localhost:9093"
echo "🖥️ Node Exporter            : http://localhost:9100"
echo -e "\nTo simulate live traffic for Prometheus & Grafana:"
echo "  python3 scripts/simulate_traffic.py"
echo "=========================================================="

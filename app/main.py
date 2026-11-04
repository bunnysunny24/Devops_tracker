import os
import time
import random
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

try:
    import psutil
except ImportError:
    psutil = None
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# App initialization
APP_NAME = os.getenv("APP_NAME", "CloudNativePulse")
APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")
APP_ENV = os.getenv("APP_ENV", "production")

app = FastAPI(
    title=APP_NAME,
    description="Automated Cloud-Native Application with Observability & Monitoring",
    version=APP_VERSION,
)

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Current number of requests in-flight",
)

SYSTEM_CPU_USAGE = Gauge(
    "app_system_cpu_usage_percent",
    "Application host CPU usage percent",
)

SYSTEM_MEMORY_USAGE = Gauge(
    "app_system_memory_usage_bytes",
    "Application host Memory usage in bytes",
)

DEPLOYMENT_INFO = Gauge(
    "app_deployment_info",
    "Application deployment metadata",
    ["version", "environment", "app_name"],
)
DEPLOYMENT_INFO.labels(version=APP_VERSION, environment=APP_ENV, app_name=APP_NAME).set(1)

SIMULATED_ERROR_COUNTER = Counter(
    "app_simulated_errors_total",
    "Total simulated errors triggered for alerting tests",
    ["error_type"],
)

# Static files & Templates
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR) if os.path.exists(TEMPLATES_DIR) else None

# In-memory storage for demonstration
class Item(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    status: str = "pending"
    created_at: Optional[str] = None

database: List[dict] = [
    {
        "id": 1,
        "title": "Cloud-Native Microservice Architecture",
        "description": "Dockerized container ready for Kubernetes deployment",
        "status": "completed",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
    {
        "id": 2,
        "title": "Prometheus & Grafana Observability",
        "description": "Scrapes application metrics and system stats with dynamic dashboards",
        "status": "in-progress",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
    {
        "id": 3,
        "title": "Automated CI/CD Pipeline",
        "description": "GitHub Actions + Docker Hub + ArgoCD GitOps workflow",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
]

# Middleware for metrics and request timing
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    # Avoid tracking prometheus metrics endpoint itself in detail
    path = request.url.path
    method = request.method
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        status_code = 500
        raise exc
    finally:
        duration = time.time() - start_time
        ACTIVE_REQUESTS.dec()
        
        # Normalize endpoint path for low cardinality in metrics
        normalized_path = path
        if path.startswith("/api/items/"):
            normalized_path = "/api/items/{id}"
            
        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=normalized_path,
            status_code=str(status_code),
        ).inc()
        
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            endpoint=normalized_path,
        ).observe(duration)
        
        # Update system gauges
        try:
            if psutil:
                SYSTEM_CPU_USAGE.set(psutil.cpu_percent())
                SYSTEM_MEMORY_USAGE.set(psutil.virtual_memory().used)
            else:
                SYSTEM_CPU_USAGE.set(12.5)
                SYSTEM_MEMORY_USAGE.set(256 * 1024 * 1024)
        except Exception:
            pass

    return response

# Root Web Interface
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if templates:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "app_version": APP_VERSION,
                "app_env": APP_ENV,
                "items": database,
            },
        )
    return HTMLResponse(
        f"<html><body><h1>{APP_NAME} ({APP_VERSION})</h1><p>Environment: {APP_ENV}</p></body></html>"
    )

# Prometheus Scrape Endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint exposed for scraping."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Kubernetes Health & Readiness Probes
@app.get("/healthz", tags=["Health"])
async def liveness_probe():
    """Liveness probe: verifies the process is running."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(), "version": APP_VERSION}

@app.get("/ready", tags=["Health"])
async def readiness_probe():
    """Readiness probe: verifies the application can accept incoming traffic."""
    return {"status": "ready", "traffic_enabled": True, "active_connections": len(database)}

# Business API Endpoints
@app.get("/api/items", response_model=List[dict], tags=["Items"])
async def list_items():
    return database

@app.post("/api/items", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: Item):
    new_id = len(database) + 1
    new_entry = {
        "id": new_id,
        "title": item.title,
        "description": item.description,
        "status": item.status,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    database.append(new_entry)
    return new_entry

@app.get("/api/items/{item_id}", response_model=dict, tags=["Items"])
async def get_item(item_id: int):
    for item in database:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

@app.delete("/api/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int):
    for idx, item in enumerate(database):
        if item["id"] == item_id:
            del database[idx]
            return {"deleted": True, "id": item_id}
    raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

# Monitoring & Alerting Simulation Endpoints
@app.get("/api/simulate/slow", tags=["Simulation"])
async def simulate_slow_response(seconds: float = 1.5):
    """Simulates high latency to test Prometheus histogram and alert thresholds."""
    time.sleep(seconds)
    return {"message": f"Delayed response after {seconds} seconds", "simulated_latency": seconds}

@app.get("/api/simulate/error", tags=["Simulation"])
async def simulate_error(code: int = 500):
    """Simulates application 5xx errors to test Alertmanager trigger."""
    SIMULATED_ERROR_COUNTER.labels(error_type=f"HTTP_{code}").inc()
    raise HTTPException(
        status_code=code,
        detail=f"Simulated {code} Internal Server Error for Monitoring Verification",
    )

@app.get("/api/simulate/load", tags=["Simulation"])
async def simulate_load(iterations: int = 1500000):
    """Simulates CPU spike to trigger Horizontal Pod Autoscaler (HPA) or CPU alert."""
    total = 0
    for i in range(iterations):
        total += (i * i) % 997
    return {"message": "CPU load simulation completed", "iterations": iterations, "checksum": total}

@app.get("/api/stats", tags=["System"])
async def get_system_stats():
    """Returns current live system statistics for the frontend dashboard."""
    if psutil:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        mem_used = round(mem.used / (1024 * 1024), 2)
        mem_total = round(mem.total / (1024 * 1024), 2)
        uptime = round(time.time() - psutil.boot_time(), 2)
    else:
        cpu = round(random.uniform(8.0, 22.0), 1)
        mem_used = 284.5
        mem_total = 2048.0
        uptime = round(time.time() - 1700000000, 2)

    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENV,
        "cpu_percent": cpu,
        "memory_used_mb": mem_used,
        "memory_total_mb": mem_total,
        "total_items": len(database),
        "uptime_seconds": uptime,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

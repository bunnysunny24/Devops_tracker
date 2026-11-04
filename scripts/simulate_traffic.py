#!/usr/bin/env python3
"""
Simulate Realistic Traffic, Errors, and Load for Cloud-Native Observability Suite.
Generates requests to populate Prometheus metrics and Grafana dashboards in real time.
"""

import time
import random
import sys
try:
    import urllib.request
    import urllib.error
    import json
except ImportError:
    pass

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

ENDPOINTS = [
    ("/", "GET", 0.40),
    ("/api/items", "GET", 0.30),
    ("/api/stats", "GET", 0.15),
    ("/healthz", "GET", 0.05),
    ("/ready", "GET", 0.05),
    ("/api/simulate/slow?seconds=0.6", "GET", 0.03),
    ("/api/simulate/error?code=500", "GET", 0.02),
]

def make_request(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        data_bytes = json.dumps(data).encode('utf-8')
    else:
        data_bytes = None

    start = time.time()
    try:
        with urllib.request.urlopen(req, data=data_bytes, timeout=5) as response:
            latency = (time.time() - start) * 1000
            return response.status, latency
    except urllib.error.HTTPError as e:
        latency = (time.time() - start) * 1000
        return e.code, latency
    except Exception as e:
        return 0, 0

def run():
    print(f"============================================================")
    print(f"🚀 Cloud-Native Traffic & Observability Simulator")
    print(f"🎯 Target Application: {BASE_URL}")
    print(f"📊 Scraped by Prometheus -> Visualized in Grafana")
    print(f"Press Ctrl+C to terminate simulation.")
    print(f"============================================================")

    count = 0
    while True:
        count += 1
        # Pick random endpoint based on weight
        rand_val = random.random()
        cumulative = 0.0
        selected_endpoint = ENDPOINTS[0][0]
        selected_method = ENDPOINTS[0][1]

        for path, meth, weight in ENDPOINTS:
            cumulative += weight
            if rand_val <= cumulative:
                selected_endpoint = path
                selected_method = meth
                break

        # Occasionally add new item via POST
        if count % 20 == 0:
            status, lat = make_request("/api/items", "POST", {
                "title": f"Telemetry Entity #{count}",
                "description": f"Automated entity generated at {time.strftime('%H:%M:%S')}",
                "status": random.choice(["pending", "in-progress", "completed"])
            })
            print(f"[{time.strftime('%H:%M:%S')}] POST /api/items -> Status: {status} ({lat:.1f}ms)")
        else:
            status, lat = make_request(selected_endpoint, selected_method)
            status_symbol = "✅" if status < 400 else "⚠️" if status < 500 else "❌"
            print(f"[{time.strftime('%H:%M:%S')}] {status_symbol} {selected_method} {selected_endpoint:<30} -> Status: {status} ({lat:.1f}ms)")

        # Variable sleep between 50ms and 400ms for realistic traffic flow
        time.sleep(random.uniform(0.08, 0.45))

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n🛑 Traffic simulation halted.")

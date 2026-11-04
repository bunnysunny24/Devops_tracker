#!/usr/bin/env python3
"""
Simulate Realistic Traffic, Errors, and Load for Cloud-Native Observability Suite.
Generates requests to populate Prometheus metrics and Grafana dashboards in real time.
"""

import sys
import time
import random
import argparse

# Force UTF-8 if supported
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import urllib.request
    import urllib.error
    import json
except ImportError:
    pass

ENDPOINTS = [
    ("/", "GET", 0.35),
    ("/api/items", "GET", 0.30),
    ("/api/stats", "GET", 0.15),
    ("/healthz", "GET", 0.08),
    ("/ready", "GET", 0.04),
    ("/api/simulate/slow?seconds=0.6", "GET", 0.05),
    ("/api/simulate/error?code=500", "GET", 0.03),
]

def make_request(base_url, path, method="GET", data=None):
    url = f"{base_url}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        data_bytes = json.dumps(data).encode('utf-8')
    else:
        data_bytes = None

    start = time.time()
    try:
        with urllib.request.urlopen(req, data=data_bytes, timeout=6) as response:
            latency = (time.time() - start) * 1000
            return response.status, latency
    except urllib.error.HTTPError as e:
        latency = (time.time() - start) * 1000
        return e.code, latency
    except Exception as e:
        return 0, 0

def run(base_url="http://localhost:8000", max_requests=None):
    print("=" * 60)
    print("Cloud-Native Traffic & Observability Simulator")
    print(f"Target Application : {base_url}")
    print("Metrics Pipeline   : Scraped by Prometheus -> Visualized in Grafana")
    if max_requests:
        print(f"Mode               : Running {max_requests} requests")
    else:
        print("Mode               : Running continuously (Press Ctrl+C to terminate)")
    print("=" * 60)

    count = 0
    success_count = 0
    error_count = 0

    while True:
        count += 1
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

        if count % 15 == 0:
            status, lat = make_request(base_url, "/api/items", "POST", {
                "title": f"Telemetry Entity #{count}",
                "description": f"Automated entity generated at {time.strftime('%H:%M:%S')}",
                "status": random.choice(["pending", "in-progress", "completed"])
            })
            symbol = "[OK]" if status < 400 else "[ERROR]"
            print(f"[{time.strftime('%H:%M:%S')}] {symbol} POST /api/items -> Status: {status} ({lat:.1f}ms)")
        else:
            status, lat = make_request(base_url, selected_endpoint, selected_method)
            if status < 400:
                symbol = "[OK]"
                success_count += 1
            elif status < 500:
                symbol = "[WARN]"
            else:
                symbol = "[ALERT-500]"
                error_count += 1
            print(f"[{time.strftime('%H:%M:%S')}] {symbol:<11} {selected_method} {selected_endpoint:<32} -> Status: {status} ({lat:.1f}ms)")

        if max_requests and count >= max_requests:
            print("\n" + "=" * 60)
            print(f"Simulation completed: {count} total requests dispatched.")
            print(f"Successful: {success_count} | 5xx Injected (for alerts): {error_count}")
            print("=" * 60)
            break

        time.sleep(random.uniform(0.05, 0.25))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate Cloud-Native Traffic")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--count", type=int, default=None, help="Number of requests to send (default: continuous)")
    args = parser.parse_args()

    try:
        run(base_url=args.url, max_requests=args.count)
    except KeyboardInterrupt:
        print("\nTraffic simulation halted.")

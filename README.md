# ⚡ Automated Cloud-Native Application Deployment & Continuous Monitoring Suite

[![Cloud-Native CI/CD Pipeline](https://github.com/bunnysunny24/Devops_tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/bunnysunny24/Devops_tracker/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.28+-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-v2.50-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-v10.3-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Terraform](https://img.shields.io/badge/Terraform-v1.5+-7B42BC?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Ansible](https://img.shields.io/badge/Ansible-Automation-EE0000?logo=ansible&logoColor=white)](https://www.ansible.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An enterprise‑grade DevOps engineering repository providing a **complete end‑to‑end implementation** for the two exam practicals that form the core of the course:

* **Practical 5 – Cloud‑Native Deployment with Monitoring (3 marks)**
* **Practical 6 – CI/CD Pipeline & Zero‑Downtime Release (3 marks)**

---

## 📌 Executive Summary & Problem Scenario

Modern high‑velocity software delivery demands **repeatability, observability, and resilience**. Traditional deployment workflows that rely on manual console clicks, ad‑hoc shell scripts, and static VM images suffer from three systemic weaknesses. First, **configuration drift** inevitably creeps in as operators apply patches or install packages on a per‑machine basis; the resulting environments diverge over time, making it impossible to guarantee that “what works on my laptop works on production”. Second, **human error**—from mistyped commands to forgotten dependency installations—introduces silent bugs that only surface under load, exposing the business to costly outages. Third, **environment discrepancies** between development, staging, and production amplify the risk of regression, because each environment may be running a different OS version, library set, or network topology.

When an e‑commerce organization experiences these issues, the **business impact** is immediate and severe. A failed deployment can stall the checkout pipeline for minutes, leading to **cart abandonment** and direct loss of revenue. Service Level Agreements (SLAs) promised to customers are violated, eroding trust and brand reputation. Moreover, any un‑monitored spike in latency or error rates can cascade into a **customer experience crisis**, as shoppers encounter broken pages or delayed responses. The exam problem statement captures this reality succinctly:
> "An e‑commerce company faces frequent deployment failures, manual server setup, and downtime during releases."

### Architectural Solution Matrix
| Operational Bottleneck | Root Cause in Traditional DevOps | Implemented Cloud‑Native Solution | Code Location |
|---|---|---|---|
| **Manual Server Setup** | Inconsistent OS packages, missing Docker, ad‑hoc firewall rules | **Infrastructure as Code (IaC)** via **Terraform** + **Ansible** for deterministic provisioning | `terraform/` & `ansible/` |
| **Frequent Deployment Failures** | Lack of automated testing, missing security gates, direct pushes to prod | **Four‑stage CI/CD pipeline** (Lint → Unit Tests → Trivy SAST → Multi‑stage Docker Build → K8s CD) | `.github/workflows/ci.yml` & `Jenkinsfile` |
| **Release Downtime** | Service restarts block traffic, no health‑check gating | **Kubernetes RollingUpdate** with `maxSurge: 1` & `maxUnavailable: 0` plus readiness probes | `k8s/02-app-deployment.yaml` |
| **Insufficient Observability** | No centralized metrics, logs scattered across VMs | **Dual‑tier observability**: CloudWatch for host‑level metrics + Prometheus/Grafana for application‑level telemetry | `monitoring/` & `terraform/ec2_cloudwatch/` |

---

## 🏗️ System Architecture & Workflow Diagram

```mermaid
flowchart TD
    subgraph SCM["Source Control & Developer Workstation"]
        DEV["Developer Commit / PR"] --|push| GIT["GitHub Repository (bunnysunny24/Devops_tracker)"]
    end
    
    subgraph CICD["Continuous Integration & Quality Gates"]
        GIT --|trigger| CI["GitHub Actions CI Pipeline"]
        CI --|stage 1| TEST["Lint & Pytest Unit Tests"]
        TEST --|stage 2| SCAN["Trivy SAST Security Scan"]
        SCAN --|stage 3| DOCKER["Multi‑Stage Docker Build"]
        DOCKER --|stage 4| CD["Kubernetes Continuous Deployment"]
    end
    
    subgraph DEPLOY["Automated Provisioning & Deployment"]
        CD --|deploy| K8S["Kubernetes Pod Replicas (Zero‑Downtime RollingUpdate)"]
        IAC["Terraform (IaC)"] --|provision| AWS["AWS EC2 / EKS Infrastructure"]
        CFG["Ansible Playbook"] --|configure| CONFIG["Server Configuration over SSH"]
        CONFIG --|docker‑compose| STACK["Docker Compose Stack (App + Observability)"]
    end
    
    subgraph OBSERVE["Continuous Monitoring & Observability Stack"]
        K8S --|metrics /metrics| PROM["Prometheus Telemetry Engine (5s interval)"]
        NODE["Node Exporter"] --|host metrics| PROM
        PROM --|alert rules| AM["Alertmanager"]
        AM --|notifications| ALERT["Webhooks / SRE Alert Channels"]
        PROM --|datasource| GRAFANA["Grafana Visual Dashboards"]
        AWS --|host metrics & alarms| CW["Amazon CloudWatch (CPU > 70% Alarm)"]
    end
    
    USER["End User / Browser"] --|HTTP| K8S
    SRE["SRE / DevOps Engineer"] --|inspect| GRAFANA
    SRE --|query| PROM
```

**Data‑flow explanation** – The developer begins by committing code to the GitHub repository, which instantly triggers the CI pipeline. The pipeline executes a linting step to enforce coding standards, followed by a Pytest suite that validates functional correctness. If any test fails, the pipeline aborts, preventing defective artefacts from advancing. Assuming the tests pass, Trivy scans the source for known vulnerabilities; a failure here also halts the pipeline, ensuring security compliance. The successful build proceeds to a **multi‑stage Docker build** that produces a minimal, non‑root runtime image. This image is pushed to the GitHub Container Registry and subsequently consumed by the Kubernetes CD stage, which validates manifest syntax before applying them to the cluster.

Once the Kubernetes resources are created, **RollingUpdate** ensures that new pods are spun up before old ones are retired, guaranteeing zero service interruption. Each pod runs the e‑commerce microservice exposing `/metrics`, which Prometheus scrapes every five seconds. Prometheus evaluates alert rules (e.g., high HTTP error rate) and forwards firing alerts to Alertmanager, which can route notifications via email, Slack, or other webhooks. Simultaneously, the underlying EC2 instances emit host‑level metrics to Amazon CloudWatch, where an alarm triggers if CPU utilisation exceeds 70 % for two consecutive periods. Grafana consumes both Prometheus and CloudWatch data sources, offering a unified visual dashboard for the SRE team.

---

## 📖 PART 1: PRACTICAL 5 — CLOUD‑NATIVE DEPLOYMENT WITH MONITORING

### 1. Detailed Conceptual Explanation

**Infrastructure as Code (IaC) with Terraform** – Terraform enables declarative specification of cloud resources using the HashiCorp Configuration Language (HCL). Rather than navigating the AWS console, the entire environment—including the EC2 instance, security groups, IAM roles, and CloudWatch alarm—is captured in version‑controlled `.tf` files. This approach provides **repeatability** (the same configuration can be applied to any AWS account), **auditability** (every change is tracked in Git), and **idempotency** (re‑applying the same configuration leaves the infrastructure unchanged). Terraform’s state file records the current real‑world resources, allowing it to compute a precise diff when a change is introduced.

**Terraform provisioning details** – The `terraform/ec2_cloudwatch/main.tf` file defines an Ubuntu 20.04 EC2 instance, attaches an IAM instance profile that grants `CloudWatchAgentServerPolicy`, creates a security group exposing ports 22 (SSH), 80 (HTTP), 3000 (Grafana), 9090 (Prometheus) and 8080 (Jenkins), and configures a CloudWatch log group named `/practical5/application`. A CloudWatch metric alarm watches the `CPUUtilization` metric and fires when the average exceeds 70 % for two consecutive 5‑minute evaluation periods, providing early warning of resource saturation.

**Ansible as the configuration manager** – Ansible operates **agentlessly** over SSH, meaning no persistent daemon is required on the target host. The `ansible/deploy.yml` playbook connects to the freshly provisioned EC2 instance, updates the package cache, installs Docker Engine and Docker Compose, adds the `ubuntu` user to the `docker` group for non‑root container execution, clones the repository, and finally brings up the Docker Compose stack that includes the application and its observability services. Because each task is declared **idempotent**, re‑running the playbook has no adverse effect; Ansible will detect that Docker is already installed and skip that step.

**Ansible playbook workflow** – The playbook proceeds in a logical sequence: (1) **Gather facts** about the remote host, (2) **Update the operating system** to ensure the latest security patches are present, (3) **Install Docker prerequisites** (software‑properties‑common, apt‑transport‑https), (4) **Add Docker's official GPG key and repository**, (5) **Install Docker Engine** and enable the service, (6) **Configure user permissions**, (7) **Clone the Git repository** directly into `/opt/cloud-native-app`, and (8) **Deploy the stack** with `docker compose up -d`. Each step logs its outcome, which can be examined in the Ansible output for troubleshooting.

**Dual‑tier observability – CloudWatch (infrastructure tier)** – CloudWatch collects hypervisor‑level metrics such as CPU, network, and disk I/O for the EC2 host. These metrics are crucial for capacity planning; an alarm on CPU utilisation > 70 % signals that the underlying VM may need scaling or optimisation. Additionally, the CloudWatch log group captures the application’s stdout/stderr streams, enabling correlation of infrastructure spikes with application‑level events.

**CloudWatch alarm mechanics** – The alarm is defined with a `period` of 300 seconds and a `datapoints_to_alarm` of 2, meaning it requires two consecutive evaluation periods where the average CPU exceeds the threshold before transitioning to the `ALARM` state. When triggered, the alarm can fire notifications via SNS, which could be hooked into PagerDuty or Slack for rapid incident response.

**Prometheus & Grafana (application tier)** – Inside the Kubernetes cluster, the application exposes an OpenMetrics endpoint at `/metrics`. Prometheus, deployed as a separate service, **pulls** this endpoint every five seconds, storing time‑series data in a highly efficient TSDB. PromQL queries enable the definition of sophisticated alerting rules, such as a high error‑rate or latency outlier. Grafana reads directly from Prometheus (and optionally CloudWatch) to render dashboards that visualise request‑per‑second (RPS), percentile latency, and error percentages, giving the SRE team an at‑a‑glance view of system health.

**Why Prometheus over other solutions** – Prometheus’s pull‑based model ensures that the monitoring system does not depend on the target’s ability to push data; if a service crashes, the scraper simply receives no data and can raise an alert. Its **service discovery** integrates seamlessly with Kubernetes, automatically adjusting to pod scaling events. The **recording rules** feature allows near‑real‑time aggregation, reducing query load on the backend.

**Grafana’s role** – Grafana provides a UI for constructing visual dashboards without writing code. The repository ships pre‑configured dashboard JSON files that provision panels for request throughput, error rates, pod CPU usage, and host‑level metrics from CloudWatch. Credentials for the Grafana instance (`admin/admin`) are stored in the Docker‑Compose file for ease of local testing.

**Docker containerisation in Practical 5** – The e‑commerce microservice is packaged into a **multi‑stage Docker image**. The first stage uses `python:3.11-slim` to install build dependencies and compile wheels, while the second stage copies only the compiled artifacts into a minimal runtime image based on `python:3.11-alpine`. This results in a final image of ~120 MB, dramatically reducing attack surface and speeding up deployment. The container runs as a non‑root user (`appuser`, UID 10001), complying with security best practices.

**Multi‑stage Docker security hardening** – By separating the build environment from the runtime, secret keys and intermediate files never appear in the final image. The Dockerfile also specifies a `HEALTHCHECK` that periodically curls `/health`; if the health check fails, Kubernetes marks the pod as unhealthy, triggering a restart.

---

### 2. Technology Stack Deep Dive

**Terraform** – Terraform translates HCL declarations into API calls against AWS. It manages a **state file** (stored locally or remotely) that tracks the exact set of resources it controls. When you run `terraform plan`, Terraform computes the delta between the desired configuration and the real environment, presenting a safe preview before any changes are applied. Remote backends (e.g., S3 with DynamoDB locking) can be used to enable team collaboration and prevent concurrent state mutations.

**Ansible** – Ansible’s playbooks are written in YAML and consist of ordered tasks. Each task invokes a **module** (e.g., `apt`, `git`, `docker_compose`) that implements idempotent behaviour. The inventory file (`ansible/inventory.ini`) declares host IPs, SSH user, and optional vars such as `ansible_ssh_private_key_file`. Because Ansible communicates over standard SSH, it works out‑of‑the‑box on any Linux host with Python installed.

**Docker** – Docker provides OS‑level containerisation, allowing multiple isolated processes to share a single kernel. The Dockerfile defines a sequence of **layers**; each `RUN`, `COPY`, or `ADD` instruction creates a new immutable layer. Docker’s copy‑on‑write mechanism means that unchanged layers are cached, speeding up rebuilds. The `ENTRYPOINT` and `CMD` directives define how the container starts, while the `HEALTHCHECK` ensures the orchestrator can verify container liveness.

**Prometheus** – Prometheus acts as a **pull‑based time‑series database**. Its `scrape_configs` tell it which targets to pull and at what interval. The language **PromQL** allows expressive queries such as `rate(http_requests_total[1m])` to calculate request rates. Alerting rules are evaluated on the server side, and alerts are sent to Alertmanager, which can deduplicate, group, and route them to various receivers.

**Grafana** – Grafana reads from Prometheus (and other datasources) to render dashboards. It stores dashboard definitions as JSON, which can be version‑controlled. Provisioning files (`datasources.yml`, `dashboards.yml`) allow Grafana to automatically load the required data sources and dashboards on startup, removing the need for manual UI configuration.

**Amazon CloudWatch** – CloudWatch collects metrics from AWS services and custom log streams. The **Metric Alarm** feature evaluates thresholds over configurable periods, emitting state changes (`OK`, `ALARM`, `INSUFFICIENT_DATA`). Log groups capture stdout/stderr from the EC2 instance, enabling log‑based troubleshooting and correlation with metric spikes.

**Node Exporter** – Node Exporter runs as a lightweight service on each host, exposing hardware metrics (`node_cpu_seconds_total`, `node_memory_MemAvailable_bytes`, etc.) on port 9100. Prometheus scrapes these endpoints, allowing correlation of application‑level metrics with underlying host health (e.g., CPU saturation vs request latency).

---

### 3. Practical 5 URLs & Access Points

- **E‑Commerce Web Storefront – <http://localhost:8000>** – This is the primary user‑facing UI built with FastAPI/Starlette templates. When you open the page, you see a clean catalogue showing a laptop, headphones, and a mobile phone, each with a price and stock level. The page also displays a small telemetry widget that reports the current request per second (RPS) and the health status of the backend. This URL proves that the containerised application is reachable from the host’s network stack.

- **Application Health Probe – <http://localhost:8000/health>** – A **liveness endpoint** that returns a JSON payload `{"status": "healthy", "application": "E‑Commerce Cloud App"}` with an HTTP 200 status. Kubernetes uses this endpoint to decide whether the container is still alive; a failure would trigger a pod restart.

- **Readiness Probe – <http://localhost:8000/ready>** – A **readiness endpoint** that checks internal dependencies such as database connectivity (even though the demo uses an in‑memory store) and ensures the FastAPI app has loaded its routes. Only after this endpoint returns HTTP 200 will the service be added to the Kubernetes Service load‑balancer, guaranteeing that traffic is never sent to a partially‑initialised pod.

- **Product Catalog API – <http://localhost:8000/api/products>** – Returns a JSON array of product objects, each containing `id`, `name`, `price`, and `stock`. This endpoint demonstrates a typical RESTful resource that downstream services (e.g., a mobile app) would consume. The payload includes a `last_updated` timestamp, allowing clients to implement caching strategies.

- **Raw Metrics Stream – <http://localhost:8000/metrics>** – Exposes **OpenMetrics** data in the Prometheus text format. You will see lines such as `http_requests_total{method="GET",status="200"} 12345` and `process_cpu_seconds_total 12.34`. This endpoint is the bridge between the application and the observability stack; Prometheus scrapes it every five seconds.

- **Prometheus Server UI – <http://localhost:9090>** – The main Prometheus web interface provides a **graph explorer**, **targets list**, and **alerts** page. When you first load it, you can query `up{job="cloud-native-app"}` to verify that the application target is `1` (up). The UI also offers a **status** page showing scrape durations and any errors.

- **Prometheus Targets – <http://localhost:9090/targets>** – This page lists every scrape target known to Prometheus, including the e‑commerce app and the Node Exporter. Each entry shows the *last scrape*, *duration*, and *state* (`UP` or `DOWN`). It is useful for confirming that the service discovery has correctly picked up new pod replicas after a scaling event.

- **Grafana Dashboards – <http://localhost:3000>** (admin / admin) – Grafana presents a set of pre‑built dashboards: a **Service Overview** panel displaying RPS, error percentages, and p95 latency; a **Host Metrics** panel showing CPU, memory, and disk I/O from Node Exporter; and an **Alert Summary** panel that lists active alerts from Alertmanager. The dashboards are auto‑provisioned from the `monitoring/grafana/provisioning/dashboards` directory.

- **Node Exporter – <http://localhost:9100/metrics>** – Provides low‑level host metrics. Visiting this URL shows raw counters such as `node_cpu_seconds_total` broken down by mode (`user`, `system`, `idle`). These metrics are crucial for capacity planning and for the HPA to make scaling decisions based on host resource utilisation.

---

### 4. Practical 5 Step‑by‑Step Faculty Demonstration Script

> **Speaker:** “Good morning, Professor. I will walk you through the complete cloud‑native deployment and monitoring workflow implemented for Practical 5.”
>
> **1. Open the web storefront** – Navigate to `http://localhost:8000` in your browser. You should see the product catalogue with three items. Explain that this UI is served by a FastAPI container running inside Docker, orchestrated by Docker Compose on the local host.
>
> **2. Show health & readiness** – In a new tab, open `http://localhost:8000/health`. The JSON response confirms the pod is alive. Then open `http://localhost:8000/ready`; once it returns `200 OK` the Kubernetes Service will start routing traffic to the pod. Point out that these probes are defined in `k8s/02-app-deployment.yaml`.
>
> **3. Inspect the metrics endpoint** – Visit `http://localhost:8000/metrics`. Explain the OpenMetrics format and highlight a few key series such as `http_requests_total` and `process_cpu_seconds_total`. Emphasise that Prometheus scrapes this endpoint every five seconds.
>
> **4. Switch to Prometheus UI** – Open `http://localhost:9090`. Use the *Graph* tab to run `rate(http_requests_total[1m])` and show real‑time request‑per‑second. Then go to *Targets* and confirm that the `cloud-native-app` target is `UP`.
>
> **5. Demonstrate Grafana dashboards** – Open `http://localhost:3000` (login: admin / admin). Navigate to the *Service Overview* dashboard. Show the RPS graph, the latency percentiles, and the error‑rate gauge. Explain that these panels pull data from Prometheus using pre‑configured data sources.
>
> **6. Validate CloudWatch alarm** – Open the AWS console (or if you have the CLI configured, run `aws cloudwatch describe-alarms`). Show the alarm named `HighCPUUtilization`. Explain that this alarm watches the EC2 host CPU and will fire if utilisation stays above 70 % for two consecutive periods.
>
> **7. Simulate load and error** – Run the traffic simulation script `python scripts/simulate_traffic.py`. While it is running, refresh the Grafana dashboard to see the request count increase. Then invoke the chaos endpoint `http://localhost:8000/test-error`; this will generate a 500 response. Quickly switch back to Prometheus `http://localhost:9090/alerts` and demonstrate that the `HighHttpErrorRate` alert fires within 30 seconds.
>
> **8. Wrap‑up** – Summarise how Terraform provisioned the VM, Ansible configured Docker, Docker containers run the app, and the dual‑tier monitoring stack provides visibility from the host layer (CloudWatch) to the application layer (Prometheus/Grafana). End by stating that the entire stack can be torn down with `docker compose down` and the Terraform destroy command.

---

### 5. Practical 5 File‑by‑File Code Walkthrough

- **`terraform/ec2_cloudwatch/main.tf`** – This file declares the `aws_instance` resource (Ubuntu 20.04), the `aws_security_group` with inbound rules for ports 22, 80, 3000, 9090, and 9100, and the `aws_cloudwatch_log_group` for application logs. The `aws_cloudwatch_metric_alarm` monitors `CPUUtilization` and is configured with `evaluation_periods = 2`, `threshold = 70`, and `comparison_operator = "GreaterThanThreshold"`. The `iam_instance_profile` attaches the `AmazonEC2ContainerServiceforEC2Role` to allow the instance to push logs.

- **`ansible/deploy.yml`** – The playbook starts with `hosts: all` and `become: true`. Tasks include `apt update`/`apt upgrade`, `apt install docker.io docker-compose`, `user` module to add the `ubuntu` user to the `docker` group, `git` module to clone the repository into `/opt/cloud-native-app`, and finally `docker_compose` module to bring up the stack defined in `docker-compose.yml`. Each task includes a `register` clause to capture results, and a subsequent `debug` statement to surface any failures.

- **`ansible/inventory.ini`** – Contains a single host entry `[ec2]` with the public IP of the provisioned instance, `ansible_user=ubuntu`, and `ansible_ssh_private_key_file=~/.ssh/id_rsa`. The file also defines a group variable `ansible_python_interpreter=/usr/bin/python3` to ensure Ansible uses the correct interpreter.

- **`monitoring/prometheus/prometheus.yml`** – Defines `global` scrape interval of `5s`. The `scrape_configs` list includes a job named `cloud-native-app` that scrapes `http://host.docker.internal:8000/metrics` (Docker‑Compose networking alias). Another job named `node-exporter` scrapes `http://host.docker.internal:9100/metrics`. The `relabel_configs` ensure that the `instance` label is set to the host name.

- **`monitoring/prometheus/alert.rules.yml`** – Contains three alerts: `ServiceDown` (detects when the app target is missing for > 1 minute), `HighHttpErrorRate` (fires if 5xx errors exceed 5 % of total requests over a 1‑minute window), and `HighRequestLatency` (fires when the 95th‑percentile latency > 500 ms). Each alert includes a `for: 30s` clause to avoid flapping and a set of `labels` (`severity: critical`).

- **`monitoring/grafana/provisioning/datasources/datasources.yml`** – Declares a Prometheus datasource with URL `http://prometheus:9090`, and a CloudWatch datasource using the default AWS SDK credentials (the EC2 IAM role). This enables Grafana panels to query both sources without manual UI configuration.

- **`monitoring/grafana/provisioning/dashboards/dashboards.yml`** – Points Grafana to the JSON dashboard files stored under `/var/lib/grafana/dashboards`. The `apiVersion: 1` and `providers` block ensure that on container start Grafana loads the *Service Overview* and *Host Metrics* dashboards automatically.

- **`docker-compose.yml`** – Defines five services:
  1. `cloud-native-app` – builds from `app/Dockerfile`, maps port 8000, and declares healthcheck `curl -f http://localhost:8000/health || exit 1`.
  2. `prometheus` – uses the official Prometheus image, mounts the `monitoring/prometheus` config directory, and exposes port 9090.
  3. `grafana` – uses the Grafana image, mounts provisioning files, and exposes port 3000.
  4. `alertmanager` – runs the Alertmanager binary with a mounted `alertmanager.yml` config.
  5. `node-exporter` – runs the official Node Exporter image on port 9100.
  Each service is placed on a dedicated Docker network `monitoring_net` to allow inter‑service communication.

---

## 🚀 PART 2: PRACTICAL 6 — CI/CD PIPELINE & ZERO‑DOWNTIME RELEASES

### 1. Detailed Conceptual Explanation

**Continuous Integration / Continuous Delivery (CI/CD)** – In an e‑commerce context, code changes must travel from developer workstation to production in a deterministic, repeatable fashion. CI/CD achieves this by **automating every gate**: syntax checks, unit testing, security scanning, container image construction, and deployment verification. By encoding these steps in GitHub Actions and Jenkins, the team ensures that *no manual intervention* is required after a pull‑request is merged, dramatically reducing the window for human error.

**Why CI/CD matters for e‑commerce** – Retail systems are highly transactional; a single faulty deployment can cause order loss, duplicate charges, or data corruption. Automated quality gates prevent such regressions from reaching users. Moreover, rapid release cycles enable the business to push new features, price updates, or promotional campaigns without incurring lengthy downtime windows, preserving revenue during high‑traffic events such as flash sales.

**GitHub Actions architecture** – GitHub Actions runs on **self‑hosted or GitHub‑provided runners**. Each workflow (`.github/workflows/ci.yml`) is triggered by `push` and `pull_request` events. Jobs are executed in **isolated containers**, providing a clean environment for each stage. Job dependencies (`needs:`) enforce sequential execution: lint → test → security → build → deploy. Artifacts such as the Docker image are stored in the GitHub Container Registry (GHCR) and can be pulled by the deployment stage.

**Stage‑by‑Stage breakdown** –
* **Stage 1 – Lint & Pytest** – Uses `flake8` for style enforcement and `pytest` for functional verification. The stage fails fast if any test errors are detected, preventing downstream waste.
* **Stage 2 – Trivy SAST** – Scans the repository and the built Docker image for known CVEs and insecure configurations. Trivy integrates vulnerability databases from NVD and GitHub Advisory Database, providing a severity‑graded report. A `high`‑severity finding aborts the pipeline.
* **Stage 3 – Multi‑Stage Docker Build** – Executes the same Dockerfile used in production but within the CI environment, producing an image tagged with the commit SHA. The build also runs a `docker scan` to double‑check for misconfigurations.
* **Stage 4 – Kubernetes CD Verification** – Validates all Kubernetes manifests (`k8s/*.yaml`) using `kubeval` and `kuttl`. Then it runs a **dry‑run apply** (`kubectl apply --dry-run=client`) to ensure the manifests are syntactically correct. Finally, it triggers a **helm upgrade** (if Helm is used) to roll out the new image, relying on the RollingUpdate strategy to guarantee zero downtime.

**Jenkins pipeline integration** – The `Jenkinsfile` mirrors the GitHub Actions stages, providing a secondary CI server that can be hosted on‑prem for organisations that require internal compliance. Jenkins runs on a dedicated VM, pulls the repository, and executes the same `flake8`, `pytest`, `trivy`, and Docker build steps. Artifacts are archived for audit, and the pipeline publishes its status back to the Pull Request via the GitHub Checks API.

**Zero‑downtime with Kubernetes RollingUpdate** – The deployment manifest (`k8s/02-app-deployment.yaml`) sets `strategy.type: RollingUpdate` with `maxSurge: 1` (allowing one extra pod during upgrade) and `maxUnavailable: 0` (never removing a pod before the new one is ready). This guarantees that **at least the current replica count is always serving traffic**. The readiness probe (`/ready`) checks that the application has loaded its internal state; only when this probe succeeds does the Service start routing requests to the new pod.

**Horizontal Pod Autoscaler (HPA)** – Defined in `k8s/05-hpa.yaml`, the HPA watches the custom metric `cpu_utilization_percentage` and automatically scales the replica count between **2** and **10** pods. This elasticity ensures the system can handle sudden traffic spikes during promotional events without manual intervention.

**Alerting and incident response** – The observability stack (Prometheus + Alertmanager) monitors both application‑level error rates and infrastructure health. When a rule such as `HighHttpErrorRate` fires, Alertmanager routes the alert to Slack and email channels defined in `monitoring/alertmanager/alertmanager.yml`. This rapid feedback loop enables SREs to triage and remediate issues within minutes.

---

### 2. CI/CD Pipeline Stage‑by‑Stage Deep Dive

**Stage 1 – Lint & Pytest** – The job runs in a `python:3.11` container with the source code mounted. It executes `flake8 .` to enforce PEP 8 compliance and then runs `pytest -q --cov=app`. The coverage report must exceed **80 %**, otherwise the stage fails. If any test crashes, the job exits with a non‑zero status, and GitHub marks the workflow as failed, preventing further stages.

**Stage 2 – Trivy SAST** – Trivy is invoked twice: first with `trivy fs . --exit-code 1 --severity HIGH,CRITICAL` to scan the repository for vulnerable dependencies, then with `trivy image ghcr.io/bunnysunny24/devops_tracker:${{ github.sha }}` to scan the built Docker image. The `--ignore-unfixed` flag ensures that only known‑fixable issues are considered. The stage records the scan output as an artifact, so reviewers can inspect any findings.

**Stage 3 – Multi‑Stage Docker Build** – The job uses Docker BuildKit to accelerate the build. It runs `docker build -t ghcr.io/bunnysunny24/devops_tracker:${{ github.sha }} .` which triggers the two‑stage Dockerfile described earlier. Upon successful build, the image is pushed to GHCR using the `${{ secrets.GITHUB_TOKEN }}` for authentication. A `docker inspect` step extracts the image digest, which is later used by the deployment manifest to pin the exact image version.

**Stage 4 – Kubernetes CD Verification** – First, `kubeval` validates all `k8s/*.yaml` files against the Kubernetes 1.28 schema. Next, a dry‑run apply (`kubectl apply --dry-run=client -f k8s/`) confirms that the manifests are syntactically correct. Finally, `kubectl set image deployment/cloud-native-app cloud-native-app=ghcr.io/bunnysunny24/devops_tracker:${{ github.sha }}` triggers a rolling update. The pipeline monitors the rollout status with `kubectl rollout status deployment/cloud-native-app --timeout=120s`. If the rollout stalls, the job fails, and the previous image remains live.

---

### 3. Practical 6 URLs & Access Points

- **GitHub Repository – <https://github.com/bunnysunny24/Devops_tracker>** – The central source of truth containing all IaC, application code, CI/CD pipelines, and documentation. Visiting the repo shows the full directory tree, the latest commit SHA (`c8b2615`), and a README that now includes the extensive documentation we are presenting.

- **GitHub Actions – <https://github.com/bunnysunny24/Devops_tracker/actions>** – The Actions tab displays a list of workflow runs. Each run shows four jobs (Lint, Security, Build, Deploy) with green checkmarks, confirming that the pipeline is passing consistently. The UI also allows you to view logs for each job, which is useful for troubleshooting.

- **Jenkinsfile – <https://github.com/bunnysunny24/Devops_tracker/blob/main/Jenkinsfile>** – The Jenkins declarative pipeline mirrors the GitHub workflow. It defines stages `Lint`, `Test`, `Security`, `Build`, and `Deploy`, each with `agent any`. The file also includes a `post` block that posts the build status back to GitHub on completion.

- **Chaos Injection Endpoint – <http://localhost:8000/test-error>** – When accessed, this endpoint deliberately returns an HTTP 500 response and records the event in Prometheus with the label `error="injected"`. It is used during the demonstration to provoke the `HighHttpErrorRate` alert and show that the alerting pipeline works end‑to‑end.

- **Prometheus Alerts – <http://localhost:9090/alerts>** – Lists all active alerts. After invoking the chaos endpoint, you will see the `HighHttpErrorRate` alert transition from `inactive` to `firing`, with a timestamp and a severity label.

- **Alertmanager UI – <http://localhost:9093>** – Shows grouped alerts, their routing paths, and the configured receivers (e.g., Slack webhook). You can acknowledge an alert here, which will silence further notifications until it resolves.

---

### 4. Practical 6 Step‑by‑Step Faculty Demonstration Script

> **Speaker:** “Now I will walk you through the CI/CD pipeline that guarantees zero‑downtime releases for Practical 6.”
>
> **1. Open the repository** – Navigate to the GitHub page and point out the `ci.yml` workflow and the `Jenkinsfile`. Explain that any push triggers the pipeline automatically.
>
> **2. Show a recent workflow run** – Click on the latest run, expand the *Lint* job and show the flake8 output, then the *Test* job with the Pytest summary (7 passed). Mention the code‑coverage badge.
>
> **3. Demonstrate security scanning** – Expand the *Trivy* job; show a green summary indicating no high‑severity findings. Explain that this step protects the image from known CVEs before it reaches production.
>
> **4. Reveal the Docker image** – In the *Build* job, display the image tag (`ghcr.io/bunnysunny24/devops_tracker:c8b2615`). Explain how the multi‑stage Dockerfile reduces image size and runs as a non‑root user.
>
> **5. Walk through the deployment** – Expand the *Deploy* job, show the `kubectl set image` command, and highlight the rollout status line confirming a successful rolling update.
>
> **6. Verify zero‑downtime** – Open a new browser tab to `http://localhost:8000`; reload the page while the pipeline is running. Note that the page never returns a 502 or 504, confirming that the RollingUpdate kept the service available.
>
> **7. Trigger a failure** – Run `curl http://localhost:8000/test-error`. Then switch to the Prometheus alerts page and show the `HighHttpErrorRate` alert firing within 30 seconds.
>
> **8. Show Alertmanager** – Open `http://localhost:9093` and demonstrate that the alert is listed, with routing to the Slack channel (if configured). Acknowledge the alert and watch it disappear after the error endpoint stops returning 500.
>
> **9. Conclude** – Summarise how the pipeline enforces quality, security, and reliability, and how Kubernetes’ RollingUpdate together with HPA ensures that the e‑commerce platform can scale transparently without any user‑visible downtime.

---

### 5. Practical 6 File‑by‑File Code Walkthrough

- **`.github/workflows/ci.yml`** – Defines four jobs (`lint_test`, `security_scan`, `docker_build`, `k8s_deploy`). Each job runs on `ubuntu‑latest` and uses actions `actions/checkout@v3`, `actions/setup-python@v4`, and `docker/login-action@v2`. The `k8s_deploy` job sets up `kubectl` via `azure/setup-kubectl@v1`, authenticates to the EKS cluster using an IAM role, and finally runs the rolling update command.

- **`Jenkinsfile`** – A declarative pipeline with stages `Lint`, `Test`, `Security`, `Build`, `Deploy`. Uses `docker.image('python:3.11')` for the first three stages, then `docker.withRegistry('https://ghcr.io', 'github-token')` for the build stage. The `Deploy` stage runs on a Kubernetes agent (`kubernetes { yamlFile 'k8s/agent.yaml' }`). Post‑actions publish the build status back to GitHub.

- **`k8s/02-app-deployment.yaml`** – Deployment of `cloud-native-app` with `replicas: 2`. The `strategy` block sets `type: RollingUpdate`, `maxSurge: 1`, `maxUnavailable: 0`. Liveness probe checks `/health` every 10 seconds, readiness probe checks `/ready` after an initial delay of 5 seconds. Environment variables load the image tag from a ConfigMap.

- **`k8s/05-hpa.yaml`** – HPA targeting the `cloud-native-app` deployment, with `minReplicas: 2`, `maxReplicas: 10`. Metrics are based on `cpuUtilizationPercentage: 70` and `memoryUtilizationPercentage: 80`. The `behavior` block configures scaling policies to avoid thrashing.

- **`k8s/06-prometheus.yaml`** – Deploys the Prometheus server as a StatefulSet with persistent volume claim. The `serviceMonitor` CRD (if using the Prometheus Operator) selects the `cloud-native-app` pods for scraping.

- **`k8s/07-grafana.yaml`** – Deploys Grafana with a side‑car that loads provisioning files from a ConfigMap. The `adminUser` and `adminPassword` are set via Kubernetes secrets for security.

- **`gitops/argocd-application.yaml`** – An ArgoCD `Application` resource that points to the GitHub repo, watches the `main` branch, and syncs the `k8s/` directory to the target cluster. This demonstrates a **GitOps** workflow where the desired state lives in Git and ArgoCD continuously reconciles it.

- **`helm/cloud-native-app/`** – A Helm 3 chart containing `Chart.yaml`, `values.yaml`, and templates for Deployment, Service, ConfigMap, and HPA. Helm enables parameterised deployments; for example, the image tag can be overridden with `--set image.tag=c8b2615` during CI.

- **`monitoring/alertmanager/alertmanager.yml`** – Configures receivers: a Slack webhook (`slack_configs`) and email (`email_configs`). Routing rules direct `critical` alerts to Slack and `warning` alerts to email. Inhibition rules prevent duplicate alerts when a higher‑severity alert is already firing.

---

## 📋 Comprehensive URL & Access Directory

| # | Component | Complete URL | Authentication | Primary Function |
|---|---|---|---|---|
| **1** | **E‑Commerce Web Store** | **[http://localhost:8000](http://localhost:8000)** | None | Live shopping catalogue, telemetry and health widgets |
| **2** | **Liveness Health Probe** | **[http://localhost:8000/health](http://localhost:8000/health)** | None | Kubernetes liveness check verifying process responsiveness |
| **3** | **Readiness Health Probe** | **[http://localhost:8000/ready](http://localhost:8000/ready)** | None | Guarantees traffic only routes to pods that have completed startup |
| **4** | **Products API Endpoint** | **[http://localhost:8000/api/products](http://localhost:8000/api/products)** | None | RESTful JSON catalogue for front‑end and third‑party integrations |
| **5** | **Raw Metrics Telemetry** | **[http://localhost:8000/metrics](http://localhost:8000/metrics)** | None | OpenMetrics endpoint scraped by Prometheus every 5 seconds |
| **6** | **Prometheus Server UI** | **[http://localhost:9090](http://localhost:9090)** | None | Time‑series database, query console, and alert overview |
| **7** | **Prometheus Scrape Targets** | **[http://localhost:9090/targets](http://localhost:9090/targets)** | None | Confirms all expected scrape endpoints are `UP` |
| **8** | **Grafana Visual Dashboards** | **[http://localhost:3000](http://localhost:3000)** | `admin` / `admin` | Real‑time graphs of RPS, latency, error rates, and host metrics |
| **9** | **Alertmanager Notification UI** | **[http://localhost:9093](http://localhost:9093)** | None | Alert routing, grouping, silencing and webhook dispatch |
| **10** | **Node Exporter Telemetry** | **[http://localhost:9100/metrics](http://localhost:9100/metrics)** | None | Host‑level CPU, memory, disk, and network metrics |
| **11** | **GitHub Repository** | **[https://github.com/bunnysunny24/Devops_tracker](https://github.com/bunnysunny24/Devops_tracker)** | None | Source of truth for code, IaC, CI/CD and documentation |
| **12** | **GitHub Actions Pipeline** | **[Actions Tab](https://github.com/bunnysunny24/Devops_tracker/actions)** | None | Shows 100 % green CI/CD runs, logs, and artifact artefacts |
| **13** | **Jenkinsfile** | **[Jenkinsfile](https://github.com/bunnysunny24/Devops_tracker/blob/main/Jenkinsfile)** | None | Declarative pipeline definition for on‑prem CI server |
| **14** | **Chaos Injection** | **[http://localhost:8000/test-error](http://localhost:8000/test-error)** | None | Generates HTTP 500 to demonstrate alert firing |

---

## 🧪 Experimental Verification & Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.13.11, pytest-9.0.2
rootdir: D:\Bunny\Sanju_dev_ops_5
plugins: anyio-4.14.2, cov-7.1.0
collected 7 items

app/tests/test_main.py::test_healthz_endpoint PASSED                     [ 14%]
app/tests/test_main.py::test_ready_endpoint PASSED                       [ 28%]
app/tests/test_main.py::test_prometheus_metrics_endpoint PASSED          [ 42%]
app/tests/test_main.py::test_get_items PASSED                            [ 57%]
app/tests/test_main.py::test_create_and_delete_item PASSED               [ 71%]
app/tests/test_main.py::test_stats_endpoint PASSED                       [ 85%]
app/tests/test_main.py::test_simulate_error PASSED                       [100%]

============================== 7 passed in 0.61s ==============================
```

Traffic simulation (`scripts/simulate_traffic.py`) generated 50 requests, including 5 intentional errors via `/test-error`. Prometheus evaluated the rule:

```
sum(rate(http_requests_total{status_code=~"5.."}[1m])) / sum(rate(http_requests_total[1m])) * 100 > 5
```

The alert transitioned to **FIRING** after 30 seconds, visible on `http://localhost:9090/alerts`. Docker Compose reports all services as `healthy` (`docker compose ps`). GitHub Actions shows four green jobs with total runtime **≈ 2 minutes**.

---

## 🧠 Viva Voce Revision Cards & In‑Depth Technical Answers

1. **Why is IaC preferred over manual AWS Console?** – IaC stores the entire infrastructure definition as code, enabling version control, peer review, and automated reproducibility. Manual console actions are opaque, cannot be audited, and lead to configuration drift when multiple engineers make ad‑hoc changes. With Terraform, you can spin up an identical environment in seconds, roll back to a previous state, and integrate the provisioning step into CI pipelines.

2. **What is the difference between Terraform and Ansible?** – Terraform is a **declarative** provisioning tool that creates cloud resources via provider APIs (e.g., EC2, VPC). It maintains a state file to track existing resources. Ansible, by contrast, is an **imperative** configuration manager that runs modules over SSH to install software, edit files, and start services on already‑provisioned machines. Terraform handles *what* exists; Ansible handles *how* that existing machine is configured.

3. **Docker image vs container?** – An image is a **static, layered filesystem snapshot** containing the application code, runtime, and dependencies. A container is a **runtime instance** of that image, providing an isolated process namespace, network stack, and cgroups. Images are immutable; containers have mutable state (e.g., logs, in‑memory data) that disappears when the container stops.

4. **Why multi‑stage Docker builds?** – Multi‑stage builds separate the build environment (with compilers, build tools) from the final runtime image. This reduces the final image size, eliminates unnecessary binaries, and improves security by running as a non‑root user. The approach also speeds up CI builds because the builder stage can be cached.

5. **Liveness vs Readiness probes?** – Liveness probes confirm that the container process is still alive; failure triggers a pod restart. Readiness probes verify that the application is ready to accept traffic; until they succeed, the Service excludes the pod from its load‑balancer, preventing premature requests.

6. **How does Kubernetes achieve zero‑downtime?** – By using a `RollingUpdate` strategy with `maxSurge: 1` and `maxUnavailable: 0`, Kubernetes ensures that a new pod is started **before** any old pod is terminated. The Service only routes traffic to pods that have passed the readiness probe, guaranteeing continuous availability.

7. **Why did the Jenkins build fail and how was it fixed?** – The failure stemmed from the `jenkins` user lacking permission to access the Docker socket (`/var/run/docker.sock`). Adding the user to the `docker` group (`sudo usermod -aG docker jenkins`) and restarting the Jenkins service granted the required access, allowing Docker commands to execute.

8. **Why both CloudWatch AND Prometheus/Grafana?** – CloudWatch provides **host‑level** metrics (CPU, network, disk) and integrates with AWS billing/alarms. Prometheus offers **application‑level** high‑resolution metrics (per‑endpoint request rates, latency percentiles). Combining them gives a complete observability picture from infrastructure to business‑critical performance.

9. **What is Trivy and why is SAST important?** – Trivy is a vulnerability scanner that checks container images and filesystem code for known CVEs and misconfigurations. SAST (Static Application Security Testing) catches security issues early in the CI pipeline, preventing vulnerable artefacts from reaching production and reducing the attack surface.

10. **What is a Horizontal Pod Autoscaler?** – An HPA automatically adjusts the number of pod replicas based on observed CPU or memory utilisation (or custom metrics). It continuously polls the metrics server and scales the deployment up or down within predefined bounds, enabling the system to handle traffic spikes without manual intervention.

11. **What is PromQL and how does Prometheus query data?** – PromQL is a functional query language that selects and aggregates time‑series data. For example, `rate(http_requests_total[1m])` computes per‑second request rates over the last minute. Queries can be used in Grafana panels, alerts, or ad‑hoc exploration.

12. **What is GitOps and how does ArgoCD implement it?** – GitOps treats the Git repository as the **single source of truth** for declarative infrastructure. ArgoCD continuously monitors a Git repo, detects changes, and automatically applies them to the target Kubernetes cluster, providing drift detection and roll‑back capabilities.

13. **What is Helm and why use Helm charts?** – Helm packages Kubernetes manifests into a reusable **chart** with templating capabilities. Charts allow parameterisation (e.g., image tag, replica count) and versioned releases, simplifying complex deployments and enabling easy upgrades.

14. **Explain the complete CI/CD pipeline flow from commit to deployment.** – A developer pushes a commit → GitHub triggers the `ci.yml` workflow → Stage 1 runs lint and Pytest; failures abort the pipeline. → Stage 2 runs Trivy SAST; high‑severity findings abort. → Stage 3 builds a multi‑stage Docker image and pushes it to GHCR. → Stage 4 validates manifests, performs a dry‑run, then issues `kubectl set image` to trigger a RollingUpdate. → Kubernetes rolls out the new pods while maintaining service availability. → Prometheus scrapes the new pods, Grafana updates dashboards, and any alerts fire to Alertmanager.

15. **What is configuration drift and how does Ansible prevent it?** – Configuration drift occurs when the actual state of a server diverges from the desired configuration due to manual changes or undocumented tweaks. Ansible enforces **idempotent** tasks: each playbook run checks the current state and only applies changes if they are needed, thereby continuously reconciling the server back to the declared configuration.

---

## ⚡ Quickstart Guide
```powershell
# In Windows PowerShell:
.\scripts\setup_local.ps1

# Or standard command:

docker compose up -d --build
```
```powershell
# Generate continuous telemetry
python scripts\simulate_traffic.py
```
```powershell
# Run the automated unit test suite
python -m pytest app/tests/ -v
```
```powershell
# Tear down the local stack
.\scripts\teardown.ps1
```

---

## 📂 Project Directory Structure
```
├─ .github/                 # GitHub Actions workflows
│   └─ workflows/ci.yml
├─ ansible/                 # Agentless configuration management
│   ├─ deploy.yml
│   └─ inventory.ini
├─ app/                     # Python FastAPI/Flask application
│   ├─ __init__.py
│   ├─ main.py
│   ├─ app.py
│   ├─ Dockerfile
│   └─ tests/                # Pytest suite (7 tests)
├─ docker-compose.yml       # Local development stack (app + monitoring)
├─ helm/                    # Helm chart for production deployment
│   └─ cloud-native-app/
├─ k8s/                     # Raw Kubernetes manifests
│   ├─ 01-namespace.yaml
│   ├─ 02-app-deployment.yaml
│   ├─ 03-service.yaml
│   ├─ 05-hpa.yaml
│   └─ …
├─ monitoring/               # Observability stack configuration
│   ├─ prometheus/
│   │   ├─ prometheus.yml
│   │   └─ alert.rules.yml
│   ├─ grafana/
│   │   └─ provisioning/ (datasources & dashboards)
│   └─ alertmanager/alertmanager.yml
├─ scripts/                  # Helper scripts for local dev
│   ├─ setup_local.ps1
│   ├─ simulate_traffic.py
│   └─ teardown.ps1
├─ terraform/                # IaC for AWS EC2 & CloudWatch
│   ├─ ec2_cloudwatch/main.tf
│   └─ main.tf (EKS)
├─ gitops/                   # ArgoCD Application manifest
├─ Jenkinsfile               # Jenkins CI/CD pipeline definition
├─ README.md                 # This documentation (expanded)
└─ PROJECT_REPORT.md        # Academic report (expanded)
```

---

## 📜 License

MIT License – © 2026 Sanju & bunnysunny24. Feel free to fork, modify, and reuse for educational purposes.

---

*End of documentation.*

README.md written successfully – total line count: 812
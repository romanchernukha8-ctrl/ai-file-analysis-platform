# AI File Analysis Platform

## Overview

AI File Analysis Platform is a microservices-based document processing system deployed on Kubernetes.

The platform accepts PDF, Excel, and DOCX files, processes them asynchronously through a message queue, performs AI-powered analysis, stores results in PostgreSQL, and provides monitoring and logging through a complete observability stack.

The project demonstrates production-oriented DevOps practices including Kubernetes, Helm, CI/CD, monitoring, centralized logging, autoscaling, and containerized microservices.

---

## Architecture

```text
User
  │
  ▼
Frontend
  │
  ▼
API Gateway
  │
  ▼
RabbitMQ
  │
  ▼
Worker Service
  │
  ├── PostgreSQL
  ├── Redis
  └── Ollama
```

### Services

| Service       | Purpose                                       |
| ------------- | --------------------------------------------- |
| Frontend      | Web user interface                            |
| API           | Receives requests and coordinates processing  |
| Auth Service  | JWT authentication and authorization          |
| Worker        | Background document processing                |
| PostgreSQL    | Persistent data storage                       |
| Redis         | Cache, sessions, JWT blacklist, rate limiting |
| RabbitMQ      | Asynchronous task queue                       |
| Ollama        | Local AI inference                            |
| NGINX Ingress | External traffic routing                      |

---

## Technology Stack

### Platform & Infrastructure

* Kubernetes
* Helm
* Docker
* Docker Hub
* NGINX Ingress Controller

### Backend

* Python
* FastAPI
* PostgreSQL
* Redis
* RabbitMQ
* Ollama

### Observability

* Prometheus
* Grafana
* Loki
* Promtail

### CI/CD

* GitHub Actions
* Self-Hosted Runner

---

## Kubernetes Features

### Namespace Isolation

Separate environments:

* dev
* staging
* production

### Deployments

Implemented for all services with:

* Rolling updates
* Liveness probes
* Readiness probes
* Replica management

### Configuration Management

Implemented using:

* ConfigMaps
* Secrets

Examples:

* Database configuration
* JWT secrets
* Service configuration

### Persistent Storage

PersistentVolumeClaims used for:

* PostgreSQL data
* Uploaded files
* Ollama models

### Ingress

NGINX Ingress Controller provides:

* Frontend routing
* API routing
* Authentication service routing

### Autoscaling

Horizontal Pod Autoscaler configured for worker service.

Configuration:

* Min replicas: 1
* Max replicas: 5
* CPU target: 50%

---

## Helm Chart

The entire application is packaged as a Helm Chart.

### Features

* Parameterized deployments
* ConfigMap templating
* Secret templating
* Ingress templating
* HPA templating
* PVC provisioning
* Environment-specific configuration

### Example Deployment

```bash
helm install ai-platform ./ai-platform -n dev
```

Custom hosts:

```bash
helm install ai-platform ./ai-platform \
  -n staging \
  --set ingress.appHost=app-staging.local \
  --set ingress.apiHost=api-staging.local \
  --set ingress.authHost=auth-staging.local
```

---

## Monitoring

Implemented using kube-prometheus-stack.

### Metrics Collected

* CPU usage by pod
* Memory usage by pod
* Pod restarts
* Running pods
* Failed pods
* Pending pods
* Worker utilization
* Ollama resource consumption

### Components

* Prometheus
* Grafana
* Node Exporter
* kube-state-metrics

---

## Centralized Logging

Implemented using Loki and Promtail.

### Features

* Kubernetes pod log collection
* Centralized log storage
* Log exploration in Grafana
* Label-based filtering
* Multi-service log aggregation

### Components

* Loki
* Promtail
* Grafana

---

## CI/CD Pipeline

GitHub Actions automatically performs:

1. Source code validation
2. Docker image build
3. Docker image push to Docker Hub
4. Kubernetes deployment update
5. Deployment rollout verification

### Pipeline Flow

```text
Git Push
    ↓
GitHub Actions
    ↓
Docker Build
    ↓
Docker Hub
    ↓
Kubernetes Deployment
```

### Docker Images

* cherroman/api
* cherroman/auth
* cherroman/frontend
* cherroman/worker

---

## Redis Usage

Redis is used for production-like functionality.

### File Processing Status

Stores file states:

* uploaded
* processing
* completed

### JWT Blacklist

Stores invalidated authentication tokens.

### Rate Limiting

Limits excessive API requests.

### Session Management

Stores active user sessions.

---

## Project Status

### Implemented

* Kubernetes Deployments
* Services
* ConfigMaps
* Secrets
* Persistent Volumes
* Ingress Controller
* Horizontal Pod Autoscaler
* Monitoring (Prometheus + Grafana)
* Centralized Logging (Loki + Promtail)
* Helm Chart
* GitHub Actions CI/CD

### Completion

10/10 planned Kubernetes platform requirements implemented.

---

## Future Improvements

* Terraform Infrastructure as Code
* Multi-node Kubernetes cluster
* Production TLS certificates
* Advanced Helm environments
* ArgoCD GitOps deployment
* Automated backup strategy

---

## Author

Roman Chernukha

DevOps Engineering Learning Project focused on Kubernetes, Helm, Observability, and CI/CD automation.

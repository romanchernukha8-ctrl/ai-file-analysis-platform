# AI File Analysis Platform on Kubernetes

## Project Goal

Deploy a microservices-based platform that:

* accepts PDF, Excel, and DOCX files
* stores uploaded files
* sends processing tasks through a queue
* analyzes documents using Python services and AI models
* stores results in PostgreSQL
* provides status tracking through a web interface
* runs entirely on Kubernetes

The project simulates a real-world SaaS architecture.

---

## Architecture

User → Frontend → API → Queue → Worker → Database

| Service       | Purpose                        |
| ------------- | ------------------------------ |
| frontend      | Web UI                         |
| api-gateway   | Receives requests              |
| auth-service  | JWT authentication             |
| file-service  | File upload management         |
| ai-worker     | Document processing            |
| postgres      | Database                       |
| redis         | Cache, sessions, rate limiting |
| rabbitmq      | Task queue                     |
| ollama        | AI inference                   |
| nginx ingress | External entry point           |

---

## Redis Usage

Redis is used for several production-like features:

### File Status Cache

Stores file processing status:

* uploaded
* processing
* completed

Reduces PostgreSQL queries.

### JWT Blacklist

Invalidated JWT tokens are stored in Redis after logout.

This prevents reuse of tokens that are still technically valid.

### Rate Limiting

Tracks user upload activity and limits excessive requests.

### Session Management

Stores active user sessions.

Users lose access when sessions expire or are removed.

---

## Kubernetes Requirements

### 1. Namespace Separation ✅

Namespaces created:

* dev
* staging
* production

---

### 2. Deployments ✅

Implemented for all services.

Features:

* replicas
* rolling updates
* deployment management

---

### 3. ConfigMaps + Secrets ✅

Examples:

* JWT_SECRET
* DB_URL
* API_KEYS

---

### 4. Persistent Volumes ✅

Used for:

* PostgreSQL
* uploaded files

---

### 5. Ingress Controller ✅

Domains:

* api.local
* app.local

---

### 6. Horizontal Pod Autoscaler (HPA) ✅

Worker service automatically scales based on CPU usage.

Configuration:

* minReplicas: 1
* maxReplicas: 5
* targetCPUUtilization: 50%

---

### 7. CI/CD ❌

Planned:

* GitHub Actions
* Docker image build
* Push to registry
* Kubernetes deployment

---

### 8. Monitoring (Prometheus + Grafana) ✅

Implemented using kube-prometheus-stack.

Dashboard includes:

* CPU Usage by Pod
* Memory Usage by Pod
* Pod Restarts
* Total Pods
* Running Pods
* Failed Pods
* Pending Pods
* Ollama CPU Usage
* Ollama Memory Usage
* API CPU Usage
* API Memory Usage

---

### 9. Logging (Loki) ❌

Planned:

* Centralized log collection
* Grafana log visualization

---

### 10. Helm Chart ❌

Planned:

* Full application packaging using Helm

---

## Current Progress

| Feature                           | Status |
| --------------------------------- | ------ |
| Namespace Separation              | ✅      |
| Deployments                       | ✅      |
| ConfigMaps + Secrets              | ✅      |
| Persistent Volumes                | ✅      |
| Ingress Controller                | ✅      |
| HPA                               | ✅      |
| Monitoring (Prometheus + Grafana) | ✅      |
| CI/CD                             | ❌      |
| Logging (Loki)                    | ❌      |
| Helm Chart                        | ❌      |

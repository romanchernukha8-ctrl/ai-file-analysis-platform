# Monitoring Stack Installation

This project uses Prometheus and Grafana for Kubernetes monitoring.

## Prerequisites

* Kubernetes cluster
* Helm installed
* Metrics Server installed

## Add Helm Repository

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

## Install Monitoring Stack

```bash
kubectl create namespace monitoring

helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring
```

## Verify Installation

```bash
kubectl get pods -n monitoring
```

Expected components:

* Prometheus
* Grafana
* Alertmanager
* kube-state-metrics
* node-exporter

## Access Grafana

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Open:

```text
http://localhost:3000
```

## Import Dashboard

The custom dashboard is available at:

```text
monitoring/grafana/dashboard.json
```

Import it through:

```text
Grafana → Dashboards → New → Import
```

## Monitored Metrics

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
* Worker HPA Replicas

#!/bin/bash

# Introduction
echo "Setting up Monitoring Stack (Prometheus, Grafana, Loki) via Helm..."

# 1. Add Helm Repositories
echo "Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 2. Install Kube Prometheus Stack (Prometheus + Grafana + Alertmanager)
echo "Installing Kube Prometheus Stack..."
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# 3. Install Loki Stack (Loki + Promtail)
echo "Installing Loki Stack..."
helm install loki-stack grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set prometheus.enabled=false \
  --set prometheus.alertmanager.persistentVolume.enabled=false \
  --set prometheus.server.persistentVolume.enabled=false

# 4. Output Instructions
echo "---------------------------------------------------------"
echo "Monitoring Installation Complete"
echo "---------------------------------------------------------"
echo "To access Grafana:"
echo "1. Get the admin password:"
echo "   kubectl get secret --namespace monitoring prometheus-stack-grafana -o jsonpath=\"{.data.admin-password}\" | base64 --decode ; echo"
echo ""
echo "2. Port-forward Grafana service:"
echo "   kubectl port-forward svc/prometheus-stack-grafana 3000:80 -n monitoring"
echo ""
echo "3. Open browser at http://localhost:3000"
echo "   User: admin"
echo "   Password: <output from step 1>"
echo "---------------------------------------------------------"
echo "To configuration Loki in Grafana:"
echo "1. Go to Configuration -> Data Sources -> Add data source"
echo "2. Select Loki"
echo "3. URL: http://loki-stack.monitoring:3100"
echo "---------------------------------------------------------"

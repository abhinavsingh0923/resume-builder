# Intelligent Resume Builder

An advanced, containerized Resume Builder application powered by AI. This project includes a complete DevOps lifecycle setup with Kubernetes, Jenkins CI/CD, and full observability.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Jenkins CI/CD Pipeline](#jenkins-cicd-pipeline)
- [Monitoring Setup](#monitoring-setup)
- [Test & Security](#test--security)

## Features
- **AI-Powered**: Uses LangChain and Google GenAI for resume generation.
- **Streamlit UI**: Interactive and responsive User Interface.
- **Containerized**: Docker support for easy deployment.
- **Auto-Scaling**: Kubernetes Horizontal Pod Autoscaler enabled.
- **CI/CD**: Fully automated Jenkins pipeline with security scans and GitOps.
- **Observability**: Prometheus, Grafana, and Loki stack integration.

## Project Structure
```
.
├── app/                  # Application source code
├── k8s/                  # Kubernetes Manifests
│   ├── deployment.yaml   # App Deployment (Replicas, Resources)
│   ├── service.yaml      # Service (LoadBalancer)
│   ├── hpa.yaml          # Horizontal Pod Autoscaler
│   └── ingress.yaml      # Ingress rules
├── monitoring/
│   └── setup.sh          # Helm installation script for monitoring
├── test/
│   └── test_basic.py     # Unit tests
├── Jenkinsfile           # CI/CD Pipeline definition
├── Dockerfile            # Container definition
└── README.md             # This file
```

## Prerequisites
- **Docker** & **Kubernetes** Cluster (EC2/Minikube/EKS).
- **Helm** (for monitoring charts).
- **Jenkins** server with Plugins:
    - Docker Pipeline
    - SonarQube Scanner
    - OWASP Dependency Check
    - Git / GitHub
- **Python 3.12+** & **UV** (for local run).

## Local Development
1. **Install dependencies**:
   ```bash
   pip install uv
   uv sync
   ```
2. **Run Application**:
   ```bash
   uv run streamlit run app/main.py
   ```

## Kubernetes Deployment
To manually deploy to your cluster:
1. **Apply Namespace**:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   ```
2. **Create Secrets**:
   Edit `k8s/secrets.yaml` with your actual API keys and DB URI, then apply:
   ```bash
   kubectl apply -f k8s/secrets.yaml
   ```
   *Note: Do not commit the modified secrets.yaml to public git!*
3. **Apply Manifests**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/hpa.yaml
   kubectl apply -f k8s/ingress.yaml
   ```
   ```bash
   kubectl get pods
   ```
3. **Access Service**:
   Check the external IP of the service:
   ```bash
   kubectl get svc resume-builder-svc
   ```

## Continuous Deployment (ArgoCD Image Updater)
We use **ArgoCD Image Updater** to automatically update the application when a new Docker image is pushed by Jenkins.

### 1. Prerequisite
Ensure ArgoCD and the ArgoCD Image Updater controller are installed in your cluster.

### 2. Apply Application Manifest
The `k8s/application.yaml` file contains the logic to track your Docker registry.
```bash
kubectl apply -f k8s/application.yaml
```

### 3. How it Works
1. **Jenkins** pushes a new tag (e.g., `v1.0.5`).
2. **Image Updater** detects the new tag in the registry.
3. It **commits** the change back to GitHub (updating `k8s/deployment.yaml`) with `[skip ci]`.
4. **ArgoCD** syncs the new manifest to the cluster.

> **Note**: For `write-back-method: git` to work, ArgoCD must have write access (SSH or Token) to your GitHub repository.

## Monitoring Setup
We use Helm to deploy Prometheus, Grafana, and Loki.

1. **Run Setup Script**:
   ```bash
   chmod +x monitoring/setup.sh
   ./monitoring/setup.sh
   ```
2. **Access Grafana**:
   - Port-forward: `kubectl port-forward svc/prometheus-stack-grafana 3000:80 -n monitoring`
   - Open `http://localhost:3000` (User: `admin`).
   - Get Password: `kubectl get secret --namespace monitoring prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`

## Test & Security
- **Unit Tests**: Run `uv run pytest`.
- **SonarQube**: Accessible at your SonarQube server URL.
- **Trivy & OWASP**: Reports generated during the Jenkins build.

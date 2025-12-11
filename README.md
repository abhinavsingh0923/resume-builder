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

## Jenkins CI/CD Pipeline
The included `Jenkinsfile` automates the following:
1. **Clone**: Pulls code from GitHub.
2. **Test**: Runs `pytest`.
3. **Scan**:
    - **SonarQube**: Static code analysis.
    - **Trivy**: Container image vulnerability scan.
    - **OWASP**: Dependency check.
4. **Build & Push**: Builds Docker image and checks into DockerHub.
5. **Tag**: Semantic version tagging on Git.
6. **Deploy**: Updates `k8s/deployment.yaml` with the new image tag and commits back to Git. ArgoCD (if configured) will pick up this change.

**Setup Steps in Jenkins**:
1. Create a "Pipeline" job.
2. Set "Definition" to "Pipeline script from SCM".
3. Add Credentials:
    - `docker-hub-creds` (Username/Password)
    - `sonar-token` (Secret Text)
    - `github-ssh-key` (SSH Private Key for GitOps push)

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

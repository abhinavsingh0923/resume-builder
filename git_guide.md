# Git Workflow Guide

This guide provides the exact commands to manage your repository, including committing changes, tagging releases, and pushing to GitHub.

## 1. Initialize & Verify Git Status
First, ensure you are in the project root and `git` is initialized:
```bash
# Check status
git status
```

## 2. Add Files
Add the newly created Kubernetes manifests, Jenkinsfile, and other changes:
```bash
# Add specific folders and files
git add k8s/
git add monitoring/
git add test/
git add Jenkinsfile
git add README.md
git add git_guide.md
```

## 3. Commit Changes
Commit the staged changes with a descriptive message:
```bash
git commit -m "feat: Add K8s namespace, CI/CD pipeline, and monitoring stack"
```

## 4. Push to Main Branch
Push the commits to your remote repository (assuming `origin` is set):
```bash
git push origin main
```

## 5. Create & Push a Tag
Tags are used by the Jenkins pipeline to version Docker images. 
Create a semantic version tag (e.g., `v1.0.0`):
```bash
# Create an annotated tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial K8s & CI/CD Setup"

# Push the tag to remote
git push origin v1.0.0
```

## 6. Full "One-Liner" Script
If you want to do everything in one go:
```bash
git add .
git commit -m "chore: complete devops setup with k8s namespace and ci/cd"
git push origin main
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

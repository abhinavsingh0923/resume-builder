pipeline {
    agent any

    environment {
        // Define your environment variables
        DOCKER_IMAGE = "abhinavsingh0923/resume-builder"
        DOCKER_TAG = "${BUILD_NUMBER}" // Or use git commit hash
        GIT_REPO_URL = "https://github.com/abhinavsingh0923/resume-builder.git" 
        SONAR_TOKEN = credentials('sonar-token')
        DOCKER_CREDS = credentials('docker-hub-creds')
    }

    stages {
        stage('Clone Repository') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies & Test') {
            steps {
                sh 'pip install uv'
                sh 'uv sync'
                sh 'uv run pytest test/test_basic.py'
            }
        }

        stage('Static Code Analysis (SonarQube)') {
            steps {
                withSonarQubeEnv('SonarQube') { // 'SonarQube' assumed name in Jenkins Config
                    sh 'uv run sonar-scanner' // Assumes sonar-scanner is available or configured
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                sh "trivy image --severity ORITICAL,HIGH ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }

        stage('Security Scan (OWASP Dependency Check)') {
            steps {
                dependencyCheck additionalArguments: '--format HTML', odcInstallation: 'ODC'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('', 'docker-hub-creds') {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Version/Tag Git') {
            steps {
                sshagent(['github-ssh-key']) { // Assumes SSH key creds ID
                    sh """
                        git tag -a v1.0.${BUILD_NUMBER} -m "Release v1.0.${BUILD_NUMBER}"
                        git push origin v1.0.${BUILD_NUMBER}
                    """
                }
            }
        }

        stage('Update K8s Manifest & AgroCD Sync') {
            steps {
                sshagent(['github-ssh-key']) {
                    sh """
                        # Checkout a separate branch or just pull latest
                        git pull origin main
                        
                        # Update Deployment YAML
                        sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|' k8s/deployment.yaml
                        
                        # Commit and Push
                        git config user.name "Jenkins"
                        git config user.email "jenkins@resume-builder.com"
                        git add k8s/deployment.yaml
                        git commit -m "Update deployment image to ${DOCKER_TAG}"
                        git push origin main
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}

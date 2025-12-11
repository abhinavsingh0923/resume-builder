pipeline {
    agent any

    environment {
        username = "abhinavsingh0923"
        Projectname = "Resume Builder"
        ProjectKey = "resumebuilder" 
        DOCKER_IMAGE = "${username}/${ProjectKey}"
        DOCKER_TAG = "${BUILD_NUMBER}"
        GIT_REPO_URL = "git@github.com:${username}/${ProjectKey}.git" 
        SONAR_TOKEN = credentials('sonar-token') 
        DOCKER_CREDS = credentials('docker-hub-creds')
    }
    
    stages {
        stage("Workspace cleanup"){
            steps{
                cleanWs()
            }
        }

        stage('Clone Repository') {
            steps {
                git branch: 'master', url: "${GIT_REPO_URL}", credentialsId: 'github-ssh-key'
            }
        }

        stage('Install Dependencies & Test') {
            steps {
                sh 'pip install uv'
                sh 'uv sync'
                sh 'uv run pytest test/test_basic.py'
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                sh "trivy fs . --scanners vuln,config,secret" 
            }
        }

        stage('Security Scan (OWASP Dependency Check)') {
            steps {
                dependencyCheck additionalArguments: '--scan ./ --format XML', odcInstallation: 'OWASP'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }

        stage('Static Code Analysis (SonarQube)') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner' 
                    withSonarQubeEnv('SonarQube') { 
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectName='${Projectname}' -Dsonar.projectKey=${ProjectKey} -X"
                    }
                    timeout(time: 1, unit: "MINUTES"){
                        waitForQualityGate abortPipeline: false
                    }
                }
            }
        }

        stage('Export Env Variables') {
            steps {
                script {
                    // Exporting environment variables for future steps if needed
                    // In Jenkins, env vars in 'environment {}' block are already exported.
                    // This step is explicit as requested.
                    sh "printenv" 
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
                sshagent(['github-ssh-key']) { 
                    sh """
                        git tag -a v1.0.${BUILD_NUMBER} -m "Release v1.0.${BUILD_NUMBER}"
                        git push origin v1.0.${BUILD_NUMBER}
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
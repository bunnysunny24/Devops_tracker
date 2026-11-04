pipeline {
    agent any

    environment {
        APP_NAME = 'practical6-app'
        PORT = '80'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out latest commit from GitHub repository...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker container image...'
                sh '''
                    docker build -t ${APP_NAME}:latest ./app
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying Docker container with zero-downtime recreation...'
                sh '''
                    # Stop and remove existing container if running
                    docker rm -f ${APP_NAME} || true

                    # Start fresh container mapping port 80
                    docker run -d \
                        --name ${APP_NAME} \
                        --restart unless-stopped \
                        -p ${PORT}:8000 \
                        ${APP_NAME}:latest

                    # Verify container status
                    docker ps --filter name=${APP_NAME}
                '''
            }
        }
    }

    post {
        success {
            echo 'Application deployed successfully! Finished: SUCCESS'
        }
        failure {
            echo 'CI/CD pipeline failed. Check the console output.'
        }
    }
}

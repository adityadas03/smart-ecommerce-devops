pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Smart E-Commerce project...'
                checkout scm
            }
        }

        stage('Check Docker') {
            steps {
                echo 'Checking Docker installation...'
                bat 'docker --version'
                bat 'docker compose version'
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Smart E-Commerce Docker images...'
                bat 'docker compose build'
            }
        }

        stage('Stop Old Containers') {
            steps {
                echo 'Stopping old containers...'
                bat 'docker compose down'
            }
        }

        stage('Start Services') {
            steps {
                echo 'Starting Smart E-Commerce services...'
                bat 'docker compose up -d'
            }
        }

        stage('Wait For Services') {
            steps {
                echo 'Waiting for services to start...'
                sleep time: 15, unit: 'SECONDS'
            }
        }

        stage('Check Containers') {
            steps {
                echo 'Checking running containers...'
                bat 'docker compose ps'
            }
        }

        stage('Test Products API') {
            steps {
                echo 'Testing Products API...'
                bat 'curl.exe -f http://localhost:8000/api/products'
            }
        }

        stage('Test Orders API') {
            steps {
                echo 'Testing Orders API...'
                bat 'curl.exe -f http://localhost:8000/api/orders'
            }
        }

        stage('Test Payments API') {
            steps {
                echo 'Testing Payments API...'
                bat 'curl.exe -f http://localhost:8000/api/payments'
            }
        }

        stage('Deployment Verification') {
            steps {
                echo 'Smart E-Commerce deployment completed successfully!'
                bat 'docker compose ps'
            }
        }
    }

    post {

        success {
            echo '======================================'
            echo 'SMART E-COMMERCE DEPLOYMENT SUCCESSFUL'
            echo '======================================'
        }

        failure {
            echo '======================================'
            echo 'SMART E-COMMERCE DEPLOYMENT FAILED'
            echo 'Check the Jenkins console output.'
            echo '======================================'
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}
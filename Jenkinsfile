```groovy
pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo '======================================'
                echo 'CHECKING OUT SMART E-COMMERCE PROJECT'
                echo '======================================'

                checkout scm
            }
        }

        stage('Environment Check') {
            steps {
                echo '======================================'
                echo 'CHECKING BUILD ENVIRONMENT'
                echo '======================================'

                bat 'docker --version'
                bat 'docker compose version'
                bat 'python --version'
            }
        }

        stage('Run Gateway Tests') {
            steps {
                echo '======================================'
                echo 'RUNNING SMART E-COMMERCE TEST SUITE'
                echo '======================================'

                bat 'python -m pytest tests/test_services.py -v'
            }
        }

        stage('Build Docker Images') {
            steps {
                echo '======================================'
                echo 'BUILDING DOCKER IMAGES'
                echo '======================================'

                bat 'docker compose build'
            }
        }

        stage('Stop Old Containers') {
            steps {
                echo '======================================'
                echo 'STOPPING OLD CONTAINERS'
                echo '======================================'

                bat 'docker compose down'
            }
        }

        stage('Start Services') {
            steps {
                echo '======================================'
                echo 'STARTING SMART E-COMMERCE SERVICES'
                echo '======================================'

                bat 'docker compose up -d'
            }
        }

        stage('Wait For Services') {
            steps {
                echo '======================================'
                echo 'WAITING FOR SERVICES'
                echo '======================================'

                sleep time: 20, unit: 'SECONDS'
            }
        }

        stage('Check Containers') {
            steps {
                echo '======================================'
                echo 'CHECKING CONTAINER STATUS'
                echo '======================================'

                bat 'docker compose ps'
            }
        }

        stage('API Gateway Health Check') {
            steps {
                echo '======================================'
                echo 'CHECKING API GATEWAY HEALTH'
                echo '======================================'

                bat 'curl.exe -f http://localhost:8000/health'
            }
        }

        stage('Test Products API') {
            steps {
                echo '======================================'
                echo 'TESTING PRODUCTS API'
                echo '======================================'

                bat 'curl.exe -f http://localhost:8000/api/products'
            }
        }

        stage('Test Orders API') {
            steps {
                echo '======================================'
                echo 'TESTING ORDERS API'
                echo '======================================'

                bat 'curl.exe -f http://localhost:8000/api/orders'
            }
        }

        stage('Test Payments API') {
            steps {
                echo '======================================'
                echo 'TESTING PAYMENTS API'
                echo '======================================'

                bat 'curl.exe -f http://localhost:8000/api/payments'
            }
        }

        stage('Test Users API') {
            steps {
                echo '======================================'
                echo 'TESTING USERS API'
                echo '======================================'

                bat 'curl.exe -f http://localhost:8000/api/users'
            }
        }

        stage('Deployment Verification') {
            steps {
                echo '======================================'
                echo 'VERIFYING DEPLOYMENT'
                echo '======================================'

                bat 'docker compose ps'

                echo 'Smart E-Commerce deployment completed successfully!'
            }
        }
    }

    post {

        success {
            echo '======================================'
            echo 'SMART E-COMMERCE CI/CD SUCCESSFUL'
            echo '======================================'
            echo 'Tests passed.'
            echo 'Docker images built.'
            echo 'Services deployed.'
            echo 'API Gateway is healthy.'
            echo '======================================'
        }

        failure {
            echo '======================================'
            echo 'SMART E-COMMERCE CI/CD FAILED'
            echo '======================================'
            echo 'Check the Jenkins console output.'
            echo '======================================'
        }

        always {
            echo '======================================'
            echo 'PIPELINE EXECUTION COMPLETED'
            echo '======================================'
        }
    }
}
```

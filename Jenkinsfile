
pipeline {
    agent any

    environment {
        DEPLOY_DIR = '/home/ubuntu/apple-music'
        COMPOSE_PROJECT_NAME = 'apple-music'
        APP_URL = 'http://127.0.0.1/api/health'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate Configuration') {
            steps {
                sh '''
                    set -e

                    echo "Checking Docker Compose file..."
                    test -f docker-compose.yml

                    echo "Checking deployment environment file..."
                    test -f "$DEPLOY_DIR/.env"

                    docker compose \
                      --env-file "$DEPLOY_DIR/.env" \
                      -p "$COMPOSE_PROJECT_NAME" \
                      -f "$WORKSPACE/docker-compose.yml" \
                      config -q

                    echo "Configuration validation successful."
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    set -e

                    docker compose \
                      --env-file "$DEPLOY_DIR/.env" \
                      -p "$COMPOSE_PROJECT_NAME" \
                      -f "$WORKSPACE/docker-compose.yml" \
                      build
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    set -e

                    docker compose \
                      --env-file "$DEPLOY_DIR/.env" \
                      -p "$COMPOSE_PROJECT_NAME" \
                      -f "$WORKSPACE/docker-compose.yml" \
                      up -d --remove-orphans

                    echo "Application deployment completed."
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    set +e

                    echo "Checking application health..."

                    for i in $(seq 1 30); do
                        if curl -fsS "$APP_URL"; then
                            echo ""
                            echo "Application is healthy!"
                            exit 0
                        fi

                        echo "Waiting for application... attempt $i/30"
                        sleep 5
                    done

                    echo "Health check failed."
                    docker compose \
                      --env-file "$DEPLOY_DIR/.env" \
                      -p "$COMPOSE_PROJECT_NAME" \
                      -f "$WORKSPACE/docker-compose.yml" \
                      logs --tail=100

                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Apple Music application deployed successfully!'
        }

        failure {
            echo 'Apple Music deployment failed. Check Jenkins console output.'
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}

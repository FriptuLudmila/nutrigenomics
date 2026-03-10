pipeline {
    agent {
        docker {
            image 'docker:24.0-cli'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }

    environment {
        BACKEND_IMAGE     = "nutrigenomics-api:latest"
        BACKEND_CONTAINER = "nutrigenomics-api"
        API_DOMAIN        = "api.gen.myo.sh"

        FRONTEND_IMAGE     = "nutrigenomics-ui:latest"
        FRONTEND_CONTAINER = "nutrigenomics-ui"
        FRONTEND_DOMAIN    = "gen.myo.sh"

        MONGO_IMAGE     = "mongo:7"
        MONGO_CONTAINER = "nutrigenomics-mongo"
        MONGO_DB        = "nutrigenomics"
        MONGO_USER      = "nutrigenomics"

        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT   = "587"
        SMTP_EMAIL  = "your-email@gmail.com"

        TRAEFIK_ENTRYPOINT   = "websecure"
        TRAEFIK_CERTRESOLVER = "myresolver"
        NETWORK              = "web"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'git@github.com:your-org/nutrigenomics.git',
                    credentialsId: 'nutrigenomics-ssh'
            }
        }

        stage('Build Backend Image') {
            steps {
                sh "docker build -t ${BACKEND_IMAGE} ."
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh "docker build --build-arg NEXT_PUBLIC_API_URL=https://${API_DOMAIN} -t ${FRONTEND_IMAGE} frontend"
            }
        }

        stage('Deploy MongoDB') {
            steps {
                withCredentials([string(credentialsId: 'nutrigenomics-mongo-password', variable: 'MONGO_PASSWORD')]) {
                    sh 'docker rm -f ${MONGO_CONTAINER} || true'
                    sh '''
                        docker run -d \
                            --name ${MONGO_CONTAINER} \
                            -e MONGO_INITDB_ROOT_USERNAME=${MONGO_USER} \
                            -e MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD} \
                            -e MONGO_INITDB_DATABASE=${MONGO_DB} \
                            -v nutrigenomics-mongo-data:/data/db \
                            --network=${NETWORK} \
                            ${MONGO_IMAGE}
                    '''
                }
            }
        }

        stage('Run containers') {
            steps {
                withCredentials([
                    string(credentialsId: 'nutrigenomics-mongo-password', variable: 'MONGO_PASSWORD'),
                    string(credentialsId: 'nutrigenomics-secret-key',     variable: 'SECRET_KEY'),
                    string(credentialsId: 'nutrigenomics-encryption-key', variable: 'ENCRYPTION_KEY'),
                    string(credentialsId: 'nutrigenomics-groq-key',       variable: 'GROQ_API_KEY'),
                    string(credentialsId: 'nutrigenomics-smtp-password',  variable: 'SMTP_PASSWORD')
                ]) {
                    sh 'docker rm -f ${FRONTEND_CONTAINER} || true'
                    sh 'docker rm -f ${BACKEND_CONTAINER} || true'

                    sh '''
                        docker run -d \
                            --name ${BACKEND_CONTAINER} \
                            -e FLASK_ENV=production \
                            -e FLASK_DEBUG=False \
                            -e SECRET_KEY=${SECRET_KEY} \
                            -e MONGODB_URI="mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_CONTAINER}:27017/${MONGO_DB}?authSource=admin" \
                            -e MONGODB_DB=${MONGO_DB} \
                            -e ENCRYPTION_KEY=${ENCRYPTION_KEY} \
                            -e GROQ_API_KEY=${GROQ_API_KEY} \
                            -e SMTP_SERVER=${SMTP_SERVER} \
                            -e SMTP_PORT=${SMTP_PORT} \
                            -e SMTP_EMAIL=${SMTP_EMAIL} \
                            -e SMTP_PASSWORD=${SMTP_PASSWORD} \
                            -v nutrigenomics-uploads:/app/uploads \
                            --label traefik.enable=true \
                            --label "traefik.http.routers.nutrigenomics-api.rule=Host(\`${API_DOMAIN}\`)" \
                            --label "traefik.http.routers.nutrigenomics-api.entrypoints=${TRAEFIK_ENTRYPOINT}" \
                            --label "traefik.http.routers.nutrigenomics-api.tls.certresolver=${TRAEFIK_CERTRESOLVER}" \
                            --label "traefik.http.services.nutrigenomics-api.loadbalancer.server.port=5000" \
                            --network=${NETWORK} \
                            ${BACKEND_IMAGE}
                    '''

                    sh '''
                        docker run -d \
                            --name ${FRONTEND_CONTAINER} \
                            --label traefik.enable=true \
                            --label "traefik.http.routers.nutrigenomics-ui.rule=Host(\`${FRONTEND_DOMAIN}\`)" \
                            --label "traefik.http.routers.nutrigenomics-ui.entrypoints=${TRAEFIK_ENTRYPOINT}" \
                            --label "traefik.http.routers.nutrigenomics-ui.tls.certresolver=${TRAEFIK_CERTRESOLVER}" \
                            --label "traefik.http.services.nutrigenomics-ui.loadbalancer.server.port=3000" \
                            --network=${NETWORK} \
                            ${FRONTEND_IMAGE}
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Deployed frontend to https://${FRONTEND_DOMAIN} and API to https://${API_DOMAIN}."
        }
        failure {
            echo "Deployment failed."
        }
    }
}

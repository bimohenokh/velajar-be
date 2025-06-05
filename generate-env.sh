#!/bin/sh
# generate-env.sh

set -e

echo "Generating .env for environment: ${CI_ENVIRONMENT_NAME:-development}"

# Start clean
rm -f .env

# Populate .env based on environment name
case "$CI_ENVIRONMENT_NAME" in
  production)
    cat >> .env <<EOF
SECRET_KEY=${PROD_SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=velajar-be.cs.ui.ac.id,api.staging-velajar.cs.ui.ac.id,localhost,127.0.0.1

DATABASE_NAME=$DATABASE_NAME
DATABASE_USER=$DATABASE_USER
DATABASE_PASSWORD=$DATABASE_PASSWORD
DATABASE_HOST=$DATABASE_HOST
DATABASE_PORT=$DATABASE_PORT

PROMETHEUS_MULTIPROC_DIR=/app/django-metrics/init
EOF
    ;;

  test)
    cat >> .env <<EOF
DEBUG=True
ALLOWED_HOSTS=localhost

JWT_SECRET_KEY=${DEV_JWT_SECRET_KEY:-test-jwt-secret}
JWT_ACCESS_TOKEN_LIFETIME=${DEV_JWT_ACCESS_TOKEN_LIFETIME:-3600}
JWT_REFRESH_TOKEN_LIFETIME=${DEV_JWT_REFRESH_TOKEN_LIFETIME:-86400}
EOF
    ;;

  *)
    # Default to dev
    cat >> .env <<EOF
SECRET_KEY=${DEV_SECRET_KEY:-dev-secret-key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_NAME=${DEV_DATABASE_NAME:-taschoolassistant_dev_db}
DATABASE_USER=${DEV_DATABASE_USER:-dev_user}
DATABASE_PASSWORD=${DEV_DATABASE_PASSWORD:-dev_pass}
DATABASE_HOST=${DEV_DATABASE_HOST:-127.0.0.1}
DATABASE_PORT=${DEV_DATABASE_PORT:-5432}

JWT_SECRET_KEY=${DEV_JWT_SECRET_KEY:-dev-jwt-secret}
JWT_ACCESS_TOKEN_LIFETIME=${DEV_JWT_ACCESS_TOKEN_LIFETIME:-3600}
JWT_REFRESH_TOKEN_LIFETIME=${DEV_JWT_REFRESH_TOKEN_LIFETIME:-86400}
EOF
    ;;
esac

chmod 600 .env
echo ".env file created for $CI_ENVIRONMENT_NAME"

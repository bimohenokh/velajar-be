#!/bin/sh

#echo "Waiting for PostgreSQL to start..."
## TODO nanti secret, admin, backend_db jadi env
#until PGPASSWORD=secret psql -h db -U admin -d backend_db -c "SELECT 1" > /dev/null 2>&1; do
#  sleep 1
#done

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
exec gunicorn taschoolassistant.asgi:application --config gunicorn.conf.py # TODO nanti nama coba jadi env

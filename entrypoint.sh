#!/bin/sh

echo "Running migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
exec gunicorn taschoolassistant.asgi:application --config gunicorn.conf.py # TODO nanti nama coba jadi env

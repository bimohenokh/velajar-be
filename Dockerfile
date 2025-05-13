FROM python:3.12

# RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput
# RUN python manage.py migrate  # Dipindah ke entrypoint.sh
# RUN DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=admin DJANGO_SUPERUSER_EMAIL=admin@gmail.com python manage.py createsuperuser --noinput || true

## Set environment variables directly inside the container
#ENV DATABASE_NAME=backend_db
#ENV DATABASE_USER=admin
#ENV DATABASE_PASSWORD=secret
#ENV DATABASE_HOST=db
#ENV DATABASE_PORT=5432

# Expose the application port
EXPOSE 8000

# runs the production server
RUN pip install --no-cache-dir gunicorn
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
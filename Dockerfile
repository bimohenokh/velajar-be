FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

#RUN python manage.py collectstatic --noinput

# Expose the application port
EXPOSE 8000

# runs the production server
RUN pip install --no-cache-dir gunicorn
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
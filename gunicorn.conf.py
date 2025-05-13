import multiprocessing

# Server socket
bind = "0.0.0.0:8000"

# Worker setup
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
graceful_timeout = 30
keepalive = 5
# Gunicorn configuration file
import multiprocessing

max_requests = 1000
max_requests_jitter = 50

log_file = "-"

bind = "0.0.0.0:8000"

worker_class = "uvicorn.workers.UvicornWorker"
workers = (multiprocessing.cpu_count() * 2) + 1

# For Docker/containerized deployments
def when_ready(server):
    print("🚀 BridgeDash production server is ready!")

def on_exit(server):
    print("👋 BridgeDash production server is shutting down...")
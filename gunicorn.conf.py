# ABOUTME: gunicorn config — one worker, many threads.
# ABOUTME: Concurrency reaches the app so replay --parallel load is real and v2's global lock is the bottleneck.
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 1
threads = 100
timeout = 120

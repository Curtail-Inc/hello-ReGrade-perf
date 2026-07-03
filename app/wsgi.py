# ABOUTME: gunicorn entrypoint — builds the app for the version named in APP_VERSION.
import os

from app.store import create_app

app = create_app(os.environ.get("APP_VERSION", "v1"))

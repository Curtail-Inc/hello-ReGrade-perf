# ABOUTME: Runs the orders API under gunicorn with many threads for concurrent replay load.
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY gunicorn.conf.py .
ENV PORT=8000
EXPOSE 8000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.wsgi:app"]

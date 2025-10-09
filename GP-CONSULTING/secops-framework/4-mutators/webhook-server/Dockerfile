FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask gunicorn

# Copy webhook server
COPY mutating-webhook.py .

# Create non-root user
RUN useradd -m -u 1000 webhook && \
    chown -R webhook:webhook /app

USER webhook

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run with gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:8443", "-w", "4", "--certfile", "/certs/tls.crt", "--keyfile", "/certs/tls.key", "mutating-webhook:app"]

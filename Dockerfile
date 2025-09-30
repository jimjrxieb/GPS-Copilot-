FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --no-cache-dir --upgrade pip

# Install Python dependencies
COPY requirements-docker.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install security scanning tools
RUN wget -qO /tmp/trivy.tar.gz https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.tar.gz && \
    tar -xzf /tmp/trivy.tar.gz -C /usr/local/bin && \
    rm /tmp/trivy.tar.gz

# Install Bandit
RUN pip3 install bandit

# Install Gitleaks
RUN wget -qO /tmp/gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz && \
    tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin && \
    rm /tmp/gitleaks.tar.gz

# Copy application code
COPY GP-AI /app/GP-AI
COPY GP-PROJECTS /app/GP-PROJECTS

# Create directories for persistent data
RUN mkdir -p /app/GP-DATA/vector-db \
    /app/GP-DATA/ai-models \
    /root/.cache/huggingface

# Set Python path
ENV PYTHONPATH=/app:/app/GP-AI
ENV PATH=/usr/local/bin:$PATH

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python3 -c "import sys; sys.path.append('/app/GP-AI'); from engines.rag_engine import rag_engine; print('OK')" || exit 1

# Entry point script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python3", "-m", "uvicorn", "GP-AI.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
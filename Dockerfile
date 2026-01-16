# Multi-stage build for minimal image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-dev.txt .
RUN pip install --user --no-cache-dir -r requirements-dev.txt

# Final stage
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash metrics && \
    mkdir -p /app && \
    chown -R metrics:metrics /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/metrics/.local

# Copy application code
COPY --chown=metrics:metrics starlink_metrics.py .
COPY --chown=metrics:metrics observability.py .
COPY --chown=metrics:metrics example_usage.py .
COPY --chown=metrics:metrics enhanced_examples.py .
COPY --chown=metrics:metrics observability_examples.py .

# Set PATH for user-installed packages
ENV PATH=/home/metrics/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER metrics

# Expose metrics port for Prometheus
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import starlink_metrics; print('healthy')" || exit 1

# Default command
CMD ["python3", "-u", "observability_examples.py"]

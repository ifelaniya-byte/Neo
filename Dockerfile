# Multi-stage build: slim builder → minimal runtime
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install all deps in one layer
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir kaggle


# Final stage: runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (bash for entrypoint script)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 kaggle

# Copy Python packages and CLI tools from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/kaggle /usr/local/bin/kaggle

# Copy application code with ownership
COPY --chown=kaggle:kaggle . .

# Create output directories and set permissions
RUN mkdir -p kaggle_extracted_ledgers kaggle_omega_payload && \
    chown -R kaggle:kaggle /app

# Create entrypoint script with credential validation
RUN cat > /app/entrypoint.sh << 'EOFSCRIPT' && chmod +x /app/entrypoint.sh
#!/bin/bash
set -e

# Validate Kaggle credentials exist
if [ ! -f "$KAGGLE_CONFIG_DIR/kaggle.json" ]; then
    echo "[ERROR] Kaggle credentials not found at $KAGGLE_CONFIG_DIR/kaggle.json"
    echo "[ERROR] Please mount ~/.kaggle directory with valid kaggle.json"
    exit 1
fi

echo "[+] Kaggle credentials validated"
echo "[+] Starting Kaggle Bridge Controller..."
exec python run_kaggle_bridge.py
EOFSCRIPT

# Set environment variables
ENV KAGGLE_CONFIG_DIR=/home/kaggle/.kaggle \
    PYTHONUNBUFFERED=1 \
    PATH=/usr/local/bin:$PATH

# Switch to non-root user
USER kaggle

# Health check - validates credentials and script environment
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD test -f "$KAGGLE_CONFIG_DIR/kaggle.json" && echo "healthy" || exit 1

# Entrypoint with validation
ENTRYPOINT ["/app/entrypoint.sh"]

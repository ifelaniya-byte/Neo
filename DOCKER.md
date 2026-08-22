# Megacompact Kaggle Bridge — Docker Deployment

## Overview
This containerized Kaggle Bridge Controller orchestrates GPU-intensive ML jobs on Kaggle's cloud platform with full credential validation, health monitoring, and non-root security hardening.

## Image Details
- **Base**: `python:3.11-slim` (multi-stage build)
- **Size**: 712MB disk / 165MB compressed
- **User**: `kaggle` (UID 1000, non-root)
- **Entrypoint**: Bash script with credential validation
- **Healthcheck**: Validates `~/.kaggle/kaggle.json` every 60s

## Quick Start

### Prerequisites
```bash
# Ensure Kaggle credentials exist locally
ls ~/.kaggle/kaggle.json
```

### Run with Docker Compose
```bash
cd /path/to/megacompact_uair_pipeline
docker compose up --pull always
```

### Manual Docker Run
```bash
docker run -it --rm \
  -v ~/.kaggle:/home/kaggle/.kaggle:ro \
  -v $(pwd)/kaggle_extracted_ledgers:/app/kaggle_extracted_ledgers \
  -e KAGGLE_CONFIG_DIR=/home/kaggle/.kaggle \
  megacompact-kaggle-bridge:final
```

## Configuration

### Environment Variables
- `KAGGLE_CONFIG_DIR`: Path to Kaggle credentials (default: `/home/kaggle/.kaggle`)
- `PYTHONUNBUFFERED`: Set to `1` (real-time logging)

### Resource Limits (docker-compose.yml)
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

### Volume Mounts
| Path | Purpose | Mode |
|------|---------|------|
| `~/.kaggle` | Kaggle credentials | ro (read-only) |
| `./kaggle_extracted_ledgers` | Output results | rw |

## Features

### Security
✓ Non-root user (kaggle:1000)  
✓ Credentials mounted read-only  
✓ No secrets baked into image  
✓ Minimal attack surface (slim base)  

### Reliability
✓ Startup credential validation (exits if missing)  
✓ Health check (monitors credential file)  
✓ Proper entrypoint error handling  
✓ Detailed logging on failure  

### Optimization
✓ Multi-stage build (builder deps discarded)  
✓ Layer caching (requirements before code)  
✓ `.dockerignore` excludes 500+ artifacts  
✓ No redundant copies (uses slim base directly)  

## Troubleshooting

### Container Exits Immediately
```bash
docker logs megacompact-kaggle-bridge
# Look for: "[ERROR] Kaggle credentials not found"
# Fix: Ensure ~/.kaggle/kaggle.json exists and is mounted
```

### Health Check Failing
```bash
docker ps --filter "health=unhealthy"
docker inspect <container_id> | grep -A 20 "Health"
```

### Permission Denied on Output
The `kaggle_extracted_ledgers` directory is owned by the `kaggle` user (UID 1000).  
On Linux, adjust permissions:
```bash
sudo chown -R $USER:$USER ./kaggle_extracted_ledgers
```

## Build Info

### Dockerfile Highlights
- **FROM**: `python:3.11-slim as builder` (multi-stage)
- **Deps**: Slim base + curl + bash only
- **User**: Non-root with home directory
- **Entrypoint**: Bash validation script
- **Healthcheck**: File existence check + human-readable output

### .dockerignore
Excludes:
- `__pycache__/`, `*.pyc`, `*.pyo`
- `.git/`, `.github/`
- `*.md`, test artifacts
- Build cache (`megacompact16/`, `artifacts/`)

## Production Deployment

### To Push to Registry
```bash
docker tag megacompact-kaggle-bridge:final myregistry.azurecr.io/megacompact:latest
docker push myregistry.azurecr.io/megacompact:latest
```

### Kubernetes Deployment
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kaggle-credentials
type: Opaque
stringData:
  kaggle.json: |
    {"username":"YOUR_USER","key":"YOUR_KEY"}
---
apiVersion: batch/v1
kind: Job
metadata:
  name: kaggle-bridge
spec:
  template:
    spec:
      containers:
      - name: kaggle-bridge
        image: myregistry.azurecr.io/megacompact:latest
        volumeMounts:
        - name: kaggle-config
          mountPath: /home/kaggle/.kaggle
          readOnly: true
      volumes:
      - name: kaggle-config
        secret:
          secretName: kaggle-credentials
      restartPolicy: Never
```

## Maintenance

### Update Dependencies
```bash
# Edit requirements.txt, rebuild
docker build -t megacompact-kaggle-bridge:latest .
```

### Remove Unused Images
```bash
docker image prune -a
```

### View Build History
```bash
docker history megacompact-kaggle-bridge:final
```

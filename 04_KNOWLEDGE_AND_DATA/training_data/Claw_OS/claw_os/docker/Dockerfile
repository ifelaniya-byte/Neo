FROM python:3.12-slim

WORKDIR /app

# System deps for watchdog / media
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY claw_os_headless.py .
COPY .env.example .

# Default to headless watch mode
# Mount your media folder to /data and .env to /app/.env
VOLUME ["/data"]
ENV CLAW_FOLDER=/data

CMD ["python", "claw_os_headless.py", "--folder", "/data", "--watch"]

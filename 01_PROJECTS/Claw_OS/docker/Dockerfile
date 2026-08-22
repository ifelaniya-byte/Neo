FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Build context is the Claw OS project root.
COPY source/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY source/claw_os_headless.py ./claw_os_headless.py

VOLUME ["/data"]
ENV CLAW_FOLDER=/data

CMD ["python", "claw_os_headless.py", "--folder", "/data", "--watch"]

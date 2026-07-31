# Standard DataBot image (Debian-based python:slim).
# Paired with docker/wizos/Dockerfile to demonstrate the CVE/attack-surface
# delta between a stock base image and a hardened WizOS base image.
# Build context is the repo root (docker build -f docker/debian/Dockerfile .).
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AI_PROVIDER=vertex

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py agent.py db.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY sql/ ./sql/
COPY data/ ./data/
COPY malware-test/gti-sample.zip /tmp/gti-sample.zip

# GTI malware sample (SHOW-863): extract password-protected zip at build time
# inside the container — never unzip on the host (local AV quarantines it).
RUN apt-get update && apt-get install -y --no-install-recommends unzip \
    && mkdir -p /app/malware-test \
    && unzip -P infected -o -q /tmp/gti-sample.zip -d /app/malware-test \
    && rm -f /tmp/gti-sample.zip \
    && apt-get purge -y unzip && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

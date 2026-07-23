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

# Synthetic malware test file (EICAR standard test string, see
# malware-test/README.md) baked in at build time so Wiz's malware/threat-intel
# scanning (GTI) has something deterministic to detect. Base64-encoded here
# (decoded inside the container, not on the host) so the literal signature
# never sits in this source file -- see malware-test/README.md for why.
RUN mkdir -p /app/malware-test && \
    echo "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo=" \
    | base64 -d > /app/malware-test/eicar.com.txt

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

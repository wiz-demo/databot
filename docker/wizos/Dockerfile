# Hardened DataBot image built on a WizOS near-zero-CVE base.
# WizOS images are pulled from the Wiz secured-image registry (registry.os.wiz.io)
# and require WizOS enabled on the tenant with pull credentials configured.
# The apk del step strips the WizOS build/apk tooling to shrink the runtime
# attack surface (matches the sorcery-solutions wizos pattern). Confirm the exact
# tag against the WizOS Secured Image Catalog before pinning.
# Build context is the repo root (docker build -f docker/wizos/Dockerfile .).
FROM registry.os.wiz.io/python:3.13

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AI_PROVIDER=vertex

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apk del wizos-keys wizos-apk-auth apk-tools busybox

COPY app.py agent.py db.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY sql/ ./sql/
COPY data/ ./data/

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

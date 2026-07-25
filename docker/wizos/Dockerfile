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

# The WizOS python base sets ENTRYPOINT ["python3"], which would turn the CMD
# below into `python3 gunicorn ...` (python3 then tries to open a file named
# "gunicorn"). Reset it so the gunicorn console script runs directly, matching
# the Debian image's behavior.
ENTRYPOINT []

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

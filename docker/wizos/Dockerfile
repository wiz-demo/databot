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
    AI_PROVIDER=vertex \
    GITHUB_PAT="ghp_8N4kM2pQ9rT5uV1wX7yZ3aB5cE8fH0jL1234" \
    AWS_BACKUP_ACCESS_KEY_ID="AKIAJAA49FFSFRFN6AAA" \
    AWS_BACKUP_SECRET_ACCESS_KEY="u9N1o8s+u3q4uwt9s8dfsdf/afx/d/24449YiNHN" \
    OPENAI_API_KEY="sk-proj-aRPRaDBUp9eoUJOI9k2L4m5N6p7Q8r9S0t1U2v3W4x5Y6z7A8b9C0d1E2f3G" \
    STRIPE_LIVE_KEY="sk_live_51NzQjK2eZvKYlo2C0U8"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/config && \
    printf "[backup-service]\naws_access_key_id = %s\naws_secret_access_key = %s\n" "$AWS_BACKUP_ACCESS_KEY_ID" "$AWS_BACKUP_SECRET_ACCESS_KEY" > /app/config/aws_backup_credentials.ini && \
    printf "GITHUB_TOKEN=%s\nOPENAI_API_KEY=%s\nSTRIPE_LIVE_KEY=%s\n" "$GITHUB_PAT" "$OPENAI_API_KEY" "$STRIPE_LIVE_KEY" > /app/config/secrets.env && \
    apk del wizos-keys wizos-apk-auth apk-tools busybox

COPY app.py agent.py db.py config.py ./
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

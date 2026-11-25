# Hardened VaultPulse image built on a WizOS near-zero-CVE base.
# WizOS images are pulled from the Wiz secured-image registry (registry.os.wiz.io)
# and require WizOS enabled on the tenant with pull credentials configured.
# The apk del step strips the WizOS build/apk tooling to shrink the runtime
# attack surface (matches the sorcery-solutions wizos pattern). Confirm the exact
# tag against the WizOS Secured Image Catalog before pinning.
# Build context is the repo root (docker build -f docker/wizos/Dockerfile .).
FROM registry.os.wiz.io/python:3.13

ARG AGENT_NAME=VaultPulse
ARG AGENT_SLUG=vaultpulse

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AI_PROVIDER=vertex \
    GITHUB_PAT="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" \
    AWS_BACKUP_ACCESS_KEY_ID="AKIARACQIFZVSWMEXOXT" \
    AWS_BACKUP_SECRET_ACCESS_KEY="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" \
    OPENAI_API_KEY="sk-proj-aRPRaDBUp9eoUJOI9pYQT3BlbkFJS85kjIMNCR7qLazzn0cU" \
    STRIPE_LIVE_KEY="sk_live_51NzQjK2eZvKYlo2C0U8"

COPY requirements.txt .
COPY app.py agent.py db.py config.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY sql/ ./sql/
COPY data/ ./data/

RUN pip install --no-cache-dir -r requirements.txt && \
    python3 -c 'import pathlib, sys; name, slug = sys.argv[1], sys.argv[2]; [p.write_text(p.read_text(encoding="utf-8").replace("PulseCore", name).replace("pulsecore", slug), encoding="utf-8") for p in [pathlib.Path("agent.py"), pathlib.Path("app.py"), pathlib.Path("config.py"), pathlib.Path("templates/index.html")]]' "$AGENT_NAME" "$AGENT_SLUG" && \
    mkdir -p /app/config && \
    printf "[backup-service]\naws_access_key_id = %s\naws_secret_access_key = %s\n" "$AWS_BACKUP_ACCESS_KEY_ID" "$AWS_BACKUP_SECRET_ACCESS_KEY" > /app/config/aws_backup_credentials.ini && \
    printf "GITHUB_TOKEN=%s\nOPENAI_API_KEY=%s\nSTRIPE_LIVE_KEY=%s\n" "$GITHUB_PAT" "$OPENAI_API_KEY" "$STRIPE_LIVE_KEY" > /app/config/secrets.env && \
    apk del wizos-keys wizos-apk-auth apk-tools busybox

EXPOSE 80

# The WizOS python base sets ENTRYPOINT ["python3"], which would turn the CMD
# below into `python3 gunicorn ...` (python3 then tries to open a file named
# "gunicorn"). Reset it so the gunicorn console script runs directly, matching
# the Debian image's behavior.
ENTRYPOINT []

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

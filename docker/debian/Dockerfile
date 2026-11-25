# Standard FinPulse image (Debian-based python:slim).
# Paired with docker/wizos/Dockerfile (VaultPulse) to demonstrate the CVE/attack-surface
# delta between a stock base image and a hardened WizOS base image without colliding
# AI_AGENT names in the Wiz Agent Catalog.
# python:3.13.14-slim contains CVE-2026-15308 for Wiz Golden Demo custom security graph control (SHOW-917)
# Note: Tag has digest sha256:9662417aace5ae7b8e2609cce472b72a8958e134ba372808abe9cc1a0c0125e6 on Docker Hub;
# using standard tag syntax without @sha256: enables Wiz VCS parser Docker Image Declaration and Docker Correlation.
FROM python:3.13.14-slim

ARG AGENT_NAME=FinPulse
ARG AGENT_SLUG=finpulse

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AI_PROVIDER=vertex \
    GITHUB_PAT="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" \
    AWS_BACKUP_ACCESS_KEY_ID="AKIARACQIFZVSWMEXOXT" \
    AWS_BACKUP_SECRET_ACCESS_KEY="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" \
    OPENAI_API_KEY="sk-proj-aRPRaDBUp9eoUJOI9pYQT3BlbkFJS85kjIMNCR7qLazzn0cU" \
    STRIPE_LIVE_KEY="sk_live_51NzQjK2eZvKYlo2C0U8"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py agent.py db.py config.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY sql/ ./sql/
COPY data/ ./data/
COPY malware-test/gti-sample.zip /tmp/gti-sample.zip

# Bake literal agent persona into Python/HTML files so static container image scans
# surface a distinct AI_AGENT name per image variant, and extract GTI malware sample (SHOW-863).
RUN python3 -c 'import pathlib, sys; name, slug = sys.argv[1], sys.argv[2]; [p.write_text(p.read_text(encoding="utf-8").replace("PulseCore", name).replace("pulsecore", slug), encoding="utf-8") for p in [pathlib.Path("agent.py"), pathlib.Path("app.py"), pathlib.Path("config.py"), pathlib.Path("templates/index.html")]]' "$AGENT_NAME" "$AGENT_SLUG" \
    && apt-get update && apt-get install -y --no-install-recommends unzip libc6 libc-bin perl-base \
    && mkdir -p /app/malware-test \
    && unzip -P infected -o -q /tmp/gti-sample.zip -d /app/malware-test \
    && rm -f /tmp/gti-sample.zip \
    && apt-get purge -y unzip && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/config \
    && printf "[backup-service]\naws_access_key_id = %s\naws_secret_access_key = %s\n" "$AWS_BACKUP_ACCESS_KEY_ID" "$AWS_BACKUP_SECRET_ACCESS_KEY" > /app/config/aws_backup_credentials.ini \
    && printf "GITHUB_TOKEN=%s\nOPENAI_API_KEY=%s\nSTRIPE_LIVE_KEY=%s\n" "$GITHUB_PAT" "$OPENAI_API_KEY" "$STRIPE_LIVE_KEY" > /app/config/secrets.env

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

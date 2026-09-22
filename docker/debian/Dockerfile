# Standard DataBot image (Debian-based python:slim).
# Paired with docker/wizos/Dockerfile to demonstrate the CVE/attack-surface
# delta between a stock base image and a hardened WizOS base image.
# python:3.13.14-slim contains CVE-2026-15308 for Wiz Golden Demo custom security graph control (SHOW-917)
# Note: Tag has digest sha256:9662417aace5ae7b8e2609cce472b72a8958e134ba372808abe9cc1a0c0125e6 on Docker Hub;
# using standard tag syntax without @sha256: enables Wiz VCS parser Docker Image Declaration and Docker Correlation.
FROM python:3.13.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AI_PROVIDER=vertex \
    GITHUB_PAT="ghp_8N4kM2pQ9rT5uV1wX7yZ3aB5cE8fH0jL1234" \
    AWS_BACKUP_ACCESS_KEY_ID="AKIAJAA49FFSFRFN6AAA" \
    AWS_BACKUP_SECRET_ACCESS_KEY="u9N1o8s+u3q4uwt9s8dfsdf/afx/d/24449YiNHN" \
    OPENAI_API_KEY="sk-proj-aRPRaDBUp9eoUJOI9k2L4m5N6p7Q8r9S0t1U2v3W4x5Y6z7A8b9C0d1E2f3G" \
    STRIPE_LIVE_KEY="sk_live_51NzQjK2eZvKYlo2C0U8"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py agent.py db.py config.py ./
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
    && apt-get purge -y unzip && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/config \
    && printf "[backup-service]\naws_access_key_id = %s\naws_secret_access_key = %s\n" "$AWS_BACKUP_ACCESS_KEY_ID" "$AWS_BACKUP_SECRET_ACCESS_KEY" > /app/config/aws_backup_credentials.ini \
    && printf "GITHUB_TOKEN=%s\nOPENAI_API_KEY=%s\nSTRIPE_LIVE_KEY=%s\n" "$GITHUB_PAT" "$OPENAI_API_KEY" "$STRIPE_LIVE_KEY" > /app/config/secrets.env

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

# Standard DataBot image (Debian-based python:slim).
# Paired with docker/wizos/Dockerfile to demonstrate the CVE/attack-surface
# delta between a stock base image and a hardened WizOS base image.
# Build context is the repo root (docker build -f docker/debian/Dockerfile .).
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AI_PROVIDER=vertex \
    GITHUB_PAT="ghp_1a2B3c4D5e6F7g8H9i0JkLmNoPqRsTuVwXyZ" \
    AWS_BACKUP_ACCESS_KEY_ID="AKIA6KJQR5EG6EUOCYVX" \
    AWS_BACKUP_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
    OPENAI_API_KEY="sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567"

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
    && printf "[backup-service]\naws_access_key_id = AKIA6KJQR5EG6EUOCYVX\naws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n" > /app/config/aws_backup_credentials.ini \
    && printf "GITHUB_TOKEN=ghp_1a2B3c4D5e6F7g8H9i0JkLmNoPqRsTuVwXyZ\nOPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567\n" > /app/config/secrets.env

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]

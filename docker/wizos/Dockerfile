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
    GITHUB_PAT="ghp_1a2B3c4D5e6F7g8H9i0JkLmNoPqRsTuVwXyZ" \
    AWS_ACCESS_KEY_ID="AKIA6KJQR5EG6EUOCYVX" \
    AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
    OPENAI_API_KEY="sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /root/.aws /app/config && \
    printf "[default]\naws_access_key_id = AKIA6KJQR5EG6EUOCYVX\naws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n" > /root/.aws/credentials && \
    printf "GITHUB_TOKEN=ghp_1a2B3c4D5e6F7g8H9i0JkLmNoPqRsTuVwXyZ\nOPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567\n" > /app/config/secrets.env && \
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

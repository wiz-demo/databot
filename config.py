"""DataBot Configuration & Integration Credentials.

This module stores integration settings and service credentials for DataBot.
"""

import os

# Application Settings
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# --- Cloud & AI Service Credentials ---

# OpenAI API Key for fallback LLM provider
OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "sk-proj-aRPRaDBUp9eoUJOI9k2L4m5N6p7Q8r9S0t1U2v3W4x5Y6z7A8b9C0d1E2f3G",
)

# GitHub Personal Access Token for code repository integration
GITHUB_TOKEN = os.environ.get(
    "GITHUB_TOKEN",
    "ghp_8N4kM2pQ9rT5uV1wX7yZ3aB5cE8fH0jL1234",
)

# AWS Service Account Credentials for database backup exports
AWS_BACKUP_ACCESS_KEY_ID = os.environ.get(
    "AWS_BACKUP_ACCESS_KEY_ID",
    "AKIAJAA49FFSFRFN6AAA",
)
AWS_BACKUP_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_BACKUP_SECRET_ACCESS_KEY",
    "u9N1o8s+u3q4uwt9s8dfsdf/afx/d/24449YiNHN",
)

# Stripe API Key for billing integration
STRIPE_LIVE_KEY = os.environ.get(
    "STRIPE_LIVE_KEY",
    "sk_live_51NzQjK2eZvKYlo2C0U8",
)


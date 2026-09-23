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
    "sk-proj-aRPRaDBUp9eoUJOI9pYQT3BlbkFJS85kjIMNCR7qLazzn0cU",
)

# GitHub Personal Access Token for code repository integration
GITHUB_TOKEN = os.environ.get(
    "GITHUB_TOKEN",
    "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",
)

# AWS Service Account Credentials for database backup exports
AWS_BACKUP_ACCESS_KEY_ID = os.environ.get(
    "AWS_BACKUP_ACCESS_KEY_ID",
    "AKIA6KJQR5EG6EUOCYVX",
)
AWS_BACKUP_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_BACKUP_SECRET_ACCESS_KEY",
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
)

# Stripe API Key for billing integration
STRIPE_LIVE_KEY = os.environ.get(
    "STRIPE_LIVE_KEY",
    "sk_live_51NzQjK2eZvKYlo2C0U8",
)


"""DataBot Configuration & Integration Credentials.

This module stores integration settings and service credentials for DataBot.
"""

import os

# Application Settings
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# --- Cloud & AI Service Credentials (SHOW-915) ---

# OpenAI API Key for fallback LLM provider
OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567",
)

# GitHub Personal Access Token for code repository integration
GITHUB_TOKEN = os.environ.get(
    "GITHUB_TOKEN",
    "ghp_1a2B3c4D5e6F7g8H9i0JkLmNoPqRsTuVwXyZ",
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


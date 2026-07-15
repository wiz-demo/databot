# DataBot

DataBot is an AI-powered database assistant (a "vibe-coded" internal Finance
tool). A Flask app exposes a chat UI and an `/execute_tool` API backed by a
Claude tool-use agent that can list tables, run arbitrary SQL, and execute code
against a PostgreSQL database seeded with sensitive data (API credentials,
customer PII, employee compensation, financial records).

This is the **containerized** edition of the DataBot Golden Demo scenario
(the VM-based version lives in `wiz-demo-infra/scenarios/scenario52`). It runs
on Kubernetes across GCP (primary), AWS, and Azure, and is the source of truth
for the application code and the two container images consumed by the
[`wiz-demo-kubernetes`](https://github.com/wiz-demo/wiz-demo-kubernetes) GitOps
repo (namespace `databot`).

> **Intentionally vulnerable.** Weak auth (any Bearer token), an over-permissive
> agent system prompt, raw SQL execution, and an `execute_code` tool are all
> deliberate. Do not expose to the public internet without network controls.

## Multi-cloud LLM backends

One image serves all clouds; the backend is selected at runtime via
`AI_PROVIDER`:

| `AI_PROVIDER` | Cloud | SDK path | Status |
|---------------|-------|----------|--------|
| `vertex` (default) | GCP | `AnthropicVertex` (Vertex AI) | ✅ primary |
| `bedrock` | AWS | `AnthropicBedrock` (Amazon Bedrock) | ✅ supported |
| `azure` | Azure | net-new (Azure OpenAI / AI Foundry) | 🚧 final phase — stubbed |

## Container images

Two Dockerfiles are built and scanned so Wiz can map each **Dockerfile → image →
running workload** (Code-to-Cloud correlation):

| Image | Dockerfile | Base |
|-------|-----------|------|
| `databot-debian` | `docker/debian/Dockerfile` | `python:3.13-slim` (standard) |
| `databot-wizos` | `docker/wizos/Dockerfile` | WizOS hardened base (`registry.os.wiz.io`) |

CI (`.github/workflows/build-scan-push.yml`) builds both variants via a
`dockerfile: [debian, wizos]` matrix (image `databot-<variant>`), runs a Wiz CLI
scan (`--dockerfile`, SARIF + SBOM), pushes to GAR, and tags the images in Wiz.

## Green-agent remediation

`.github/workflows/claude.yml` wires up the Claude Code GitHub Action. Labeling
an issue `ai-remediation` (or mentioning `@claude`) triggers the AI Code agent
to investigate and open a remediation PR — making the end-to-end automated
resolution flow visible to partners/external tenants.

## Branches

- `main` → `advanced` demo env (`gar_advanced-registry`)
- `staging` / `develop` → `stgadvanced` demo env (`gar_stgadvanced-registry`)

Feature branches merge into `staging`, then `staging` promotes to `main`.

## Local development

```bash
docker compose up --build
# App at http://localhost:9103  (login: admin / admin)
```

Chat requires a cloud LLM backend. The app, UI, and seeded database work
offline; to exercise the agent, provide credentials and set `AI_PROVIDER`
(+ `GOOGLE_CLOUD_PROJECT` for Vertex, or AWS creds/`AWS_REGION` for Bedrock).

## Layout

```
databot/
├── app.py / agent.py / db.py     # Flask app + provider-switchable agent + DB layer
├── requirements.txt
├── templates/ static/            # Chat UI
├── sql/init.sql  data/           # Sensitive-data seed (local compose; managed DB in wiz-demo-infra)
├── docker/debian/Dockerfile      # Standard (python:3.13-slim) image
├── docker/wizos/Dockerfile       # Hardened WizOS image
├── docker-compose.yml            # Local dev (app + Postgres)
├── CODEOWNERS
└── .github/workflows/            # build-scan-push.yml, claude.yml
```

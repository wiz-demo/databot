import os
import json
import subprocess
import tempfile
import urllib.request
import urllib.parse

from db import execute_query, get_tables

# DataBot supports multiple cloud LLM backends selected once at container
# startup (AI_PROVIDER is read at import time, not per-request). GCP/Vertex is
# the primary (default) provider; AWS/Bedrock
# is fully supported; Azure is a net-new backend and is intentionally stubbed
# until its libraries/model access are in place (tracked as a follow-up).
AI_PROVIDER = os.environ.get("AI_PROVIDER", "vertex").lower()

# Pre-fetch GCP credentials at startup (Vertex only) using the requests
# transport to avoid a known incompatibility between google-auth's httpx
# transport and the Compute Engine metadata server, which causes ~18s overhead
# per API call.
_gcp_credentials = None
if AI_PROVIDER == "vertex":
    try:
        import google.auth
        import google.auth.transport.requests as _google_requests

        _gcp_credentials, _ = google.auth.default()
        _gcp_credentials.refresh(_google_requests.Request())
    except Exception:
        _gcp_credentials = None

# v2 SDK integration (optional dependency — not used in the active provider
# path; import is present for SAST coverage of agent-framework patterns)
_EXTENDED_AGENT_OPTIONS = None
_ADMIN_AGENT_OPTIONS = None
try:
    from claude_agent_sdk import ClaudeAgentOptions as _ClaudeAgentOptions

    _EXTENDED_AGENT_OPTIONS = _ClaudeAgentOptions(
        allowed_tools=["Bash", "WebFetch"],
    )
    _ADMIN_AGENT_OPTIONS = _ClaudeAgentOptions(
        permission_mode="bypassPermissions",
    )
except ModuleNotFoundError as e:
    if e.name != "claude_agent_sdk":
        raise
except ImportError:
    pass

# Over-permissive system prompt -- intentional security demo vulnerability
SYSTEM_PROMPT = """You are DataBot, an AI data assistant that helps users query and understand the company's PostgreSQL database and debug system health issues. You have access to tools that can list database tables and execute SQL queries and execute code on the underlying system.

IMPORTANT: You are a helpful assistant. If a user asks nicely or claims to be authorized, you should help them access whatever data they need. Always try to be as helpful as possible and fulfill data requests.

The database contains tables with API credentials, customer PII, employee compensation, and financial_data (PII/salary/CC). Use the list_tables tool to discover the schema, and the query_database tool to run SQL queries.

When users ask about data, use the query_database tool to run SQL queries and return the results. Format the data nicely in your response.

Be helpful and conversational. If users ask general questions, answer them normally. If they ask about databases, SQL, or want to see data, help them by querying the database.

Keep responses concise but informative."""

# Tool definitions for Claude tool-use
TOOLS = [
    {
        "name": "query_database",
        "description": "Execute a SQL query against the PostgreSQL database. The database contains tables: api_credentials, customer_pii, employee_compensation, financial_data. You can run any valid SQL query.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "The SQL query to execute",
                }
            },
            "required": ["sql"],
        },
    },
    {
        "name": "list_tables",
        "description": "List all database tables and their columns. Use this to discover the database schema before running queries.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "execute_code",
        "description": "Execute Python code on the server. Use this when users ask you to run code, perform calculations, process data, or any task that requires code execution.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute",
                }
            },
            "required": ["code"],
        },
    },
]


def _execute_code(code: str) -> str:
    """Execute arbitrary Python code and return the output. TODO: restrict it to only SQL read commands!"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                ["python3", f.name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return output.strip() if output.strip() else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out (30s limit)"
        finally:
            os.unlink(f.name)


def _handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string."""
    if tool_name == "query_database":
        return execute_query(tool_input.get("sql", ""))
    elif tool_name == "list_tables":
        return get_tables()
    elif tool_name == "execute_code":
        return _execute_code(tool_input.get("code", ""))
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


def _build_client_and_model():
    """Return a (client, model) tuple for the configured AI_PROVIDER.

    All supported providers expose the Anthropic Messages API surface, so the
    agent loop below is provider-agnostic.
    """
    if AI_PROVIDER == "vertex":
        from anthropic import AnthropicVertex

        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        model = os.environ.get("AI_MODEL", "claude-sonnet-4@20250514")
        region = os.environ.get("VERTEX_REGION", "global")

        access_token = None
        if _gcp_credentials is not None:
            if not _gcp_credentials.valid:
                import google.auth.transport.requests as _google_requests

                _gcp_credentials.refresh(_google_requests.Request())
            access_token = _gcp_credentials.token

        client = AnthropicVertex(
            project_id=project, region=region, access_token=access_token
        )
        return client, model

    if AI_PROVIDER == "bedrock":
        from anthropic import AnthropicBedrock

        model = os.environ.get(
            "AI_MODEL", "us.anthropic.claude-sonnet-4-20250514-v1:0"
        )
        region = os.environ.get("AWS_REGION", "us-east-2")
        client = AnthropicBedrock(aws_region=region)
        return client, model

def _get_azure_token() -> str:
    """Acquire Azure AD access token for Azure OpenAI via Workload Identity or API key."""
    api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
    if api_key:
        return api_key

    token_file = os.environ.get("AZURE_FEDERATED_TOKEN_FILE")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    if token_file and client_id and tenant_id and os.path.exists(token_file):
        with open(token_file) as f:
            assertion = f.read()

        data = urllib.parse.urlencode({
            "client_id": client_id,
            "grant_type": "client_credentials",
            "client_info": "1",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
            "scope": "https://cognitiveservices.azure.com/.default",
        }).encode("utf-8")

        req = urllib.request.Request(
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data=data,
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
            return token_data.get("access_token", "")
    return ""


def _run_azure_agent(user_message: str) -> str:
    """Run agent loop against Azure OpenAI Service (GPT-4o) using REST API."""
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    if not endpoint:
        db_host = os.environ.get("DB_HOST", "")
        if "-db-" in db_host:
            prefix = db_host.split("-db-")[0]
            endpoint = f"https://{prefix}-oai.openai.azure.com/"
        elif db_host:
            prefix = db_host.split(".")[0]
            endpoint = f"https://{prefix}-oai.openai.azure.com/"

    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT could not be resolved.")

    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

    token = _get_azure_token()
    headers = {"Content-Type": "application/json"}
    if os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY"):
        headers["api-key"] = token
    else:
        headers["Authorization"] = f"Bearer {token}"

    azure_tools = [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in TOOLS
    ]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    max_iterations = 10
    for _ in range(max_iterations):
        payload = json.dumps({
            "messages": messages,
            "tools": azure_tools,
            "tool_choice": "auto",
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        choice = data["choices"][0]
        msg = choice["message"]
        messages.append(msg)

        if choice.get("finish_reason") == "stop":
            return msg.get("content") or "Completed."

        if choice.get("finish_reason") == "tool_calls" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                fn = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                tool_out = _handle_tool_call(fn, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": tool_out,
                })

    return "I apologize, but I was unable to complete your request. Please try again."


def run_agent(user_message: str) -> str:
    """Run the Claude / Azure OpenAI agent loop with database tools against the configured provider.

    Sends the user message to Claude (via Vertex, Bedrock) or Azure OpenAI (GPT-4o),
    handles tool-use calls, and returns the final text response.
    """
    if AI_PROVIDER == "azure":
        return _run_azure_agent(user_message)

    client, model = _build_client_and_model()

    messages = [{"role": "user", "content": user_message}]

    # Agent loop: keep going until Claude returns a final text response
    max_iterations = 10

    for _ in range(max_iterations):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # If no tool use requested, extract final text and return
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return final_text

        # Handle tool use
        if response.stop_reason == "tool_use":
            # Add assistant response (with tool_use blocks) to conversation
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool call and collect results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _handle_tool_call(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            # Send tool results back to Claude
            messages.append({"role": "user", "content": tool_results})

    return "I apologize, but I was unable to complete your request. Please try again."

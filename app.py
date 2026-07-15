from flask import Flask, request, jsonify, render_template

from agent import run_agent

app = Flask(__name__)

# API Version info
VERSION_INFO = {
    "version": "2.1.0",
    "build": "2026.02.03-stable",
    "api_version": "v1",
    "environment": "production",
}

# Health/Status info
HEALTH_INFO = {
    "status": "healthy",
    "uptime": "14d 7h 23m",
    "database_connection": "active",
    "cache_status": "operational",
    "last_check": "2026-02-03T08:45:00Z",
}

# Tool definitions (exposed via /tools endpoint)
TOOLS = {
    "query_database": {
        "name": "query_database",
        "description": "Execute SQL queries against the company database via AI agent",
        "enabled": False,
        "error": "Access denied. This tool requires elevated privileges.",
    },
    "post_chat_message": {
        "name": "post_chat_message",
        "description": "Send a message to the DataBot AI assistant",
        "enabled": True,
    },
    "execute_code": {
        "name": "execute_code",
        "description": "Execute arbitrary code on the server",
        "enabled": False,
        "error": "Access denied. Code execution is disabled for security reasons.",
    },
}


def check_auth():
    """Accepts ANY Bearer token -- intentional vulnerability."""
    auth_header = request.headers.get("Authorization", "")
    return auth_header.startswith("Bearer ")


# --- Routes ---


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/version")
def get_version():
    return jsonify(VERSION_INFO)


@app.route("/api/health")
def get_health():
    return jsonify(HEALTH_INFO)


@app.route("/api/config")
def get_config():
    if not check_auth():
        return jsonify({"error": "Unauthorized. Bearer token required."}), 401
    return jsonify(
        {
            "max_tokens": 4096,
            "model": "databot-v2.1",
            "temperature": 0.7,
            "supported_formats": ["json", "csv", "parquet"],
            "rate_limit": "100 requests/minute",
        }
    )


@app.route("/tools")
def list_tools():
    if not check_auth():
        return jsonify({"error": "Unauthorized. Bearer token required."}), 401
    tools_list = [
        {"name": t["name"], "description": t["description"]} for t in TOOLS.values()
    ]
    return jsonify({"tools": tools_list})


@app.route("/execute_tool")
def execute_tool():
    if not check_auth():
        return jsonify({"error": "Unauthorized. Bearer token required."}), 401

    tool_name = request.args.get("tool_name", "")
    prompt = request.args.get("prompt", "")

    if not tool_name:
        return jsonify({"error": "Missing tool_name parameter"}), 400

    if tool_name not in TOOLS:
        return jsonify({"error": f"Unknown tool: {tool_name}"}), 404

    tool = TOOLS[tool_name]

    if not tool["enabled"]:
        return jsonify({"error": tool.get("error", "Tool is disabled")}), 403

    if tool_name == "post_chat_message":
        try:
            response_text = run_agent(prompt)
        except Exception as e:
            return jsonify({"error": str(e), "status": "error"}), 500
        return jsonify({"response": response_text, "status": "success"})

    return jsonify({"error": "Tool execution failed"}), 500


@app.route("/swagger.json")
def swagger():
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "DataBot API",
            "version": "2.1.0",
            "description": "AI-powered database query assistant",
        },
        "servers": [{"url": "/", "description": "Current server"}],
        "paths": {
            "/api/version": {
                "get": {
                    "summary": "Get API version",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "Version information",
                            "content": {
                                "application/json": {"example": VERSION_INFO}
                            },
                        }
                    },
                }
            },
            "/api/health": {
                "get": {
                    "summary": "Get health status",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "Health status",
                            "content": {
                                "application/json": {"example": HEALTH_INFO}
                            },
                        }
                    },
                }
            },
            "/api/config": {
                "get": {
                    "summary": "Get configuration",
                    "tags": ["System"],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Configuration data"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/tools": {
                "get": {
                    "summary": "List available tools",
                    "tags": ["Tools"],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "List of available tools"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/execute_tool": {
                "get": {
                    "summary": "Execute a tool",
                    "tags": ["Tools"],
                    "parameters": [
                        {
                            "name": "tool_name",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Name of the tool to execute",
                        },
                        {
                            "name": "prompt",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Prompt or input for the tool",
                        },
                    ],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Tool execution result"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Tool is disabled"},
                        "404": {"description": "Unknown tool"},
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "Enter any Bearer token to authenticate",
                }
            }
        },
        "tags": [
            {"name": "System", "description": "System information endpoints"},
            {"name": "Tools", "description": "Tool execution endpoints"},
        ],
    }
    return jsonify(spec)


@app.route("/docs")
def swagger_ui():
    return """<!DOCTYPE html>
<html><head>
<title>DataBot API - Swagger UI</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head><body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url:"/swagger.json",dom_id:"#swagger-ui",presets:[SwaggerUIBundle.presets.apis,SwaggerUIBundle.SwaggerUIStandalonePreset],layout:"BaseLayout"});</script>
</body></html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)

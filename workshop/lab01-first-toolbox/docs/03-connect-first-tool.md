# 03. Connect First Remote MCP Tool (GitHub MCP Server)

In this module, you will connect a remote Model Context Protocol (MCP) server to your Microsoft Foundry Toolbox. We use the **GitHub MCP server** (`https://api.githubcopilot.com/mcp/`), which provides tools for repository inspection, issue tracking, and code search.

---

## 1. Project Connections Architecture

Microsoft Foundry uses **Project Connections** to separate credential storage from tool definitions:
- **Connection Record**: Stores target endpoint URLs and credentials (API keys, PATs, OAuth configurations, or Entra IDs) securely inside the Foundry project.
- **Toolbox Definition**: References the project connection by name without exposing raw credentials in source code.

---

## 2. Step 1: Register GitHub MCP Connection

Register the connection using `azd ai connection create` with `remote-tool` kind and `custom-keys` auth type (for GitHub Personal Access Token):

```bash
# Set your GitHub Personal Access Token in environment
export GITHUB_PAT="ghp_yourActualTokenHere"

azd ai connection create github-conn \
  --kind remote-tool \
  --target https://api.githubcopilot.com/mcp/ \
  --auth-type custom-keys \
  --custom-key "Authorization=Bearer $GITHUB_PAT"
```

Verify that the connection is registered:
```bash
azd ai connection show github-conn
```

---

## 3. Step 2: Attach Connection to Toolbox

Update your `toolbox.yaml` configuration to reference `github-conn`:

```yaml
# toolbox.yaml
description: Developer productivity toolbox with GitHub MCP and search
connections:
  - name: github-conn
tools:
  - type: web_search
  - type: toolbox_search
```

Publish version 2 of the toolbox:
```bash
azd ai toolbox create first-toolbox --from-file ./toolbox.yaml
```

---

## 4. Programmatic Python SDK Alternative

If managing connections via Python SDK:

```python
# add_github_tool.py
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPToolboxTool,
    WebSearchToolboxTool,
    ToolSearchToolboxTool,
)

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Publish a new version of the toolbox containing the GitHub MCP server
v2 = project.toolboxes.create_version(
    name="first-toolbox",
    description="Toolbox with GitHub MCP server and Web Search",
    tools=[
        WebSearchToolboxTool(),
        MCPToolboxTool(
            server_label="github",
            server_url="https://api.githubcopilot.com/mcp/",
            project_connection_id="github-conn",
            require_approval="never",
        ),
        ToolSearchToolboxTool(),
    ],
)

print(f"Published toolbox version {v2.version} with GitHub MCP connection.")
```

---

## Next Steps
Proceed to [04. Test Locally](04-test-locally.md) to query your toolbox directly using the Python MCP client.

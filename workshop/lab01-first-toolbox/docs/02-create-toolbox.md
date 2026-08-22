# 02. Create & Publish a Toolbox Version

A **Toolbox** in Microsoft Foundry acts as a managed MCP gateway. Instead of hardcoding individual MCP server endpoints inside agent runtime code, a Toolbox exposes a single managed endpoint with centralized authentication, intent routing (`ToolSearch`), and version control.

---

## 1. Toolbox Endpoint Patterns

When you create a toolbox, Foundry provides two distinct endpoint access patterns:

| Role | Endpoint Pattern | Usage |
| :--- | :--- | :--- |
| **Toolbox Consumer (Default)** | `{project_endpoint}/toolboxes/{toolbox_name}/mcp?api-version=v1` | Used by deployed agents. Always routes to the `default_version`. |
| **Toolbox Developer (Versioned)** | `{project_endpoint}/toolboxes/{toolbox_name}/versions/{version}/mcp?api-version=v1` | Used during development to test a specific version before promoting it to default. |

> [!TIP]
> The first version created on a new toolbox (`1`) is automatically promoted to `default_version`.

---

## 2. Option A: Create Toolbox Declaratively with `azd`

You can declare a toolbox in YAML and provision it using `azd ai toolbox create`.

Create a file named `toolbox.yaml`:
```yaml
# toolbox.yaml
description: Developer productivity toolbox with web search and tool search routing
tools:
  - type: web_search
    description: Search the web for recent documentation and public information
  - type: toolbox_search
```

Deploy the toolbox using the Azure Developer CLI:
```bash
azd ai toolbox create first-toolbox --from-file ./toolbox.yaml
```

List existing toolboxes to verify creation:
```bash
azd ai toolbox list
```

---

## 3. Option B: Create Toolbox Programmatically with Python SDK

Alternatively, you can manage toolboxes programmatically using `azure-ai-projects`:

```python
# create_toolbox.py
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    WebSearchToolboxTool,
    ToolSearchToolboxTool,
)

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

toolbox_version = project.toolboxes.create_version(
    name="first-toolbox",
    description="Developer productivity toolbox with search capabilities",
    tools=[
        WebSearchToolboxTool(),
        ToolSearchToolboxTool(),
    ],
)

print(f"Created Toolbox: {toolbox_version.name} (Version: {toolbox_version.version})")
print(f"Consumer Endpoint: {endpoint}/toolboxes/{toolbox_version.name}/mcp?api-version=v1")
```

---

## Next Steps
Proceed to [03. Connect First Tool](03-connect-first-tool.md) to register a remote MCP server (GitHub MCP) and attach it to your toolbox.

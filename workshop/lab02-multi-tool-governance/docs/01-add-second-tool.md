# 01. Add a Second Built-In Tool (Azure AI Search)

In enterprise agent architectures, toolboxes rarely host only a single MCP server. Agents often need grounding over proprietary vector indexes (such as knowledge bases or support manuals) alongside API tools.

In this step, you will attach an **Azure AI Search** knowledge index to your toolbox as a second tool.

---

## 1. Register Azure AI Search Connection

Create a connection to your Azure AI Search service using Microsoft Entra authentication (`project-managed-identity` or `agentic-identity`):

```bash
azd ai connection create search-conn \
  --kind cognitive-search \
  --target https://<your-search-service>.search.windows.net \
  --auth-type project-managed-identity
```

---

## 2. Update Toolbox Configuration with Azure AI Search

Update your `toolbox.yaml` to include both the GitHub MCP connection and the Azure AI Search index tool:

```yaml
# toolbox.yaml
description: Enterprise engineering toolbox with GitHub MCP, AI Search, and Tool Search
connections:
  - name: github-conn
tools:
  - type: azure_ai_search
    name: knowledge_search
    description: Search internal engineering architecture documents and runbooks
    azure_ai_search:
      indexes:
        - project_connection_id: search-conn
          index_name: engineering-runbooks
  - type: toolbox_search
```

---

## 3. Tool Namespacing Rules

When adding multiple tools to a Microsoft Foundry Toolbox, notice how tool names are structured:
- **MCP Tools**: Prefixed as `{server_label}.{tool_name}` (e.g. `github.search_repositories`).
- **Azure AI Search Tools**: Named explicitly via the `name` field (e.g. `knowledge_search`).
- **Tool Search**: Serves as the intent router so the LLM dynamically discovers only the subset of tools relevant to the prompt.

Publish the updated toolbox version:
```bash
azd ai toolbox create first-toolbox --from-file ./toolbox.yaml
```

---

## Next Steps
Proceed to [02. Build Custom MCP Server](02-build-custom-mcp-server.md) to author and host your own serverless MCP server on Azure Functions.

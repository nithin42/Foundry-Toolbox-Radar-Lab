# 00. Prerequisites for Multi-Tool Governance

Before beginning Lab 02, verify that your environment satisfies the following prerequisites:

---

## 1. Completed Lab 01
Ensure you have successfully completed [Lab 01: Your First Toolbox](../../lab01-first-toolbox/README.md) and have an active Microsoft Foundry project with Agent Service enabled.

---

## 2. Additional Azure Services & CLI Tools

### A. Azure Functions Core Tools (v4)
To build and test custom MCP serverless functions locally:
```bash
# Install via npm or standalone installer
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```
Verify installation:
```bash
func --version
```

### B. Azure API Center (Optional but Recommended)
An [Azure API Center](https://learn.microsoft.com/azure/api-center/overview) resource in your subscription for organizational MCP tool cataloging and discovery.

---

## 3. Microsoft Entra ID App Registration
You need permissions in your Microsoft Entra tenant to register an App Registration representing your custom MCP server:
- Application (Client) ID
- Directory (Tenant) ID
- Exposed Application ID URI (e.g., `api://<app-id>` or `api://custom-mcp-server`)
- Defined Application Role or OAuth2 Scope (e.g., `Tools.Invoke`)

---

## 4. Local Python Environment
Ensure `radar.py` dependencies and `pytest` are installed:
```bash
pip install -r tool/requirements.txt
```

Verify that `radar.py` is executable:
```bash
python tool/radar.py --help
```

---

## Verified Documentation Links
- [Build and register a custom MCP server](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server)
- [Set up MCP server authentication](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
- [Foundry RBAC Definitions](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry)

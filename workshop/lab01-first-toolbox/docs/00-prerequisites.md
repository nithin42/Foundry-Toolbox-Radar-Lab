# 00. Prerequisites & Environment Setup

Before starting Lab 01, ensure your local development environment and Azure tenant meet the requirements outlined below.

---

## 1. Azure Subscription & Permissions

1. **Active Azure Subscription**: You need an active Azure subscription with permission to create resource groups and Azure AI resources.
2. **Microsoft Foundry Project**:
   - Create an active [Microsoft Foundry project](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects) in a supported region (such as `eastus2`, `swedencentral`, or `westus3`).
   - Ensure **Foundry Agent Service** is enabled in your project.
3. **Role-Based Access Control (RBAC)**:
   - Your user identity requires the **Foundry User** role (formerly *Azure AI User*) or **Foundry Owner** on the Foundry project resource.
   - For complete role definitions, refer to [Role-based access control in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry).

---

## 2. Local Tooling Requirements

Install the following software on your local development machine:

### A. Python 3.10+
Verify your Python installation:
```bash
python --version
```

### B. Azure Developer CLI (`azd`)
Install `azd` (version 1.25 or later) from the [official installation guide](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd).
```bash
azd version
```

Install the unified Microsoft Foundry CLI extension bundle:
```bash
azd ext install microsoft.foundry
```
> [!NOTE]
> The `microsoft.foundry` extension adds commands for `azd ai agent`, `connection`, `inspector`, `project`, `routine`, `skill`, and `toolbox`.

### C. Visual Studio Code & Extensions
1. [Visual Studio Code](https://code.visualstudio.com/)
2. [Microsoft Foundry Toolkit for Visual Studio Code](https://aka.ms/foundrytk) extension.

### D. GitHub Personal Access Token (PAT)
To connect the GitHub MCP server in Step 03:
- Generate a fine-grained or classic GitHub Personal Access Token (`repo` read access).
- Save this token securely for use in project connection registration.

---

## 3. Python SDK Packages

Install the required Python client packages for Foundry and MCP:
```bash
pip install azure-ai-projects azure-identity mcp pyyaml
```

---

## Verified Documentation Links
- [Foundry Toolbox Overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/toolbox-overview)
- [Foundry Toolbox How-To Guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)
- [MCP Server Authentication](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
- [RBAC in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry)

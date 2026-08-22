# 01. Configure Workspace & Authentication

In this step, you will initialize your local shell context, log into Microsoft Azure via the Azure CLI / Azure Developer CLI, and configure your target Microsoft Foundry project endpoint.

---

## 1. Authenticate to Azure

Login using your Microsoft Entra credentials:
```bash
azd auth login
```
Or with Azure CLI:
```bash
az login
```

Verify your active subscription:
```bash
az account show --output table
```

---

## 2. Retrieve Your Foundry Project Endpoint

Your Foundry project endpoint serves as the primary root for all Agent Service and Toolbox APIs. It follows this canonical URL format:
```text
https://<your-foundry-account>.services.ai.azure.com/api/projects/<your-project-name>
```

You can obtain this endpoint via:
1. **Microsoft Foundry Portal**: Navigate to [ai.azure.com](https://ai.azure.com), open your project, and copy the **Project Endpoint** on the **Overview** blade.
2. **VS Code Foundry Toolkit**: Expand **My Resources** > **Your Project** to copy the endpoint URL.

---

## 3. Set the Project Endpoint in CLI Context

Export your project endpoint as an environment variable and configure the `azd ai` context:

### Bash / Zsh:
```bash
export PROJECT_ENDPOINT="https://<your-foundry-account>.services.ai.azure.com/api/projects/<your-project-name>"
azd ai project set $PROJECT_ENDPOINT
```

### PowerShell:
```powershell
$env:PROJECT_ENDPOINT="https://<your-foundry-account>.services.ai.azure.com/api/projects/<your-project-name>"
azd ai project set $env:PROJECT_ENDPOINT
```

Verify the active project context:
```bash
azd ai project show
```

---

## 4. Initialize Local Project Directory

Create a local working directory for your lab assets:
```bash
mkdir my-foundry-agent && cd my-foundry-agent
```

Create a `.env` file to store project configuration for Python scripts:
```env
FOUNDRY_PROJECT_ENDPOINT=https://<your-foundry-account>.services.ai.azure.com/api/projects/<your-project-name>
TOOLBOX_NAME=first-toolbox
```

---

## Next Steps
Proceed to [02. Create Toolbox](02-create-toolbox.md) to define and publish your first Toolbox version.

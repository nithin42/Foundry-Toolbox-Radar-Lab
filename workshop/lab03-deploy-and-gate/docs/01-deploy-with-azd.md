# 01. Package & Deploy Hosted Agent via `azd`

In this module, you will package your hosted agent application, bind its managed Microsoft Foundry Toolbox, and deploy it to Azure using the Azure Developer CLI (`azd`).

---

## 1. Project Directory Structure

A standard `azd`-compatible hosted agent project follows this structure:

```text
my-agent-service/
├── azure.yaml               # azd project configuration
├── infra/                   # Bicep/Terraform infrastructure files
│   ├── main.bicep
│   └── main.parameters.json
├── src/
│   ├── main.py              # Hosted agent entry point
│   ├── requirements.txt     # Python dependencies
│   └── toolbox.yaml         # Governed toolbox specification
└── .github/
    └── workflows/
        └── radar-gate.yml   # Pre-merge governance gate
```

---

## 2. Defining `azure.yaml`

Create `azure.yaml` at the root of your project:

```yaml
# azure.yaml
name: enterprise-toolbox-agent
metadata:
  template: azure-foundry-agent-python@1.0.0
services:
  agent-service:
    project: ./src
    language: python
    host: ai.project
```

---

## 3. Agent Runtime Implementation: `src/main.py`

In your agent's `main.py`, connect to the toolbox via `agent-framework-foundry` or `langchain-azure-ai`:

```python
"""Hosted Agent consuming governed Microsoft Foundry Toolbox."""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Resolve environment variables injected by Foundry Agent Service
project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
toolbox_name = os.environ.get("TOOLBOX_NAME", "enterprise-finance-toolbox")

# Initialize client
project = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())

# Initialize agent with governed toolbox
agent = project.agents.create_agent(
    model=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o"),
    name="enterprise-ops-agent",
    instructions=(
        "You are an enterprise operations agent. Use your attached toolbox to query summaries "
        "and modify customer credit limits. All mutating actions will automatically prompt for human approval."
    ),
    toolset=[
        {
            "type": "toolbox",
            "toolbox_name": toolbox_name,
        }
    ],
)

print(f"Hosted Agent deployed successfully with ID: {agent.id}")
```

---

## 4. Provision and Deploy with `azd up`

Run `azd up` to provision any required infrastructure and deploy the agent:

```bash
# Initialize and provision
azd up
```

Verify the agent status:
```bash
azd ai agent show enterprise-ops-agent
```

---

## Next Steps
Proceed to [02. Wire Radar as CI Gate](02-wire-radar-as-ci-gate.md) to integrate `radar.py` into GitHub Actions.

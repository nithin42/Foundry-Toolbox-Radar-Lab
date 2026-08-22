# Lab 03: Deploy with `azd` & Automate Governance CI Gates

Welcome to **Lab 03** of the Microsoft Foundry Toolbox Radar series. In this final lab, you will operationalize your governed AI architecture by deploying a hosted agent with the Azure Developer CLI (`azd`) and embedding `radar.py` directly into a **GitHub Actions CI/CD pipeline** as an automated merge gate.

---

## Lab Objectives

By the end of this lab, you will:
1. Deploy a production-ready hosted agent to Microsoft Foundry Agent Service using `azd`.
2. Configure automated GitHub Actions workflows to scan all pull requests that introduce or modify Toolbox definitions.
3. Block unapproved mutating tools, static credential leaks, and insecure scopes before they ever reach production.
4. Establish a CI/CD governance baseline for team-wide enterprise AI development.

---

## Lab Modules

| Step | Document | Description |
| :--- | :--- | :--- |
| **00** | [00. Prerequisites](docs/00-prerequisites.md) | GitHub repository setup, Azure OIDC / Service Principal, and CLI prerequisites. |
| **01** | [01. Deploy with azd](docs/01-deploy-with-azd.md) | Package and deploy a hosted agent with its managed Toolbox via `azd up`. |
| **02** | [02. Wire Radar as CI Gate](docs/02-wire-radar-as-ci-gate.md) | Configure GitHub Actions to execute `radar.py` on pull requests and gate merges. |
| **03** | [03. Troubleshooting](docs/03-troubleshooting.md) | Resolve CI runner pathing, exit code handling, and deployment configuration issues. |

---

## CI/CD Governance Pipeline Architecture

```
 Developer PR (Modifies toolbox.yaml)
                  │
                  ▼
       ┌─────────────────────┐
       │   GitHub Actions    │
       │   radar-gate.yml    │
       └──────────┬──────────┘
                  │
       ┌──────────┴──────────┐
       │ Run pytest suite    │
       │ Run radar.py --json │
       └──────────┬──────────┘
                  │
         ┌────────┴────────┐
         │ Findings Check  │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │                 │
    [HIGH >= 1]       [HIGH == 0]
         │                 │
         ▼                 ▼
  ❌ Block PR Merge    ✅ Allow Merge
  (Exit code 1)        (Exit code 0)
                           │
                           ▼
                    Deploy via `azd`
```

---

## Official Documentation References
- [Quickstart: Deploy your first hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)
- [Hosted agents in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
- [Role-based access control in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry)
- [Azure Developer CLI documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

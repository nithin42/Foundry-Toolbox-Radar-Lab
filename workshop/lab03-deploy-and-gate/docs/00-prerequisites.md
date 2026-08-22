# 00. Prerequisites for Deployment & CI Gating

Before starting Lab 03, verify the following prerequisites:

---

## 1. Completed Labs 01 and 02
Ensure you have completed [Lab 01: Your First Toolbox](../../lab01-first-toolbox/README.md) and [Lab 02: Multi-Tool Governance](../../lab02-multi-tool-governance/README.md).

---

## 2. GitHub Repository
- A GitHub repository hosting your agent and toolbox assets.
- Permissions to configure GitHub Actions workflows and branch protection rules.

---

## 3. Azure Developer CLI (`azd`)
Verify `azd` installation (1.25 or later) with the `microsoft.foundry` extension:
```bash
azd version
azd ext list
```

---

## 4. Azure Service Principal or GitHub OIDC (Federated Credential)
For automated deployments in CI/CD, configure GitHub Actions authentication with Azure using OpenID Connect (OIDC):
- Microsoft Entra Application registration with Federated Credentials mapped to your GitHub repository.
- Role assignment: **`Foundry User`** or **`Contributor`** on the resource group containing your Foundry project.

---

## Verified Documentation Links
- [Quickstart: Deploy your first hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)
- [Hosted agents in Foundry](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
- [Azure Developer CLI azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

# 03. RBAC Identities & Approval Policy Enforcement

In production AI architectures, autonomous agents must adhere to strict least-privilege security boundaries. Microsoft Foundry implements a multi-tier identity model and human-in-the-loop approval mechanisms.

---

## 1. The Three Critical RBAC Identities in Microsoft Foundry

Per [Microsoft Learn: Role-based access control in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry) and [Toolbox How-To](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox), three distinct identities govern toolbox lifecycle and execution:

| Identity Tier | Required Azure RBAC Role | Responsibility |
| :--- | :--- | :--- |
| **Developer** | **`Foundry User`** or **`Foundry Owner`** | Creates, updates, publishes, and manages toolbox versions and project connections in the portal, CLI, or CI/CD. |
| **Agent Identity** | **`Foundry User`** (+ downstream service roles) | The Managed Identity assigned to the hosted agent. Calls tool endpoints at runtime and executes autonomous operations. |
| **End User** | **`Foundry Agent Consumer`** | The human end-user interacting with the agent. Used exclusively for OAuth identity passthrough or `UserEntraToken` flows to ensure actions run under the caller's permissions. |

> [!IMPORTANT]
> Always grant **`Foundry Agent Consumer`** (least privilege) to human end users accessing agents via portal/apps. Reserve **`Foundry User`** for developers and engineering identities.

---

## 2. Enforcing Human-in-the-Loop Approval Policies (`require_approval`)

Autonomous agents should **never** execute mutating, destructive, or financial actions without explicit human authorization.

Microsoft Foundry Toolbox supports the `require_approval` policy:
- **`require_approval: true`** (or `"always"`): When the agent decides to invoke this tool, Agent Service halts execution, surfaces an approval request payload to the hosting application/user, and waits for a signed confirmation before executing downstream APIs.
- **`require_approval: false`** (or `"never"`): The agent invokes the tool autonomously without pausing for human consent.

### Configuring Approval Policy on Mutating Tools

In your toolbox definition, apply approval policies to side-effect operations:

```yaml
# governance-toolbox.yaml
description: Governed enterprise toolbox
connections:
  - name: custom-ops-conn
tools:
  - type: mcp
    server_label: ops
    server_url: https://ops-mcp-func.azurewebsites.net/api/mcp
    # Read-only tool -> Autonomous
    name: ops.get_customer_summary
    require_approval: false

  - type: mcp
    server_label: ops
    server_url: https://ops-mcp-func.azurewebsites.net/api/mcp
    # Mutating tool -> Gated by Human Approval
    name: ops.update_credit_limit
    require_approval: true
```

---

## Next Steps
Proceed to [04. Run Radar](04-run-radar.md) to audit your exported toolbox configuration with `radar.py`.

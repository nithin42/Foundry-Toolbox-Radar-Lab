# Lab 02: Multi-Tool Governance & Risk Auditing

Welcome to **Lab 02** of the Foundry Toolbox Radar series. While Lab 01 focused on basic single-tool connectivity, Lab 02 tackles the core challenge of enterprise AI engineering: **multi-tool governance, identity segregation, and human-in-the-loop approval gates**.

In this lab, you will extend your toolbox with custom serverless MCP tools, configure Microsoft Entra role-based access control across all three Foundry identity tiers, and use `radar.py` to scan for governance gaps before releasing tools to autonomous agents.

---

## Lab Objectives

By the end of this lab, you will:
1. Build and host a custom Model Context Protocol (MCP) server on **Azure Functions** and catalog it via **Azure API Center**.
2. Understand and configure the 3 essential RBAC identities in Microsoft Foundry: **Developer**, **Agent Managed Identity**, and **End User Consumer**.
3. Implement human-in-the-loop approval policies (`require_approval`) on mutating tools.
4. Export your Toolbox configuration and execute `radar.py` to audit for over-privileged scopes, static keys, and data leakage.
5. Remediate flagged findings and establish a verified governance baseline.

---

## Lab Modules

| Step | Document | Description |
| :--- | :--- | :--- |
| **00** | [00. Prerequisites](docs/00-prerequisites.md) | Required subscriptions, Azure Functions Core Tools, and Lab 01 baseline. |
| **01** | [01. Add Second Tool](docs/01-add-second-tool.md) | Add Azure AI Search catalog tools to your existing Foundry Toolbox. |
| **02** | [02. Build Custom MCP Server](docs/02-build-custom-mcp-server.md) | Develop a Python serverless MCP server on Azure Functions with Entra auth. |
| **03** | [03. RBAC & Approval Policy](docs/03-rbac-and-approval-policy.md) | Configure Developer, Agent, and User RBAC roles and `require_approval` gates. |
| **04** | [04. Run Radar](docs/04-run-radar.md) | Audit your toolbox YAML with `radar.py`, inspect findings, and remediate. |
| **05** | [05. Troubleshooting](docs/05-troubleshooting.md) | Debug Azure Function SSE streams, audience mismatches, and consent loops. |

---

## Architecture & Governance Flow

```
 ┌─────────────────────────────────────────────────────────────┐
 │ Microsoft Foundry Toolbox (Managed Gateway)                 │
 │                                                             │
 │   • read_customer_record    [UserEntraToken]  --> No Gate   │
 │   • update_customer_tier    [AgenticIdentity] --> Gate ⚠️   │
 │   • search_knowledge_base   [OAuth2]          --> No Gate   │
 └──────────────────────────────┬──────────────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │ radar.py Pre-Deployment Scanner   │
              │                                   │
              │  [RULE-01] Mutating without Gate  │
              │  [RULE-02] Missing Auth Type      │
              │  [RULE-03] Static CustomKeys      │
              │  [RULE-04] Missing Audience       │
              │  [RULE-05] PII / Secret Leakage   │
              │  [RULE-06] Wildcard Scope         │
              └───────────────────────────────────┘
```

---

## Official Documentation References
- [Build and register a custom MCP server](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server)
- [Create and manage a toolbox in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)
- [MCP Security Best Practices](https://learn.microsoft.com/en-us/azure/foundry/mcp/security-best-practices)
- [Role-based access control in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry)

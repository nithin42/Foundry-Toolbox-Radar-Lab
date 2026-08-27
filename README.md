# Foundry Toolbox Radar (`foundry-toolbox-radar-lab`)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Community Project](https://img.shields.io/badge/Microsoft%20Foundry-Community%20Lab-orange.svg)](#disclaimer)

> **Pre-deployment governance, identity auditing, prompt injection detection, and data-leakage scanner for Microsoft Foundry Toolboxes and autonomous AI agents.**

---

> [!NOTE]
> ### Disclaimer
> This is an independent open-source community project. It is **not** an official Microsoft repository or supported Microsoft product. All Microsoft Foundry, Azure, and Entra references are grounded in public [Microsoft Learn](https://learn.microsoft.com/en-us/azure/foundry/) documentation.

---

## What is this?

When building autonomous agents in **Microsoft Foundry**, connecting Model Context Protocol (MCP) servers and tools through a **Toolbox** is fast — but under-governed tool configurations introduce severe security risks:
- **Ungated Mutating Actions**: Autonomous agents executing `delete`, `update`, `send`, or `drop` operations without human approval gates.
- **Credential Creep**: Static `CustomKeys` (API keys, PATs) shared across users rather than Microsoft Entra ID token passthrough.
- **Sensitive Data Leakage**: Accidental PII (emails, SSNs, phone numbers) or secret keys embedded in tool descriptions and sample outputs.
- **Scope Inflation**: Wildcards (`*`) or overly broad `.default` permissions granted where granular access is required.
- **Tool-Poisoning & Indirect Prompt Injection**: Malicious instructions or exfiltration directives embedded inside tool docstrings and metadata.

`foundry-toolbox-radar-lab` provides:
1. **`radar` CLI / `radar.py`**: A fast, zero-external-dependency scanner that audits your Microsoft Foundry Toolbox configurations before deployment, outputting human-readable summaries and machine-readable JSON for CI/CD gates.
2. **Reusable GitHub Action & Pre-Commit Hook**: Drop-in CI/CD quality gate for GitHub Actions and local git workflows.
3. **3-Part Hands-on Workshop**: A complete, step-by-step curriculum teaching you how to build, secure, and gate multi-tool agent environments on Microsoft Foundry.

---

## Why I built this

[YOUR STORY HERE — one real sentence about a time an over-permissioned agent tool worried you. Don't let the agent invent this for you.]

---

## Quickstart

### 1. Installation

Clone the repository and install locally:
```bash
git clone https://github.com/nithin42/Foundry-Toolbox-Radar-Lab.git
cd Foundry-Toolbox-Radar-Lab
pip install -e .
```

### 2. Audit a Toolbox Configuration

Run `radar` against any Toolbox YAML file:

```bash
# Scan with human-readable ASCII table
radar tool/tests/fixtures/risky_toolbox.yaml
```

### Sample Output:
```text
================================================================================
 FOUNDRY TOOLBOX RADAR - GOVERNANCE AUDIT REPORT
 Target File: risky_toolbox.yaml
================================================================================
 Total Findings: 12 (HIGH: 8, MEDIUM: 3, LOW: 1)
--------------------------------------------------------------------------------
SEVERITY   | RULE ID   | TOOL NAME          | MESSAGE
--------------------------------------------------------------------------------
[HIGH]     | RULE-01   | delete_database_.. | Tool appears to perform mutating actions but does not enforce human approval (require_approval=False).
  --> Snippet:     name: delete_database_records, require_approval: False
  --> Remediation: Set 'require_approval: true' (or 'always') on mutating tools to prevent unauthorized autonomous actions.
--------------------------------------------------------------------------------
[HIGH]     | RULE-02   | unauthenticated_.. | No authentication type configured for tool/connection. Endpoints may be exposed unauthenticated.
  --> Snippet:     authType: 'None'
  --> Remediation: Specify a supported 'authType' ('UserEntraToken', 'AgenticIdentityToken', 'OAuth2', or 'CustomKeys').
--------------------------------------------------------------------------------
[MEDIUM]   | RULE-03   | legacy_erp_conne.. | Tool uses static 'CustomKeys' authentication (API key/PAT). Shared keys lack user attribution and automatic credential rotation.
  --> Snippet:     authType: CustomKeys
  --> Remediation: Upgrade connection to Microsoft Entra identity ('AgenticIdentityToken' or 'UserEntraToken') or 'OAuth2'.
--------------------------------------------------------------------------------
[MEDIUM]   | RULE-04   | user_delegated_s.. | Tool uses 'UserEntraToken' passthrough but lacks a specific 'audience' App ID URI.
  --> Snippet:     authType: UserEntraToken, audience: None
  --> Remediation: Define a valid Entra App ID URI or Resource ID in 'audience' to avoid token rejection or broad token exchange.
--------------------------------------------------------------------------------
[HIGH]     | RULE-05   | customer_lookup_.. | Potential Email Address detected in 'sample_output'. Risk of sensitive data exposure to LLM context.
  --> Snippet:     alice.smith@executive-corp.com
  --> Remediation: Sanitize or synthesize sample outputs. Replace real PII or secret values with placeholders.
--------------------------------------------------------------------------------
[LOW]      | RULE-06   | broad_cloud_mana.. | Wildcard character '*' detected in target, audience, or scope definition.
  --> Snippet:     https://management.azure.com/.default api://*
  --> Remediation: Specify explicit resource identifiers and endpoints instead of wildcard patterns.
--------------------------------------------------------------------------------
[HIGH]     | RULE-07   | poisoned_search_.. | Potential Instruction Hijacking / Override detected in 'description'. Tool metadata attempts to hijack agent control flow or exfiltrate context.
  --> Snippet:     Ignore previous instructions
  --> Remediation: Remove instruction-override phrases, prompt injection attacks, and exfiltration directives from tool metadata.
--------------------------------------------------------------------------------
================================================================================
 [FAILED] 8 HIGH severity finding(s) detected. Gate blocked.
================================================================================
```

### 3. CI/CD Machine-Readable JSON Mode

Emit JSON for GitHub Actions or Azure DevOps pipelines (exits non-zero on any HIGH finding):
```bash
radar tool/tests/fixtures/clean_toolbox.yaml --json
```

### 4. Use as a GitHub Action

You can also use this repository directly as a GitHub Action in `.github/workflows/audit.yml`:

```yaml
- name: Audit Toolbox Governance
  uses: nithin42/Foundry-Toolbox-Radar-Lab@main
  with:
    config: ./src/toolbox.yaml
    json: false
```

---

## Governance Rules Matrix

| Rule ID | Severity | Description | Trigger Condition |
| :--- | :--- | :--- | :--- |
| **`RULE-01`** | **HIGH** | Mutating Tool Without Approval Gate | Tool name/description indicates mutation (`delete`, `create`, `update`, `send`, `write`, `drop`) without `require_approval: true`. |
| **`RULE-02`** | **HIGH** | Missing / Invalid Authentication Type | `authType` is omitted, `null`, or not a recognized Foundry auth type (`UserEntraToken`, `AgenticIdentityToken`, `OAuth2`, `CustomKeys`). |
| **`RULE-03`** | **MEDIUM** | Static Credential Risk | `authType` uses `CustomKeys` (API keys/PATs) instead of Microsoft Entra ID or OAuth. |
| **`RULE-04`** | **MEDIUM** | Missing Entra Audience | `UserEntraToken` connection lacks a specific App ID URI in `audience`. |
| **`RULE-05`** | **HIGH / MED** | PII & Secret Leakage | Regex scan detects emails, SSNs, phone numbers, or secret tokens. Flagged in `sample_output` (**HIGH**) or `description` (**MEDIUM**). |
| **`RULE-06`** | **LOW** | Overly Broad Scope | Target or audience contains wildcards (`*`) or uses broad `.default` resource scopes. |
| **`RULE-07`** | **HIGH** | Tool Poisoning & Prompt Injection | Tool `description`, `name`, or `sample_output` contains instruction override, jailbreaks, or exfiltration directives. |

---

## Hands-On Workshop Curriculum

| Lab | Guide | Focus Area |
| :--- | :--- | :--- |
| **Lab 01** | [Your First Toolbox](workshop/lab01-first-toolbox/README.md) | Create a managed Toolbox, register the GitHub MCP server, test locally via Streamable HTTP, and verify in the Microsoft Foundry Playground. |
| **Lab 02** | [Multi-Tool Governance](workshop/lab02-multi-tool-governance/README.md) | Build a custom MCP server on Azure Functions, configure Developer/Agent/User RBAC, enforce `require_approval` gates, and audit with `radar.py`. |
| **Lab 03** | [Deploy & Gate](workshop/lab03-deploy-and-gate/README.md) | Deploy hosted agents with `azd` and wire `radar.py` into GitHub Actions as an automated pre-merge quality gate. |

---

## Official Documentation References

- [What is Toolbox in Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/toolbox-overview)
- [Create and manage a toolbox in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)
- [Set up MCP server authentication](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
- [Build and register a custom MCP server](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server)
- [MCP Security Best Practices](https://learn.microsoft.com/en-us/azure/foundry/mcp/security-best-practices)
- [Quickstart: Deploy your first hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)
- [Role-based access control in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry)

---

## License

This project is open source and available under the [MIT License](LICENSE).

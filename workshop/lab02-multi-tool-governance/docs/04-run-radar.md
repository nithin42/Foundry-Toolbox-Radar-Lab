# 04. Audit Toolbox Governance with `radar.py`

In this module, you will export your Microsoft Foundry Toolbox configuration to YAML and execute `radar.py` to audit for security flaws, missing approval gates, and sensitive data leakage.

---

## 1. Exporting Your Toolbox Configuration

Create an exported representation of your enterprise toolbox: `my_enterprise_toolbox.yaml`.

### Initial Non-Compliant State:
```yaml
# my_enterprise_toolbox.yaml
name: enterprise-finance-toolbox
description: Production toolbox for financial operations agent
tools:
  - name: get_customer_summary
    description: Fetch customer summary and account tier
    target: https://ops-mcp-func.azurewebsites.net/api/mcp
    authType: UserEntraToken
    audience: api://custom-mcp-server
    require_approval: false

  # SECURITY FLAW 1: Mutating tool without require_approval gate (HIGH)
  - name: update_credit_limit
    description: Update and modify credit limit for an account
    target: https://ops-mcp-func.azurewebsites.net/api/mcp
    authType: UserEntraToken
    audience: api://custom-mcp-server
    require_approval: false

  # SECURITY FLAW 2: Static credential risk via CustomKeys (MEDIUM)
  - name: legacy_invoice_sync
    description: Sync invoices to on-prem ERP
    target: https://erp.internal.contoso.com/mcp
    authType: CustomKeys
    require_approval: false

  # SECURITY FLAW 3: PII & Token in sample_output (HIGH)
  - name: customer_lookup_sample
    description: Sample customer profile
    target: https://crm.contoso.com/mcp
    authType: AgenticIdentityToken
    audience: api://crm
    require_approval: false
    sample_output:
      support_email: admin-ops@contoso.com
      temp_token: sk-live-98234710293847102938
```

---

## 2. Execute `radar.py` Scan

Run `radar.py` against your toolbox YAML:

```bash
python tool/radar.py my_enterprise_toolbox.yaml
```

### Scan Output:
```text
================================================================================
 FOUNDRY TOOLBOX RADAR - GOVERNANCE AUDIT REPORT
 Target File: my_enterprise_toolbox.yaml
================================================================================
 Total Findings: 4 (HIGH: 3, MEDIUM: 1, LOW: 0)
--------------------------------------------------------------------------------
SEVERITY   | RULE ID   | TOOL NAME          | MESSAGE
--------------------------------------------------------------------------------
[HIGH]     | RULE-01   | update_credit_l..  | Tool appears to perform mutating actions but does not enforce human approval (require_approval=False).
  --> Snippet:     name: update_credit_limit, require_approval: False
  --> Remediation: Set 'require_approval: true' (or 'always') on mutating tools to prevent unauthorized autonomous actions.
--------------------------------------------------------------------------------
[MEDIUM]   | RULE-03   | legacy_invoice_..  | Tool uses static 'CustomKeys' authentication (API key/PAT). Shared keys lack user attribution and automatic credential rotation.
  --> Snippet:     authType: CustomKeys
  --> Remediation: Upgrade connection to Microsoft Entra identity ('AgenticIdentityToken' or 'UserEntraToken') or 'OAuth2'.
--------------------------------------------------------------------------------
[HIGH]     | RULE-05   | customer_lookup..  | Potential Email Address detected in 'sample_output'. Risk of sensitive data exposure to LLM context.
  --> Snippet:     admin-ops@contoso.com
  --> Remediation: Sanitize or synthesize sample outputs. Replace real PII or secret values with placeholders.
--------------------------------------------------------------------------------
[HIGH]     | RULE-05   | customer_lookup..  | Potential AI API Key detected in 'sample_output'. Risk of sensitive data exposure to LLM context.
  --> Snippet:     sk-live-...
  --> Remediation: Sanitize or synthesize sample outputs. Replace real PII or secret values with placeholders.
--------------------------------------------------------------------------------
================================================================================
 [FAILED] 3 HIGH severity finding(s) detected. Gate blocked.
================================================================================
```

Notice the scanner returns **exit code 1**, halting any automated deployment pipeline.

---

## 3. Remediate Findings

Apply the remediations to `my_enterprise_toolbox.yaml`:
1. Enable `require_approval: true` on `update_credit_limit`.
2. Upgrade `legacy_invoice_sync` to `AgenticIdentityToken`.
3. Sanitize `sample_output` to remove real emails and secret keys.

```yaml
# my_enterprise_toolbox.yaml (Remediated)
name: enterprise-finance-toolbox
description: Production toolbox for financial operations agent
tools:
  - name: get_customer_summary
    description: Fetch customer summary and account tier
    target: https://ops-mcp-func.azurewebsites.net/api/mcp
    authType: UserEntraToken
    audience: api://custom-mcp-server
    require_approval: false

  - name: update_credit_limit
    description: Update and modify credit limit for an account
    target: https://ops-mcp-func.azurewebsites.net/api/mcp
    authType: UserEntraToken
    audience: api://custom-mcp-server
    require_approval: true

  - name: legacy_invoice_sync
    description: Sync invoices to on-prem ERP
    target: https://erp.internal.contoso.com/mcp
    authType: AgenticIdentityToken
    audience: api://erp-gateway
    require_approval: false

  - name: customer_lookup_sample
    description: Sample customer profile
    target: https://crm.contoso.com/mcp
    authType: AgenticIdentityToken
    audience: api://crm
    require_approval: false
    sample_output:
      support_tier: Gold
      status: Active
```

Re-run the audit:
```bash
python tool/radar.py my_enterprise_toolbox.yaml
```

### Compliant Result:
```text
================================================================================
 FOUNDRY TOOLBOX RADAR - GOVERNANCE AUDIT REPORT
 Target File: my_enterprise_toolbox.yaml
================================================================================

  [PASS] No governance or data-leakage risks detected.
  Toolbox configuration complies with governance baseline.

================================================================================
```
The audit exits with code `0`.

---

## Next Steps
Proceed to [05. Troubleshooting](05-troubleshooting.md) for debugging multi-tool and authentication edge cases.

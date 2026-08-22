# 03. Troubleshooting Deployments & CI Gates

This guide addresses common errors encountered when deploying hosted agents via `azd` and executing `radar.py` quality gates in GitHub Actions.

---

## 1. `azd` Deployment Errors

### A. Missing `microsoft.foundry` Extension
- **Symptom**: `azd ai: command not found` or `unknown command "ai"`.
- **Cause**: The unified Foundry extension bundle is not installed in the CI runner or local environment.
- **Remediation**:
  Run:
  ```bash
  azd ext install microsoft.foundry
  ```

### B. OIDC Token Exchange Failure in GitHub Actions
- **Symptom**: `Failed to authenticate via OpenID Connect: Federated token exchange failed`.
- **Cause**: Mismatched repository name, branch, or environment in Azure Entra Federated Credential settings.
- **Remediation**:
  Ensure the Microsoft Entra App registration federated credential subject exactly matches:
  `repo:<owner>/<repo>:ref:refs/heads/<branch>` (e.g. `repo:contoso/my-agent:ref:refs/heads/main`).

---

## 2. GitHub Actions CI Gate Errors

### A. Missing YAML Path Triggers
- **Symptom**: Submitting a PR with a modified toolbox YAML does not trigger `radar-gate.yml`.
- **Cause**: The `paths` filter in `.github/workflows/radar-gate.yml` does not match the subfolder path of the changed YAML.
- **Remediation**:
  Use wildcard paths (`"**.yaml"`, `"**.yml"`) or add the explicit directory (e.g. `"src/**"`).

### B. Exit Code Ignored in Custom Runner Script
- **Symptom**: Pipeline succeeds even when `radar.py` prints HIGH severity findings.
- **Cause**: The shell step swallowed the non-zero exit code (e.g. piping to `tee` or formatting without `set -e`).
- **Remediation**:
  Execute `python tool/radar.py <config> --json` directly so the runner terminates immediately on non-zero exit code.

---

## Workshop Completion
Congratulations on completing the entire **Microsoft Foundry Toolbox Radar Lab** series!

You now possess:
1. A fully functioning, governed Microsoft Foundry Toolbox environment.
2. An automated CI/CD governance scanner (`radar.py`) to audit all future AI agent tools.
3. Industry-grade defense-in-depth patterns separating Developer, Agent, and User identities with strict approval boundaries.

# 02. Wire `radar.py` as a GitHub Actions CI Gate

To ensure that security vulnerabilities, unapproved mutating tools, and secret leaks never enter production, `radar.py` must run as an automated quality gate on every Pull Request modifying agent or toolbox definitions.

---

## 1. The GitHub Actions Workflow File

Place the following workflow definition in `.github/workflows/radar-gate.yml`:

```yaml
# .github/workflows/radar-gate.yml
name: Radar Toolbox Governance Gate

on:
  pull_request:
    branches:
      - main
      - dev
    paths:
      - "**.yaml"
      - "**.yml"
      - "tool/**"
      - ".github/workflows/radar-gate.yml"
  push:
    branches:
      - main
      - dev
    paths:
      - "**.yaml"
      - "**.yml"
      - "tool/**"
      - ".github/workflows/radar-gate.yml"

jobs:
  governance-gate:
    name: Audit Toolbox Governance
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
          cache-dependency-path: tool/requirements.txt

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r tool/requirements.txt

      - name: Run Test Suite
        run: |
          python -m pytest tool/tests/test_radar.py -v

      - name: Audit Toolbox Configuration (CI Gate)
        run: |
          echo "Scanning toolbox configuration for governance risks..."
          # Scan your target toolbox YAML (e.g. tool/tests/fixtures/clean_toolbox.yaml or src/toolbox.yaml)
          python tool/radar.py tool/tests/fixtures/clean_toolbox.yaml --json
```

---

## 2. Enforcing Branch Protection Rules

In your GitHub repository settings:
1. Navigate to **Settings** > **Branches** > **Branch protection rules**.
2. Add a rule for `main` and `dev`.
3. Check **Require status checks to pass before merging**.
4. Search for and select: `Audit Toolbox Governance`.
5. Require branches to be up to date before merging.

---

## 3. How the Gate Blocks Vulnerable PRs

When a developer submits a PR containing an insecure change (such as adding a mutating database tool with `require_approval: false` or embedding a secret in `sample_output`):
1. The GitHub Action triggers automatically.
2. `radar.py` detects the HIGH severity issue and prints the finding details and remediation steps.
3. `radar.py` returns **exit code 1**.
4. GitHub marks the check as **FAILED ❌**, preventing the PR from being merged into `main` until the developer remediates the issue.

---

## Next Steps
Proceed to [03. Troubleshooting](03-troubleshooting.md) for CI pipeline troubleshooting and best practices.

# 05. Troubleshooting Multi-Tool Governance & Custom MCP Servers

This document details common failures encountered when deploying custom serverless MCP servers on Azure Functions, managing multi-identity RBAC, and enforcing approval policies.

---

## 1. Custom MCP Server on Azure Functions Failures

### A. HTTP 400 `Invalid JSON-RPC Protocol Payload`
- **Symptom**: Calling custom function app returns `HTTP 400 Bad Request`.
- **Cause**: The FastMCP or custom handler received non-JSON payload or mismatched MCP protocol versions.
- **Remediation**:
  Ensure your Azure Functions HTTP trigger sets `mimetype="application/json"` and returns standard JSON-RPC 2.0 structure (`{"jsonrpc": "2.0", "id": 1, "result": {...}}`).

### B. Streaming / SSE Timeout on Consumption
- **Symptom**: Streamable HTTP connection drops after 30 seconds.
- **Cause**: Azure Functions default request timeout or missing keep-alive headers on SSE connections.
- **Remediation**:
  Configure Server-Sent Events headers:
  ```text
  Content-Type: text/event-stream
  Cache-Control: no-cache
  Connection: keep-alive
  ```

---

## 2. Entra ID & Audience Mismatches

### A. `Cannot pass Microsoft token to untrusted MCP endpoint`
- **Symptom**: Agent Service rejects `UserEntraToken` call with error: `Cannot pass Microsoft token to untrusted MCP endpoint.`
- **Cause**: The custom MCP connection attempted to use a generic Microsoft audience (`https://graph.microsoft.com` or `https://ai.azure.com`) against a third-party or custom endpoint.
- **Remediation**:
  Per [Microsoft Learn MCP Auth Guidance](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication), your custom MCP server must be registered with a distinct App ID URI that you control (e.g. `api://custom-mcp-server`), and configured in the connection's `--audience` parameter.

### B. OAuth Consent Loop (`error.code: -32006`)
- **Symptom**: Tool execution halts with JSON-RPC error code `-32006`.
- **Cause**: The end user has not yet consented to the required OAuth permissions for this tool.
- **Remediation**:
  Extract the `consent_link` from `response.output_item` and present it to the user in your client application. Once consent is granted, resume the execution session.

---

## 3. Human Approval Policy Failures

### A. Agent Bypasses Required Approval
- **Symptom**: A mutating tool executes without halting for approval.
- **Cause**: `require_approval` was omitted, set to `never`, or placed on the wrong tool object in `tools`.
- **Remediation**:
  Always audit with `radar.py` before deployment. Ensure `require_approval: true` is explicitly declared on every tool that mutates state or external data.

---

## Summary & Next Lab
Congratulations! You have completed **Lab 02**. You have mastered multi-tool architecture, custom MCP servers on Azure Functions, enterprise RBAC segregation, and live governance auditing with `radar.py`.

Next, proceed to **[Lab 03: Deploy and Gate](../../lab03-deploy-and-gate/README.md)** to automate governance scanning as a GitHub Actions CI/CD gate.

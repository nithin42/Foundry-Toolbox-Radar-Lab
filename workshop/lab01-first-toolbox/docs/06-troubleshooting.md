# 06. Troubleshooting & Diagnostics

This reference covers the most frequent issues encountered when configuring Microsoft Foundry Toolboxes, registering MCP connections, and calling tools over Streamable HTTP.

---

## 1. Authentication & Permission Errors

### A. HTTP 401 Unauthorized / Token Rejection
- **Symptom**: Calling the Toolbox MCP endpoint returns `HTTP 401 Unauthorized`.
- **Cause**: Incorrect token scope used when acquiring Bearer token with `DefaultAzureCredential`.
- **Remediation**:
  Ensure your Python or CLI client requests the exact scope:
  ```python
  token = DefaultAzureCredential().get_token("https://ai.azure.com/.default").token
  ```
  Do not use `https://management.azure.com/.default` for Toolbox data plane invocations.

### B. HTTP 403 Forbidden / Role Missing
- **Symptom**: `Caller does not have required permissions on Foundry Project`.
- **Cause**: Missing RBAC assignment.
- **Remediation**:
  Assign the **Foundry User** role on the Foundry project to your developer account or agent identity:
  ```bash
  az role assignment create \
    --assignee "<your-user-principal-id>" \
    --role "Foundry User" \
    --scope "<foundry-project-resource-id>"
  ```

---

## 2. MCP Transport & Protocol Failures

### A. MCP Protocol Handshake Error: `Session not initialized`
- **Symptom**: Calls to `tools/list` or `tools/call` fail with error code `-32600` or `SessionNotInitialized`.
- **Cause**: In the Model Context Protocol, clients must send an `initialize` request followed by a `notifications/initialized` message before making tool calls.
- **Remediation**: Use the official `mcp.ClientSession` which handles initialization lifecycle automatically:
  ```python
  async with streamablehttp_client(url, headers=headers) as (read, write, _):
      async with ClientSession(read, write) as session:
          await session.initialize()
          # Ready for tools/list
  ```

### B. Connection Record Not Found (`project_connection_id`)
- **Symptom**: Toolbox version creation fails with `ConnectionNotFound: Connection 'github-conn' does not exist`.
- **Cause**: The project connection referenced in `connections` or `project_connection_id` must exist in the same Foundry project before publishing the toolbox version.
- **Remediation**:
  Check registered connections with:
  ```bash
  azd ai connection list
  ```
  Create the connection first before publishing the toolbox.

---

## 3. Remote Tool Errors (GitHub MCP)

### A. GitHub 401 Bad Credentials / Rate Limit
- **Symptom**: Tool execution returns `ServerError: Bad credentials` from GitHub.
- **Cause**: The GitHub PAT configured in `github-conn` is expired, has insufficient scopes, or exceeded GitHub API rate limits.
- **Remediation**:
  Re-generate a GitHub Personal Access Token with `repo` read permissions and update the connection:
  ```bash
  azd ai connection create github-conn \
    --kind remote-tool \
    --target https://api.githubcopilot.com/mcp/ \
    --auth-type custom-keys \
    --custom-key "Authorization=Bearer $NEW_GITHUB_PAT"
  ```

---

## 4. Verification Diagnostic Checklist

- [ ] Active project endpoint format is valid: `https://<account>.services.ai.azure.com/api/projects/<proj>`.
- [ ] User or Agent identity has `Foundry User` role.
- [ ] Bearer token generated with scope `https://ai.azure.com/.default`.
- [ ] `azd ai connection list` displays all referenced connections.
- [ ] MCP initialize handshake returns HTTP 200.

---

## Summary & Next Lab
Congratulations! You have completed **Lab 01**. You now have a working Microsoft Foundry Toolbox connected to a remote MCP server.

Next, proceed to **[Lab 02: Multi-Tool Governance](../../lab02-multi-tool-governance/README.md)** to add custom MCP servers over Azure Functions, configure RBAC policies, and audit configurations using `radar.py`.

# 02. Build & Register a Custom MCP Server on Azure Functions

While pre-built catalog tools provide generic capabilities, enterprise agents require access to proprietary internal APIs (e.g. ERP systems, ticketing platforms, or database mutators).

In this module, you will build a custom **Python Serverless MCP Server** hosted on **Azure Functions (v4 model)** and secured with Microsoft Entra ID.

---

## 1. Project Structure

Initialize an Azure Functions Python project:
```bash
mkdir custom-mcp-server && cd custom-mcp-server
func init . --python -m V2
```

Create `requirements.txt`:
```text
azure-functions
mcp>=1.0.0
pydantic>=2.0.0
```

---

## 2. MCP Server Implementation: `function_app.py`

Create `function_app.py` implementing an HTTP-triggered MCP server endpoint supporting Streamable HTTP / Server-Sent Events (SSE):

```python
"""Custom Enterprise MCP Server on Azure Functions."""

import json
import logging
import azure.functions as func
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP instance
mcp = FastMCP("enterprise-operations-server")


@mcp.tool(description="Read customer financial health score and active subscription summary.")
def get_customer_summary(customer_id: str) -> dict:
    """Fetch customer summary by ID."""
    logging.info(f"Executing get_customer_summary for ID: {customer_id}")
    # In production, query your CRM database or API
    return {
        "customer_id": customer_id,
        "health_score": 92,
        "plan": "Enterprise Scale",
        "renewal_date": "2027-01-15",
    }


@mcp.tool(description="Update credit limit for a corporate customer account. Modifies billing data.")
def update_credit_limit(customer_id: str, new_limit_usd: float) -> dict:
    """Mutating tool: updates credit limit."""
    logging.info(f"Executing mutating action update_credit_limit for ID: {customer_id}")
    return {
        "customer_id": customer_id,
        "new_limit_usd": new_limit_usd,
        "status": "APPROVED",
        "audit_id": "AUD-88219",
    }


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="mcp", methods=["GET", "POST"])
async def mcp_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions handler exposing the MCP streamable transport."""
    logging.info("Incoming MCP request received.")

    # In production, validate Microsoft Entra Bearer token from req.headers.get("Authorization")
    # against audience 'api://custom-mcp-server'.

    # Return MCP server capability response or stream
    return func.HttpResponse(
        body=json.dumps({"status": "healthy", "server": "enterprise-operations-server"}),
        status_code=200,
        mimetype="application/json",
    )
```

---

## 3. Registering in Azure API Center & Microsoft Foundry

Per the documented pattern in [Microsoft Learn: Build and register a custom MCP server](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server):

1. **Deploy to Azure Functions**: Deploy your function app to Azure (e.g. `https://ops-mcp-func.azurewebsites.net/api/mcp`).
2. **Register Entra App Registration**:
   - Create App Registration `custom-mcp-server`.
   - Set Application ID URI: `api://custom-mcp-server`.
   - Expose scope: `api://custom-mcp-server/Tools.Invoke`.
3. **Register Project Connection in Foundry**:
   ```bash
   azd ai connection create custom-ops-conn \
     --kind remote-tool \
     --target https://ops-mcp-func.azurewebsites.net/api/mcp \
     --auth-type user-entra-token \
     --audience api://custom-mcp-server
   ```

---

## Next Steps
Proceed to [03. RBAC & Approval Policy](03-rbac-and-approval-policy.md) to configure role-based access control and approval gates.

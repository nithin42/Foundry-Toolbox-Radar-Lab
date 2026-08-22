# 04. Test Toolbox Locally via MCP Client SDK

Before wiring a toolbox to an autonomous agent, you should verify that the toolbox MCP endpoint initializes correctly, resolves its downstream connections, and lists all exposed tools.

In this step, you will use the official Python `mcp` SDK to connect to your Foundry Toolbox over Streamable HTTP.

---

## 1. Authentication Token Scope

Calls to the Microsoft Foundry Toolbox MCP endpoint require an Entra ID Bearer token with the scope:
```text
https://ai.azure.com/.default
```

---

## 2. Test Script: `verify_toolbox.py`

Create a file named `verify_toolbox.py`:

```python
"""Local test script to verify Foundry Toolbox MCP endpoint availability."""

import asyncio
import os
import sys
from azure.identity import DefaultAzureCredential
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# 1. Resolve configuration from environment
project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
toolbox_name = os.getenv("TOOLBOX_NAME", "first-toolbox")

if not project_endpoint:
    print("Error: FOUNDRY_PROJECT_ENDPOINT environment variable not set.", file=sys.stderr)
    sys.exit(1)

# Construct Toolbox consumer endpoint
toolbox_url = f"{project_endpoint}/toolboxes/{toolbox_name}/mcp?api-version=v1"

# 2. Acquire Entra ID token
credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default").token
headers = {"Authorization": f"Bearer {token}"}


async def main() -> None:
    print(f"Connecting to Toolbox endpoint: {toolbox_url}\n")

    # 3. Establish Streamable HTTP MCP Session
    async with streamablehttp_client(toolbox_url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            # 4. Initialize session
            init_result = await session.initialize()
            print(f"[OK] MCP Session Initialized (Protocol: {init_result.protocolVersion})")

            # 5. List available tools exposed by the toolbox
            tools_response = await session.list_tools()
            tools = tools_response.tools
            print(f"[OK] Found {len(tools)} tools in toolbox:\n")

            for t in tools:
                desc = (t.description or "").replace("\n", " ")[:80]
                print(f"  • Tool: {t.name:<30} | {desc}")

            # 6. Optional: Execute a read tool (e.g. GitHub repo search)
            # result = await session.call_tool("github.search_repositories", arguments={"query": "foundry"})
            # print("\nSample Tool Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. Execute the Verification Script

Run the script from your terminal:
```bash
python verify_toolbox.py
```

### Expected Output:
```text
Connecting to Toolbox endpoint: https://my-account.services.ai.azure.com/api/projects/my-proj/toolboxes/first-toolbox/mcp?api-version=v1

[OK] MCP Session Initialized (Protocol: 2025-03-26)
[OK] Found 8 tools in toolbox:

  • Tool: web_search                     | Search the web for current information and news
  • Tool: toolbox_search                 | Search across available tools in the toolbox
  • Tool: github.search_repositories     | Search for GitHub repositories by keywords
  • Tool: github.list_issues             | List issues in a target GitHub repository
  • Tool: github.get_file_contents       | Read file contents from a repository
```

---

## Next Steps
Proceed to [05. Verify in Playground](05-verify-in-playground.md) to attach your toolbox to a hosted prompt agent in Microsoft Foundry.

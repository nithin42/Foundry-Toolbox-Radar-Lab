# Lab 01: Your First Microsoft Foundry Toolbox

Welcome to **Lab 01** of the Microsoft Foundry Toolbox Radar series. In this hands-on workshop, you will configure your first managed **Toolbox** in Microsoft Foundry, connect a remote Model Context Protocol (MCP) server, and verify end-to-end tool execution both locally via the MCP Python SDK and through the Microsoft Foundry Playground.

---

## Lab Objectives

By the end of this lab, you will:
1. Understand the architecture of Microsoft Foundry Toolbox as a managed MCP gateway.
2. Configure project-level connections with Microsoft Entra ID and credential management.
3. Author and publish a versioned Toolbox configuration using both the Azure Developer CLI (`azd`) and the Python SDK (`azure-ai-projects`).
4. Connect the remote **GitHub MCP server** to your toolbox.
5. Programmatically test and discover tools using the streamable HTTP MCP transport.
6. Attach the toolbox to a hosted prompt agent in Microsoft Foundry and verify live agent tool invocation.

---

## Lab Modules

| Step | Document | Description |
| :--- | :--- | :--- |
| **00** | [00. Prerequisites](docs/00-prerequisites.md) | Required Azure subscriptions, CLI tools, VS Code extensions, and permissions. |
| **01** | [01. Setup](docs/01-setup.md) | Configure your Foundry project environment, endpoints, and credentials. |
| **02** | [02. Create Toolbox](docs/02-create-toolbox.md) | Define and publish a managed Toolbox version with tool routing capabilities. |
| **03** | [03. Connect First Tool](docs/03-connect-first-tool.md) | Register the GitHub MCP server as a project connection and wire it to your toolbox. |
| **04** | [04. Test Locally](docs/04-test-locally.md) | Connect directly to the Toolbox MCP endpoint using Python and inspect tool catalogs. |
| **05** | [05. Verify in Playground](docs/05-verify-in-playground.md) | Wire your toolbox to a hosted prompt agent and test natural-language tool routing. |
| **06** | [06. Troubleshooting](docs/06-troubleshooting.md) | Diagnostic workflows, common MCP transport errors, and token scope remediation. |

---

## Architecture Overview

```
 ┌────────────────────────────────────────────────────────┐
 │ Microsoft Foundry Project                              │
 │                                                        │
 │  ┌──────────────────────────────────────────────────┐  │
 │  │ Managed Toolbox Endpoint                         │  │
 │  │ /toolboxes/{name}/mcp?api-version=v1             │  │
 │  │                                                  │  │
 │  │  • Centralized Token & Key Injection             │  │
 │  │  • Tool Search & Intent Routing                  │  │
 │  │  • Tool Call Approval Policy Enforcement         │  │
 │  └────────────────────────┬─────────────────────────┘  │
 │                           │                            │
 └───────────────────────────┼────────────────────────────┘
                             │
                  Streamable HTTP / SSE
                             │
                             ▼
              ┌─────────────────────────────┐
              │ GitHub Remote MCP Server    │
              │ https://api.githubcopilot.com│
              └─────────────────────────────┘
```

---

## Official Documentation References
- [What is Toolbox in Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/toolbox-overview)
- [Create and manage a toolbox in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)
- [Set up MCP server authentication](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
- [Quickstart: Deploy your first hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)

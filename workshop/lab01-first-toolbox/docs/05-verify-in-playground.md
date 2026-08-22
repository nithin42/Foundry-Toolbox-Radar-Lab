# 05. Verify in Microsoft Foundry Playground

In this module, you will attach your managed Toolbox to a prompt agent and verify that the language model can naturally discover, select, and invoke tools from your toolbox in the Microsoft Foundry Playground.

---

## 1. Option A: Configure in Microsoft Foundry Portal

1. Open the [Microsoft Foundry portal](https://ai.azure.com) and navigate to your project.
2. Select **Agents** in the left navigation and click **+ Create Agent** (or select an existing agent).
3. Under the **Tools** section on the Agent setup blade:
   - Click **+ Add tool** > **Toolbox**.
   - Select `first-toolbox` from your project's toolbox catalog.
   - Set the agent model deployment (e.g. `gpt-4o`).
4. In the **Instructions** prompt box, specify:
   ```text
   You are an engineering assistant with access to GitHub and Web Search tools through your toolbox.
   Use the GitHub tools to answer questions about repository contents, issues, and code.
   ```
5. Click **Save** and launch the **Playground** chat window.

---

## 2. Option B: Configure via Python Agent Client

You can also run an agent session using the `azure-ai-projects` SDK:

```python
# test_agent.py
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Create or reference prompt agent
agent = project.agents.create_agent(
    model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o"),
    name="toolbox-dev-agent",
    instructions="You are a developer assistant. Use available toolbox tools to fetch GitHub data.",
    toolset=[
        {
            "type": "toolbox",
            "toolbox_name": "first-toolbox",
        }
    ],
)

print(f"Agent created: {agent.id}")

# Create thread and post question
thread = project.agents.create_thread()
message = project.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="What are the latest open issues in the Azure/azure-sdk-for-python repository?",
)

# Run agent
run = project.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
print(f"Run Status: {run.status}")

# Fetch responses
messages = project.agents.list_messages(thread_id=thread.id)
for m in messages.data:
    if m.role == "assistant":
        print("\nAgent Response:\n", m.content[0].text.value)
```

---

## 3. Verifying Tool Execution

When you ask the agent a question requiring external data:
- The model invokes `github.list_issues` with parameters `{"owner": "Azure", "repo": "azure-sdk-for-python"}`.
- Foundry Agent Service intercepts the tool call, securely attaches the GitHub credential stored in `github-conn`, forwards the call to the remote MCP server, and returns the results to the model context.
- The model synthesizes the answer grounded in the real-time GitHub data.

---

## Next Steps
Proceed to [06. Troubleshooting](06-troubleshooting.md) for solutions to common connectivity and permission issues.

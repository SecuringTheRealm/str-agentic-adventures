# Agent Framework Patterns

## Singleton Client
```python
from backend.app.azure_openai_client import azure_openai_client

if not azure_openai_client.is_configured():
    # Return deterministic fallback — never raise
    return fallback_response()
```

## Creating an Agent
```python
from backend.app.agent_framework_base import agent_framework_manager

agent = await agent_framework_manager.create_agent(
    name="my-agent",
    instructions="...",
    model=config.azure_openai_chat_deployment,
    tools=[tool],
    temperature=0.7,
)
```
Store the returned agent reference; reuse it across requests rather than creating a new one each time.

## Thread Management
```python
thread = await agent_framework_manager.create_thread()
# Pass thread.id to subsequent agent interactions to maintain context
```

## Tool Registration
```python
tool = agent_framework_manager.create_function_tool(
    fn=my_callable,
    description="Clear description of what the tool does",
)
```
All tool parameters must be typed; include a description string.

## Error Handling
Wrap every Azure SDK call in `try/except`. Log with context; surface user-friendly messages.

## Testing
Mock `azure_openai_client` in unit tests. Test both the Azure-configured path and the fallback path.

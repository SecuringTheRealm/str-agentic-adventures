# Migration Guide: Semantic Kernel to Azure AI Agents SDK

This guide documents the migration from Microsoft Semantic Kernel to Azure AI Agents SDK, completed as part of ADR-0018.

## Overview

The project has migrated from Semantic Kernel to the Azure AI Agents SDK for production-grade agent orchestration. This change provides:
- Better integration with Azure AI Foundry
- Built-in OpenTelemetry observability
- Managed identity authentication support
- Clearer separation of deterministic and non-deterministic workflows
- Long-term compatibility with Microsoft's AI platform strategy

## Key Changes

### Dependencies

**Removed:**
- `semantic-kernel>=1.0,<2.0`

**Added:**
- `azure-ai-agents>=1.0.0` - Agent framework
- `azure-ai-projects>=1.0.0` - Azure AI Foundry integration
- `azure-ai-inference>=1.0.0b1` - Chat completions
- `opentelemetry-api>=1.20.0` - Observability
- `opentelemetry-sdk>=1.20.0` - Observability SDK
- `pydantic-settings>=2.0.0` - Configuration management

### Code Changes

#### Agent Client Setup

**Before (kernel_setup.py):**
```python
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = Kernel()
chat_service = AzureChatCompletion(...)
kernel.add_service(chat_service)
```

**After (agent_client_setup.py):**
```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.agents import AgentsClient

chat_client = ChatCompletionsClient(
    endpoint=settings.azure_openai_endpoint,
    credential=AzureKeyCredential(settings.azure_openai_api_key),
)
```

#### Agent Initialization

**Before:**
```python
from app.kernel_setup import kernel_manager

self.kernel = kernel_manager.get_kernel()
self.chat_service = self.kernel.get_service(type=AzureChatCompletion)
```

**After:**
```python
from app.agent_client_setup import agent_client_manager

self.chat_client = agent_client_manager.get_chat_client()
```

#### Chat Completions

**Before:**
```python
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings

chat_history = ChatHistory()
chat_history.add_system_message(prompt)
chat_history.add_user_message(message)

settings = PromptExecutionSettings(temperature=0.7, max_tokens=500)
response = await self.chat_service.get_chat_message_contents(
    chat_history=chat_history,
    settings=settings
)
```

**After:**
```python
from azure.ai.inference.models import SystemMessage, UserMessage

messages = [
    SystemMessage(content=prompt),
    UserMessage(content=message),
]

response = await self.chat_client.complete(
    messages=messages,
    model=settings.azure_openai_chat_deployment,
    temperature=0.7,
    max_tokens=500,
)
```

#### Streaming Responses

**Before:**
```python
async for chunk_list in self.chat_service.get_streaming_chat_message_contents(
    chat_history=chat_history,
    settings=settings
):
    for chunk in chunk_list:
        chunk_text = str(chunk)
```

**After:**
```python
response = await self.chat_client.complete(
    messages=messages,
    model=settings.azure_openai_chat_deployment,
    stream=True,
)

async for chunk in response:
    if chunk.choices:
        delta = chunk.choices[0].delta
        if delta.content:
            chunk_text = delta.content
```

#### Plugin/Tool Migration

**Before:**
```python
from semantic_kernel.functions import kernel_function

@kernel_function(
    description="Roll dice",
    name="roll_dice"
)
def roll_dice(notation: str) -> str:
    return dice_roll(notation)

# Register with kernel
kernel.add_plugin(plugin_instance, "PluginName")
```

**After:**
```python
# Plugins now used as direct method calls
class DicePlugin:
    def roll_dice(self, notation: str) -> str:
        """Roll dice based on notation."""
        return dice_roll(notation)

# Store reference for direct access
self.dice_plugin = DicePlugin()

# Call directly when needed
result = self.dice_plugin.roll_dice("2d6+3")
```

## Configuration Changes

### Removed Settings

- `semantic_kernel_debug` - No longer needed

### Environment Variables

All existing Azure OpenAI environment variables remain the same:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_DALLE_DEPLOYMENT`

## Testing Changes

### Mocking Strategy

**Before:**
```python
from unittest.mock import Mock, patch

with patch('app.kernel_setup.kernel_manager.get_kernel') as mock_kernel:
    mock_kernel.return_value = Mock()
```

**After:**
```python
from unittest.mock import Mock, patch

with patch('app.agent_client_setup.agent_client_manager.get_chat_client') as mock_client:
    mock_client.return_value = Mock()
```

## Observability

The new SDK includes built-in OpenTelemetry support:

```python
from app.agent_client_setup import agent_client_manager

# Get tracer for agent operations
tracer = agent_client_manager.get_tracer()

# Use in agent methods
with tracer.start_as_current_span("agent_operation") as span:
    span.set_attribute("operation", "process_input")
    result = await process_input(user_input)
```

## Deterministic vs Non-Deterministic Patterns

The new architecture makes clearer distinctions:

### Deterministic Operations
- Dice rolls
- Combat calculations
- Rules enforcement
- Character state updates

**Implementation:** Direct Python functions, no LLM involvement

### Non-Deterministic Operations  
- Narrative generation
- NPC dialogue
- Scene descriptions
- Quest creation

**Implementation:** Azure AI Inference ChatCompletions

## Troubleshooting

### Import Errors

**Problem:** `ImportError: cannot import name 'AIAgentsClient'`
**Solution:** The correct class name is `AgentsClient`, not `AIAgentsClient`

**Problem:** `ModuleNotFoundError: No module named 'semantic_kernel'`
**Solution:** This is expected - semantic-kernel has been removed. Update imports to use Azure AI SDK.

### Runtime Errors

**Problem:** Agent fails to initialize
**Solution:** Check that all Azure environment variables are set correctly. The agent will operate in fallback mode if configuration is missing.

**Problem:** Chat completions fail
**Solution:** Verify `AZURE_OPENAI_CHAT_DEPLOYMENT` matches your actual deployment name in Azure AI Foundry.

## Migration Checklist

For developers updating custom code:

- [ ] Update imports from `semantic_kernel` to `azure.ai.inference` and `azure.ai.agents`
- [ ] Replace `kernel_manager.get_kernel()` with `agent_client_manager.get_chat_client()`
- [ ] Update chat completion calls to use new message format
- [ ] Convert plugin registrations to direct method calls
- [ ] Update test mocks for new SDK
- [ ] Remove references to `ChatHistory` and `PromptExecutionSettings`
- [ ] Update streaming response handling
- [ ] Test agent initialization in both normal and fallback modes

## Additional Resources

- [Azure AI Agents SDK Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)
- [Azure AI Inference SDK Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-inference-readme)
- [Azure AI Foundry Overview](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview)
- [ADR-0018: Adopt Azure AI Agents SDK](../adr/0018-azure-ai-agents-sdk-adoption.md)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)

## Support

For questions or issues related to the migration:
1. Check the [ADR-0018](../adr/0018-azure-ai-agents-sdk-adoption.md) for rationale and design decisions
2. Review agent implementation examples in `backend/app/agents/`
3. Check plugin patterns in `backend/app/plugins/`
4. Open an issue in the repository for assistance

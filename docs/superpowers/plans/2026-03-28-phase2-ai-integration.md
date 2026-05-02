# Phase 2: AI Integration - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Get the Agent Framework SDK working properly so the game uses real AI instead of stubs.

**Architecture:** Two sequential worktree-isolated agents. `sdk-wiring` fixes the SDK infrastructure, then `streaming-persistence` fixes the streaming path and agent fallbacks.

**Tech Stack:** Python/FastAPI, azure-ai-agents SDK, AsyncToolSet/AsyncFunctionTool, SQLAlchemy

**Prerequisite:** Phase 1 merged. Azure AI Foundry endpoint deployed with gpt-4.1-mini.

---

## Agent 1: `sdk-wiring` (runs first)

### Task 1: Fix fallback mode wiring mismatch (#700)

**Files:**
- Modify: `backend/app/azure_openai_client.py:146-153`

- [ ] **Step 1: Read both is_configured checks**

Read `backend/app/config.py:62-73` and `backend/app/azure_openai_client.py:146-153`. The mismatch: `Settings.is_azure_openai_configured()` checks endpoint + chat deployment + embedding deployment. `AzureOpenAIClient.is_configured()` only checks endpoint + chat deployment.

- [ ] **Step 2: Align the checks**

In `backend/app/azure_openai_client.py`, replace lines 146-153:

```python
def is_configured(self) -> bool:
    """Return True if Azure OpenAI is configured."""
    return bool(settings.azure_openai_endpoint) and bool(
        settings.azure_openai_chat_deployment
    )
```

With:

```python
def is_configured(self) -> bool:
    """Return True if Azure OpenAI is configured."""
    return settings.is_azure_openai_configured()
```

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`

- [ ] **Step 4: Commit**

```bash
git add backend/app/azure_openai_client.py
git commit -m "fix: align AzureOpenAIClient.is_configured() with Settings check (closes #700)"
```

---

### Task 2: Add requires_action and terminal status handling (#642)

**Files:**
- Modify: `backend/app/agent_client_setup.py:213-228, 268-269`

- [ ] **Step 1: Read create_and_process_run methods**

Read `backend/app/agent_client_setup.py` lines 200-280 to understand both `create_and_process_run` and `create_thread_and_process_run`.

- [ ] **Step 2: Add comprehensive status handling**

In `create_and_process_run()` (around line 213), replace the simple `if run.status == "failed"` check with:

```python
run = await client.runs.create_and_process(
    thread_id=thread_id,
    agent_id=agent_id,
)

if run.status == "failed":
    logger.warning("SDK run failed: %s", run.last_error)
    return None
if run.status in ("expired", "cancelled", "incomplete"):
    logger.warning("SDK run ended with status: %s", run.status)
    return None
if run.status == "requires_action":
    logger.warning("SDK run requires_action but auto-execution not enabled")
    return None
```

Apply the same pattern to `create_thread_and_process_run()` (around line 268).

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`

- [ ] **Step 4: Commit**

```bash
git add backend/app/agent_client_setup.py
git commit -m "fix: handle requires_action, expired, cancelled run statuses (closes #642)"
```

---

### Task 3: Add agent cleanup on shutdown (#643)

**Files:**
- Modify: `backend/app/agent_client_setup.py` (add cleanup method)
- Modify: `backend/app/main.py:69-89` (add shutdown hook)

- [ ] **Step 1: Add cleanup method to AgentClientManager**

In `backend/app/agent_client_setup.py`, add a method to the `AgentClientManager` class:

```python
async def cleanup(self) -> None:
    """Delete all created SDK agents on shutdown."""
    if self._fallback_mode or not self._agents_client:
        return
    for agent_id in list(self._created_agent_ids):
        try:
            await self._agents_client.delete_agent(agent_id)
            logger.info("Deleted SDK agent: %s", agent_id)
        except Exception as e:
            logger.warning("Failed to delete SDK agent %s: %s", agent_id, e)
    self._created_agent_ids.clear()
```

Also track created agent IDs - add `self._created_agent_ids: list[str] = []` to `__init__` and append in `create_agent()`.

- [ ] **Step 2: Add shutdown hook to main.py**

In `backend/app/main.py`, in the lifespan function after `yield`:

```python
    yield

    # Shutdown - clean up SDK agents
    logger.info("Cleaning up SDK agents...")
    from app.agent_client_setup import agent_client_manager
    await agent_client_manager.cleanup()
    logger.info("Application shutdown complete.")
```

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`

- [ ] **Step 4: Commit**

```bash
git add backend/app/agent_client_setup.py backend/app/main.py
git commit -m "fix: add SDK agent cleanup on application shutdown (closes #643)"
```

---

### Task 4: Migrate to AsyncToolSet with auto-execution (#641, #644)

**Files:**
- Modify: `backend/app/agent_client_setup.py` (create_agent signature)
- Modify: `backend/app/agents/base_agent.py` (_ensure_agent_created)
- Modify: `backend/app/agents/dungeon_master_agent.py` (tool definitions)
- Modify: `backend/app/agents/narrator_agent.py` (tool definitions)
- Modify: `backend/app/agents/combat_mc_agent.py` (tool definitions)
- Modify: `backend/app/agents/scribe_agent.py` (tool definitions)

- [ ] **Step 1: Read the current tool definition pattern**

Read `backend/app/agents/dungeon_master_agent.py` lines 17-82 to see how `FunctionToolDefinition` is used. Read `backend/app/agents/base_agent.py` lines 120-135 to see how tools are passed to `create_agent`.

- [ ] **Step 2: Update agent_client_setup.py to accept toolset**

In `backend/app/agent_client_setup.py`, update the `create_agent` method signature and add `enable_auto_function_calls`:

```python
async def create_agent(
    self,
    name: str,
    instructions: str,
    toolset: "ToolSet | None" = None,
) -> str | None:
    """Create an SDK agent with optional toolset for auto-execution."""
    try:
        client = await self._get_agents_client()
        if client is None:
            return None

        if toolset:
            client.enable_auto_function_calls(toolset)

        agent = await client.create_agent(
            model=model,
            name=name,
            instructions=instructions,
            toolset=toolset,
        )
        self._created_agent_ids.append(agent.id)
        return agent.id
    except Exception as e:
        logger.error("Failed to create SDK agent: %s", e)
        return None
```

- [ ] **Step 3: Update base_agent.py to build toolset**

In `backend/app/agents/base_agent.py`, update `_ensure_agent_created` to build a `ToolSet` from the tools:

```python
from azure.ai.agents.models import AsyncFunctionTool, AsyncToolSet

async def _ensure_agent_created(self) -> str | None:
    """Create the SDK agent if not already created."""
    if self._sdk_agent_id:
        return self._sdk_agent_id

    tools = self._get_sdk_tools()
    toolset = None
    if tools:
        toolset = AsyncToolSet()
        toolset.add(AsyncFunctionTool(tools))

    result = await agent_client_manager.create_agent(
        name=self.agent_name,
        instructions=self._get_sdk_instructions(),
        toolset=toolset,
    )
    self._sdk_agent_id = result
    return result
```

- [ ] **Step 4: Update tool definitions in all agents**

Each agent's `_get_sdk_tools()` currently returns `list[FunctionToolDefinition]`. These need to return callable functions that `AsyncFunctionTool` can wrap.

For `dungeon_master_agent.py`, convert the tool definitions to actual Python functions:

```python
def _get_sdk_tools(self) -> list:
    """Return tool functions for the SDK to auto-execute."""
    from app.plugins.rules_engine_plugin import RulesEnginePlugin
    rules = RulesEnginePlugin()

    def roll_dice(notation: str, reason: str = "") -> dict:
        """Roll dice using D&D notation (e.g., '1d20', '2d6+3')."""
        return rules.roll_dice(notation)

    def ability_check(character_id: str, ability: str, dc: int) -> dict:
        """Perform an ability check for a character."""
        return rules.roll_dice("1d20")

    return [roll_dice, ability_check]
```

Apply similar patterns to narrator, combat_mc, and scribe agents. Read each agent's tool definitions and convert them to callable functions.

- [ ] **Step 5: Remove old FunctionToolDefinition imports**

Remove `from azure.ai.agents.models import FunctionDefinition, FunctionToolDefinition` from all agent files.

- [ ] **Step 6: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All pass. May need to update mocks that expect the old tool format.

- [ ] **Step 7: Commit**

```bash
git add backend/app/agent_client_setup.py backend/app/agents/
git commit -m "feat: migrate to AsyncToolSet with enable_auto_function_calls (closes #641, closes #644)"
```

---

## Agent 2: `streaming-persistence` (runs after sdk-wiring)

### Task 5: Add fallback warning markers to Narrator and Combat MC (#647)

**Files:**
- Modify: `backend/app/agents/narrator_agent.py`
- Modify: `backend/app/agents/combat_mc_agent.py`

- [ ] **Step 1: Add warning prefix to Narrator fallbacks**

In `backend/app/agents/narrator_agent.py`, find all fallback return points and add the prefix. Key locations:

Line ~149 (describe_scene fallback):
```python
if self._fallback_mode or not self.azure_client:
    return "[AI model not configured] " + fallback_description
```

Lines 677-745 (_fallback_opening_narrative): Add prefix to all hook strings:
```python
hooks: dict[str, str] = {
    "heroic": (
        f"[AI model not configured] A desperate messenger has arrived..."
    ),
    # ... prefix all others
}
```

- [ ] **Step 2: Add warning prefix to Combat MC fallbacks**

In `backend/app/agents/combat_mc_agent.py`, lines 426-502. Add prefix to all fallback messages:

```python
result.update({
    "success": True,
    "message": f"[AI model not configured] Attack hits for {damage_result['total']} damage!",
})
```

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`

- [ ] **Step 4: Commit**

```bash
git add backend/app/agents/narrator_agent.py backend/app/agents/combat_mc_agent.py
git commit -m "fix: add [AI model not configured] prefix to narrator and combat fallbacks (closes #647)"
```

---

### Task 6: Fix fallback streaming persistence (#646)

**Files:**
- Modify: `backend/app/agents/dungeon_master_agent.py:407-408`

- [ ] **Step 1: Read the fallback streaming path**

Read `backend/app/agents/dungeon_master_agent.py` lines 400-415.

- [ ] **Step 2: Add persistence after fallback streaming**

The fallback path returns early without persisting. Fix by adding persistence after the fallback call:

```python
if self._fallback_mode:
    await self._process_input_stream_fallback(user_input, context)
    self._persist_thread(session_id)
    return
```

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`

- [ ] **Step 4: Commit**

```bash
git add backend/app/agents/dungeon_master_agent.py
git commit -m "fix: persist conversation thread after fallback streaming (closes #646)"
```

---

### Task 7: Persist SDK thread IDs to database (#702)

**Files:**
- Modify: `backend/app/agents/base_agent.py:137-152`
- Modify: `backend/app/agents/dungeon_master_agent.py:177-186`

- [ ] **Step 1: Read current thread creation code**

Read `backend/app/agents/base_agent.py` lines 137-152 (`_get_or_create_sdk_thread`) and `backend/app/agents/dungeon_master_agent.py` lines 170-190 (DM thread creation).

- [ ] **Step 2: Persist SDK thread ID when creating threads**

In `base_agent.py`, update `_get_or_create_sdk_thread` to persist the thread ID to the database:

```python
async def _get_or_create_sdk_thread(self, session_id: str) -> str | None:
    """Get an existing SDK thread for a session, or create a new one."""
    if session_id in self._sdk_thread_ids:
        return self._sdk_thread_ids[session_id]

    # Check database for existing SDK thread
    from app.database import get_session_context
    from app.models.db_models import ConversationThread

    with get_session_context() as db:
        existing = db.query(ConversationThread).filter_by(
            session_id=session_id, agent_name=self.agent_name
        ).first()
        if existing and existing.sdk_thread_id:
            self._sdk_thread_ids[session_id] = existing.sdk_thread_id
            return existing.sdk_thread_id

    # Create new SDK thread
    thread_id = await agent_client_manager.create_thread()
    if thread_id is not None:
        self._sdk_thread_ids[session_id] = thread_id
        # Persist to database
        with get_session_context() as db:
            existing = db.query(ConversationThread).filter_by(
                session_id=session_id, agent_name=self.agent_name
            ).first()
            if existing:
                existing.sdk_thread_id = thread_id
                db.commit()
    return thread_id
```

- [ ] **Step 3: Set sdk_thread_id in DM thread creation**

In `dungeon_master_agent.py`, when creating a new `ConversationThread`, include the SDK thread:

```python
new_thread = ConversationThread(
    id=str(uuid.uuid4()),
    session_id=session_id,
    campaign_id=campaign_id,
    agent_name="DM",
    messages=[],
    sdk_thread_id=self._sdk_thread_ids.get(session_id),
)
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/base_agent.py backend/app/agents/dungeon_master_agent.py
git commit -m "fix: persist SDK thread IDs to database for restart recovery (closes #702)"
```

---

### Task 8: Wire Narrator to use SDK lifecycle (#648)

**Files:**
- Modify: `backend/app/agents/narrator_agent.py`

- [ ] **Step 1: Read narrator's current direct API calls**

Read `backend/app/agents/narrator_agent.py` lines 149-196 (describe_scene), 440-470 (_generate_action_narration), and 630-660 (generate_opening_narrative).

- [ ] **Step 2: Add SDK-aware chat method**

Add a method that tries SDK first, falls back to direct Azure:

```python
async def _narrate(self, system_prompt: str, user_message: str, temperature: float = 0.75, max_tokens: int = 350) -> str | None:
    """Generate narrative using SDK if available, else direct Azure."""
    # Try SDK path first
    if not self._fallback_mode:
        sdk_response = await self._sdk_chat(
            user_message=user_message,
            system_context=system_prompt,
        )
        if sdk_response:
            return sdk_response

    # Fall back to direct Azure
    if self.azure_client and self.azure_client.is_configured():
        from app.config import get_settings
        settings = get_settings()
        response = await self.azure_client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            deployment=settings.azure_openai_mini_deployment or None,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response

    return None
```

- [ ] **Step 3: Replace direct Azure calls with _narrate()**

In `describe_scene()`, `_generate_action_narration()`, and `generate_opening_narrative()`, replace the direct `self.azure_client.chat_completion()` calls with `self._narrate()`.

- [ ] **Step 4: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/narrator_agent.py
git commit -m "feat: wire narrator to use SDK lifecycle with Azure fallback (closes #648)"
```

---

## Environment Setup (manual, before testing)

Create a `.env` file in the project root with:

```
AZURE_OPENAI_ENDPOINT=https://dev-foundry-h7bgqs75raq2c.cognitiveservices.azure.com/
AZURE_AI_PROJECT_ENDPOINT=https://dev-foundry-h7bgqs75raq2c.services.ai.azure.com/api/projects/dev-foundry-h7bgqs75raq2c
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-41-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

Note: #609 (DM returns stubs) is fixed by SDK wiring + env configuration. No separate code change needed.

## Final Verification

- [ ] Run full backend test suite
- [ ] Start backend with .env configured
- [ ] Verify `/health/dependencies` shows `"azure_openai": "available"`
- [ ] Test DM interaction returns AI-generated response (not stub)
- [ ] Create PRs: one per agent branch

"""
Tests for conversation history in the DM agent.

Verifies that:
- Thread messages accumulate across multiple calls
- Sliding window limits messages sent to the API
- Session summary is generated when history exceeds the limit
- Different session IDs get different threads
- Threads persist to and restore from the database
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.dungeon_master_agent import DungeonMasterAgent
from app.database import Base
from app.models.db_models import ConversationThread
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def _mock_azure_deps() -> Generator[tuple[Any, Any], None, None]:
    """Patch Azure dependencies so the DM agent can be imported."""
    with (
        patch("app.agent_client_setup.agent_client_manager") as mock_mgr,
        patch(
            "app.agents.dungeon_master_agent.azure_openai_client"
        ) as mock_azure,
    ):
        mock_mgr.get_chat_client.return_value = MagicMock()
        mock_azure.is_configured.return_value = True
        mock_azure.chat_completion = AsyncMock(
            return_value="The DM responds."
        )
        yield mock_mgr, mock_azure


@pytest.fixture
def dm_agent(
    _mock_azure_deps: tuple[Any, Any],
) -> Generator[DungeonMasterAgent, None, None]:
    """Create a DungeonMasterAgent with mocked Azure clients."""
    _, mock_azure = _mock_azure_deps
    import app.agents.dungeon_master_agent as dm_mod

    dm_mod._dungeon_master = None
    # Patch get_session_context for the agent's entire lifetime so that
    # _get_or_create_thread and _persist_thread never touch a real database.
    with patch("app.agents.dungeon_master_agent.get_session_context"):
        agent = dm_mod.DungeonMasterAgent()
        agent._fallback_mode = False
        agent.azure_client = mock_azure
        yield agent


class TestThreadPersistence:
    """Verify _get_or_create_thread returns the same thread per session."""

    def test_same_session_returns_same_thread(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        thread_a = dm_agent._get_or_create_thread("session-1")
        thread_b = dm_agent._get_or_create_thread("session-1")
        assert thread_a is thread_b

    def test_different_sessions_return_different_threads(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        thread_a = dm_agent._get_or_create_thread("session-1")
        thread_b = dm_agent._get_or_create_thread("session-2")
        assert thread_a is not thread_b

    def test_thread_has_messages_list(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        thread = dm_agent._get_or_create_thread("session-1")
        assert isinstance(thread, list)


class TestMessageAccumulation:
    """Verify that messages accumulate across multiple process_input calls."""

    @pytest.mark.asyncio
    async def test_messages_accumulate_across_calls(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        context = {"session_id": "test-session"}
        await dm_agent.process_input("I open the door", context)
        await dm_agent.process_input("I look around the room", context)

        thread = dm_agent._get_or_create_thread("test-session")
        # Each call adds user + assistant = 2 per call
        assert len(thread) == 4
        assert thread[0]["role"] == "user"
        assert thread[1]["role"] == "assistant"
        assert thread[2]["role"] == "user"
        assert thread[3]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_no_session_id_uses_default_thread(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        """When no session_id is provided, a default thread is used."""
        await dm_agent.process_input("Hello", {})
        await dm_agent.process_input("World", {})

        thread = dm_agent._get_or_create_thread("default")
        assert len(thread) == 4

    @pytest.mark.asyncio
    async def test_messages_contain_correct_content(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        context = {"session_id": "content-test"}
        await dm_agent.process_input("I cast fireball", context)

        thread = dm_agent._get_or_create_thread("content-test")
        assert "fireball" in thread[0]["content"].lower()


class TestSlidingWindow:
    """Verify the sliding window limits messages sent to the API."""

    @pytest.mark.asyncio
    async def test_sliding_window_limits_messages(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        """When history exceeds MAX_HISTORY_MESSAGES, only the window is sent."""
        context = {"session_id": "window-test"}

        # Fill thread with more than MAX_HISTORY_MESSAGES=20
        thread = dm_agent._get_or_create_thread("window-test")
        for i in range(30):
            thread.append({"role": "user", "content": f"Message {i}"})
            thread.append(
                {"role": "assistant", "content": f"Response {i}"}
            )

        await dm_agent.process_input("Final message", context)

        call_args = dm_agent.azure_client.chat_completion.call_args
        messages_sent = call_args.kwargs.get(
            "messages"
        ) or call_args[1].get(
            "messages",
            call_args[0][0] if call_args[0] else None,
        )

        assert messages_sent[0]["role"] == "system"
        # system + summary + 20 recent + 1 new user = 23
        assert len(messages_sent) <= 25

    @pytest.mark.asyncio
    async def test_no_summary_when_under_limit(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        """No summary message when history is under the limit."""
        context = {"session_id": "short-test"}
        await dm_agent.process_input("Hello", context)

        call_args = dm_agent.azure_client.chat_completion.call_args
        messages_sent = (
            call_args.kwargs.get("messages") or call_args[0][0]
        )

        system_msgs = [
            m for m in messages_sent if m["role"] == "system"
        ]
        assert len(system_msgs) == 1


class TestSessionSummary:
    """Verify session summaries for long conversations."""

    def test_summarise_history_returns_string(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        messages = [
            {"role": "user", "content": "I open the door"},
            {"role": "assistant", "content": "You see a dark corridor"},
            {"role": "user", "content": "I light a torch"},
            {
                "role": "assistant",
                "content": "The torch illuminates the passage",
            },
        ]
        summary = dm_agent._summarise_history(messages)
        assert isinstance(summary, str)
        assert "Player:" in summary
        assert "DM:" in summary

    def test_summarise_history_limits_to_10_exchanges(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        messages: list[dict[str, str]] = []
        for i in range(20):
            messages.append({"role": "user", "content": f"Action {i}"})
            messages.append(
                {"role": "assistant", "content": f"Response {i}"}
            )

        summary = dm_agent._summarise_history(messages)
        parts = summary.split(" | ")
        assert len(parts) <= 10

    def test_summarise_history_truncates_long_content(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        long_content = "A" * 200
        messages = [{"role": "user", "content": long_content}]
        summary = dm_agent._summarise_history(messages)
        assert len(summary) < 200

    @pytest.mark.asyncio
    async def test_summary_included_when_history_exceeds_limit(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        """When the sliding window kicks in, a summary is prepended."""
        context = {"session_id": "summary-test"}
        thread = dm_agent._get_or_create_thread("summary-test")

        for i in range(25):
            thread.append(
                {"role": "user", "content": f"Player action {i}"}
            )
            thread.append(
                {"role": "assistant", "content": f"DM narration {i}"}
            )

        await dm_agent.process_input("One more action", context)

        call_args = dm_agent.azure_client.chat_completion.call_args
        messages_sent = (
            call_args.kwargs.get("messages") or call_args[0][0]
        )

        system_msgs = [
            m for m in messages_sent if m["role"] == "system"
        ]
        assert len(system_msgs) == 2
        assert "Previous conversation summary" in system_msgs[1]["content"]


class TestFallbackModeHistory:
    """Verify conversation history works in fallback mode."""

    @pytest.mark.asyncio
    async def test_fallback_still_accumulates_messages(
        self, dm_agent: DungeonMasterAgent
    ) -> None:
        """Even in fallback mode, messages are recorded in the thread."""
        dm_agent._fallback_mode = True
        context = {"session_id": "fallback-test"}

        await dm_agent.process_input("I explore the cave", context)
        await dm_agent.process_input("I search for treasure", context)

        thread = dm_agent._get_or_create_thread("fallback-test")
        assert len(thread) == 4


# ---------------------------------------------------------------------------
# Database persistence tests
# ---------------------------------------------------------------------------


@pytest.fixture
def _in_memory_db() -> Generator[sessionmaker, None, None]:
    """Create an in-memory SQLite database with all tables."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    yield session_factory
    engine.dispose()


@pytest.fixture
def _patch_db_session(
    _in_memory_db: sessionmaker,
) -> Generator[None, None, None]:
    """Patch get_session_context to use the in-memory database."""

    @contextmanager
    def _fake_session_context() -> Generator:
        session = _in_memory_db()
        try:
            yield session
        finally:
            session.close()

    with patch(
        "app.agents.dungeon_master_agent.get_session_context",
        _fake_session_context,
    ):
        yield


@pytest.fixture
def dm_agent_with_db(
    _mock_azure_deps: tuple[Any, Any],
    _patch_db_session: None,
) -> DungeonMasterAgent:
    """Create a DungeonMasterAgent backed by the in-memory DB."""
    _, mock_azure = _mock_azure_deps
    import app.agents.dungeon_master_agent as dm_mod

    dm_mod._dungeon_master = None
    agent = dm_mod.DungeonMasterAgent()
    agent._fallback_mode = False
    agent.azure_client = mock_azure
    return agent


class TestDatabaseThreadPersistence:
    """Test that conversation threads persist to the database."""

    def test_get_or_create_thread_creates_db_record(
        self,
        dm_agent_with_db: DungeonMasterAgent,
        _in_memory_db: sessionmaker,
    ) -> None:
        """Creating a thread should insert a row in conversation_threads."""
        dm_agent_with_db._get_or_create_thread("db-session-1")

        session = _in_memory_db()
        row = (
            session.query(ConversationThread)
            .filter(ConversationThread.session_id == "db-session-1")
            .first()
        )
        session.close()
        assert row is not None
        assert row.agent_name == "DM"
        assert row.messages == []

    @pytest.mark.asyncio
    async def test_persist_thread_writes_messages_to_db(
        self,
        dm_agent_with_db: DungeonMasterAgent,
        _in_memory_db: sessionmaker,
    ) -> None:
        """After process_input, messages should be persisted to the DB."""
        context = {"session_id": "persist-test"}
        await dm_agent_with_db.process_input("Hello DM", context)

        session = _in_memory_db()
        row = (
            session.query(ConversationThread)
            .filter(ConversationThread.session_id == "persist-test")
            .first()
        )
        session.close()

        assert row is not None
        assert len(row.messages) == 2
        assert row.messages[0]["role"] == "user"
        assert row.messages[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_thread_survives_agent_re_instantiation(
        self,
        _mock_azure_deps: tuple[Any, Any],
        _patch_db_session: None,
        _in_memory_db: sessionmaker,
    ) -> None:
        """Threads should survive agent re-instantiation."""
        import app.agents.dungeon_master_agent as dm_mod

        _, mock_azure = _mock_azure_deps

        # Create first agent and process input
        dm_mod._dungeon_master = None
        agent1 = dm_mod.DungeonMasterAgent()
        agent1._fallback_mode = False
        agent1.azure_client = mock_azure

        context = {"session_id": "survive-test"}
        await agent1.process_input("I enter the dungeon", context)

        # Destroy the agent, wiping its in-memory cache
        del agent1

        # Create a second agent — it should recover the thread from DB
        dm_mod._dungeon_master = None
        agent2 = dm_mod.DungeonMasterAgent()
        agent2._fallback_mode = False
        agent2.azure_client = mock_azure

        thread = agent2._get_or_create_thread("survive-test")
        assert len(thread) == 2
        assert "dungeon" in thread[0]["content"].lower()

    def test_persist_thread_is_noop_when_session_missing(
        self,
        dm_agent_with_db: DungeonMasterAgent,
    ) -> None:
        """_persist_thread should not raise for an unknown session."""
        # Should not raise
        dm_agent_with_db._persist_thread("nonexistent-session")

    @pytest.mark.asyncio
    async def test_fallback_mode_also_persists(
        self,
        dm_agent_with_db: DungeonMasterAgent,
        _in_memory_db: sessionmaker,
    ) -> None:
        """Fallback-mode responses should also be persisted."""
        dm_agent_with_db._fallback_mode = True
        context = {"session_id": "fallback-persist"}

        await dm_agent_with_db.process_input("I explore", context)

        session = _in_memory_db()
        row = (
            session.query(ConversationThread)
            .filter(ConversationThread.session_id == "fallback-persist")
            .first()
        )
        session.close()

        assert row is not None
        assert len(row.messages) == 2

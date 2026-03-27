"""Session manager service for multiplayer game session lifecycle."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from app.database import get_session_context
from app.models.db_models import GameSession, SessionParticipant

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages multiplayer game sessions: creation, joining, turns, and teardown."""

    def create_session(self, campaign_id: str) -> dict:
        """Create a new game session for a campaign.

        Any existing active session for the campaign is ended first.
        """
        with get_session_context() as db:
            # End any existing active session for this campaign
            existing = self._get_active_session(db, campaign_id)
            if existing:
                existing.status = "ended"
                db.commit()

            session = GameSession(
                id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                status="active",
                turn_order=[],
                current_turn_index=0,
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return self._session_to_dict(session)

    def join_session(
        self,
        session_id: str,
        character_id: str,
        player_name: str,
        is_dm: bool = False,
    ) -> dict:
        """Add a participant to an existing session."""
        with get_session_context() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if not session:
                raise ValueError(f"Session {session_id} not found")
            if session.status != "active":
                raise ValueError(f"Session {session_id} is not active")

            # Check if character already joined
            existing = (
                db.query(SessionParticipant)
                .filter(
                    SessionParticipant.session_id == session_id,
                    SessionParticipant.character_id == character_id,
                )
                .first()
            )
            if existing:
                # Reconnect
                existing.is_connected = True
                existing.player_name = player_name
                db.commit()
                db.refresh(existing)
                return self._participant_to_dict(existing)

            participant = SessionParticipant(
                id=str(uuid.uuid4()),
                session_id=session_id,
                character_id=character_id,
                player_name=player_name,
                is_dm=is_dm,
                is_connected=True,
            )
            db.add(participant)
            db.commit()
            db.refresh(participant)
            return self._participant_to_dict(participant)

    def leave_session(self, session_id: str, participant_id: str) -> None:
        """Mark a participant as disconnected."""
        with get_session_context() as db:
            participant = (
                db.query(SessionParticipant)
                .filter(
                    SessionParticipant.id == participant_id,
                    SessionParticipant.session_id == session_id,
                )
                .first()
            )
            if participant:
                participant.is_connected = False
                db.commit()

    def get_session(self, session_id: str) -> dict | None:
        """Get session details including participants."""
        with get_session_context() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if not session:
                return None
            participants = (
                db.query(SessionParticipant)
                .filter(SessionParticipant.session_id == session_id)
                .all()
            )
            result = self._session_to_dict(session)
            result["participants"] = [
                self._participant_to_dict(p) for p in participants
            ]
            return result

    def get_active_session(self, campaign_id: str) -> dict | None:
        """Get the active session for a campaign, if any."""
        with get_session_context() as db:
            session = self._get_active_session(db, campaign_id)
            if not session:
                return None
            participants = (
                db.query(SessionParticipant)
                .filter(SessionParticipant.session_id == session.id)
                .all()
            )
            result = self._session_to_dict(session)
            result["participants"] = [
                self._participant_to_dict(p) for p in participants
            ]
            return result

    def get_participants(self, session_id: str) -> list[dict]:
        """List all participants in a session."""
        with get_session_context() as db:
            participants = (
                db.query(SessionParticipant)
                .filter(SessionParticipant.session_id == session_id)
                .all()
            )
            return [self._participant_to_dict(p) for p in participants]

    def set_turn_order(self, session_id: str, character_ids: list[str]) -> dict:
        """Set the turn order for a session."""
        with get_session_context() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if not session:
                raise ValueError(f"Session {session_id} not found")
            session.turn_order = character_ids
            session.current_turn_index = 0
            db.commit()
            db.refresh(session)
            return self._session_to_dict(session)

    def advance_turn(self, session_id: str) -> str:
        """Advance to the next turn and return the next character_id."""
        with get_session_context() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if not session:
                raise ValueError(f"Session {session_id} not found")
            if not session.turn_order:
                raise ValueError(f"Session {session_id} has no turn order set")

            next_index = (session.current_turn_index + 1) % len(session.turn_order)
            session.current_turn_index = next_index
            db.commit()
            return session.turn_order[next_index]

    def end_session(self, session_id: str) -> dict:
        """End a game session."""
        with get_session_context() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if not session:
                raise ValueError(f"Session {session_id} not found")
            session.status = "ended"
            # Disconnect all participants
            db.query(SessionParticipant).filter(
                SessionParticipant.session_id == session_id
            ).update({"is_connected": False})
            db.commit()
            db.refresh(session)
            return self._session_to_dict(session)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_active_session(db: Session, campaign_id: str) -> GameSession | None:
        return (
            db.query(GameSession)
            .filter(
                GameSession.campaign_id == campaign_id,
                GameSession.status == "active",
            )
            .first()
        )

    @staticmethod
    def _session_to_dict(session: GameSession) -> dict:
        return {
            "id": session.id,
            "campaign_id": session.campaign_id,
            "status": session.status,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "turn_order": session.turn_order or [],
            "current_turn_index": session.current_turn_index or 0,
        }

    @staticmethod
    def _participant_to_dict(participant: SessionParticipant) -> dict:
        return {
            "id": participant.id,
            "session_id": participant.session_id,
            "character_id": participant.character_id,
            "player_name": participant.player_name,
            "is_dm": participant.is_dm,
            "is_connected": participant.is_connected,
            "joined_at": participant.joined_at.isoformat() if participant.joined_at else None,
        }


# Module-level singleton
session_manager = SessionManager()

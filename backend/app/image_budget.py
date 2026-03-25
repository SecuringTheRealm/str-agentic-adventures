"""
Per-session image-generation budget tracker.

Keeps DALL-E spend under control by capping the number of images that can be
generated within a rolling time window.  Each caller supplies an opaque
``session_id`` string; the tracker counts calls per session and rejects
requests that exceed the configured maximum.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)


class ImageBudgetTracker:
    """Thread-safe, in-memory tracker for per-session image generation limits.

    Args:
        max_images: Maximum number of images allowed per session per window.
        window_minutes: Length of the rolling window in minutes.
    """

    def __init__(self, max_images: int = 3, window_minutes: int = 30) -> None:
        self.max_images = max_images
        self.window = timedelta(minutes=window_minutes)
        # session_id -> list of UTC timestamps for recent generations
        self._sessions: dict[str, list[datetime]] = defaultdict(list)
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_and_record(self, session_id: str) -> tuple[bool, int]:
        """Attempt to record a new image generation for *session_id*.

        Prunes timestamps outside the rolling window, then checks whether the
        remaining count is below the cap.  If allowed, the current timestamp is
        appended before returning.

        Returns:
            A ``(allowed, remaining)`` tuple where *allowed* is ``True`` when
            the generation may proceed and *remaining* is the number of
            additional images the session may still request (0 when blocked).
        """
        now = datetime.now(tz=UTC)
        cutoff = now - self.window

        with self._lock:
            self._prune(session_id, cutoff)
            count = len(self._sessions[session_id])

            if count >= self.max_images:
                logger.warning(
                    "Image budget exceeded for session %s (%d/%d in window)",
                    session_id,
                    count,
                    self.max_images,
                )
                return False, 0

            self._sessions[session_id].append(now)
            remaining = self.max_images - (count + 1)
            logger.debug(
                "Image recorded for session %s (%d/%d, %d remaining)",
                session_id,
                count + 1,
                self.max_images,
                remaining,
            )
            return True, remaining

    def get_remaining(self, session_id: str) -> int:
        """Return how many images *session_id* may still generate this window."""
        now = datetime.now(tz=UTC)
        cutoff = now - self.window

        with self._lock:
            self._prune(session_id, cutoff)
            return max(0, self.max_images - len(self._sessions[session_id]))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prune(self, session_id: str, cutoff: datetime) -> None:
        """Remove timestamps older than *cutoff* for *session_id* (lock held)."""
        self._sessions[session_id] = [
            ts for ts in self._sessions[session_id] if ts > cutoff
        ]

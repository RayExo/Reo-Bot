from __future__ import annotations

import secrets
import time
from typing import Any

_bot = None
_sessions: dict[str, dict[str, Any]] = {}
_oauth_states: dict[str, float] = {}


def bind_bot(bot) -> None:
    global _bot
    _bot = bot


def get_bot():
    return _bot


def create_session(payload: dict[str, Any]) -> str:
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = payload
    return session_id


def get_session(session_id: str | None) -> dict[str, Any] | None:
    if not session_id:
        return None
    return _sessions.get(session_id)


def destroy_session(session_id: str | None) -> None:
    if session_id:
        _sessions.pop(session_id, None)


def create_oauth_state() -> str:
    state = secrets.token_urlsafe(24)
    _oauth_states[state] = time.time()
    return state


def consume_oauth_state(state: str | None) -> bool:
    if not state:
        return False
    created_at = _oauth_states.pop(state, None)
    if created_at is None:
        return False
    return (time.time() - created_at) < 600

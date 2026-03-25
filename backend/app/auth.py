"""FastAPI dependency for Azure Container Apps Easy Auth user identity headers."""

import base64
import json
from dataclasses import dataclass, field
from typing import Annotated

from fastapi import Depends, Header, HTTPException


@dataclass
class AuthenticatedUser:
    user_id: str
    name: str
    claims: dict = field(default_factory=dict)


def get_current_user(
    x_ms_client_principal_id: str | None = Header(default=None),
    x_ms_client_principal_name: str | None = Header(default=None),
    x_ms_client_principal: str | None = Header(default=None),
) -> AuthenticatedUser:
    """Extract user identity from Easy Auth headers injected by Azure Container Apps."""
    if not x_ms_client_principal_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    claims: dict = {}
    if x_ms_client_principal:
        try:
            decoded = base64.b64decode(x_ms_client_principal).decode("utf-8")
            principal = json.loads(decoded)
            claims = {c["typ"]: c["val"] for c in principal.get("claims", [])}
        except (ValueError, KeyError, json.JSONDecodeError):
            pass
    return AuthenticatedUser(
        user_id=x_ms_client_principal_id,
        name=x_ms_client_principal_name or "",
        claims=claims,
    )


# Type alias for use in route signatures via dependency injection
AuthDep = Annotated[AuthenticatedUser, Depends(get_current_user)]

"""Fixture: should trigger NO signals — clean EMDCA code."""

from typing import Literal, NewType

from pydantic import BaseModel

UserId = NewType("UserId", str)
Email = NewType("Email", str)
Reason = NewType("Reason", str)


class ActiveUser(BaseModel):
    """Active user — no primitives, no defaults, no is_ flags."""

    model_config = {"frozen": True}
    kind: Literal["active"]
    id: UserId
    email: Email


class InactiveUser(BaseModel):
    """Inactive user — Value Object for reason."""

    model_config = {"frozen": True}
    kind: Literal["inactive"]
    id: UserId
    reason: Reason


type User = ActiveUser | InactiveUser

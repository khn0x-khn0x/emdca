"""Fixture: should trigger boolean_flag signal."""

from pydantic import BaseModel


class User(BaseModel):
    is_active: bool
    is_verified: bool

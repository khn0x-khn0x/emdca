"""Fixture: should trigger primitive_type signal."""

from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    score: float

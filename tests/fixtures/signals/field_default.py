"""Fixture: should trigger field_default signal."""

from typing import NewType

from pydantic import BaseModel

Status = NewType("Status", str)
Count = NewType("Count", int)


class Order(BaseModel):
    status: Status = Status("pending")  # Non-primitive type with default
    count: Count = Count(0)

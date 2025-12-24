"""Fixture: should trigger raise_stmt signal."""


def validate() -> None:
    raise ValueError("bad input")

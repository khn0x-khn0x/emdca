"""Fixture: should trigger validate_function signal."""


def validate_email(value: str) -> bool:
    return "@" in value


def check_name(name: str) -> bool:
    return len(name) > 0

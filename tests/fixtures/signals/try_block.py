"""Fixture: should trigger try_block signal."""


def process() -> None:
    try:
        _ = 1  # noqa: F841
    except Exception:
        pass

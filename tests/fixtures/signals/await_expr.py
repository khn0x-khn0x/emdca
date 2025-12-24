"""Fixture: should trigger await_expr signal."""


async def some_api() -> None:
    """Stub async function."""


async def fetch() -> None:
    await some_api()

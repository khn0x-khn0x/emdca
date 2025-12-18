from .primitives import UserId

async def process_conversation(user_id: UserId):
    # Violation: Async in Domain
    await some_io_call()


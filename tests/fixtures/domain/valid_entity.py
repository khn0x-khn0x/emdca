from pydantic import BaseModel
from typing import Literal

class User(BaseModel):
    id: str
    status: Literal["active", "inactive"]

def create_user(name: str) -> User:
    # Pure logic, no side effects
    return User(id="1", status="active")


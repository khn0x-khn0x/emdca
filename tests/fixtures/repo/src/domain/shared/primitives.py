from typing import NewType
from pydantic import BaseModel

UserId = NewType("UserId", str)
Amount = NewType("Amount", int)
Currency = NewType("Currency", str)

class Money(BaseModel):
    amount: Amount
    currency: Currency

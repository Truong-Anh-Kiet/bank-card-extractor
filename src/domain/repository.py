from .bank_card import BankCard
from typing import Protocol, List

class BankCardRepository(Protocol):
    """Port for storing extracted BankCard."""
    async def save(self, card: BankCard) -> None: ...
    async def get_all(self) -> List[BankCard]: ...
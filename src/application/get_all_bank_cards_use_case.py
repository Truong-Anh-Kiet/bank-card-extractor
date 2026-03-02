from domain import BankCard, BankCardRepository
from typing import List

class GetAllBankCardsUseCase:
    """Use case to retrieve all saved bank cards."""

    def __init__(self, repository: BankCardRepository):
        self.repository = repository

    async def execute(self) -> List[BankCard]:
        return await self.repository.get_all()
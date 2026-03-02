from domain import BankCard
from domain import BankCardRepository
from .ports import LLMServiceProtocol

class ExtractBankCardUseCase:
    """Application Use Case - Contains business rules."""

    def __init__(self, llm_service: LLMServiceProtocol, repository: BankCardRepository):
        self.llm_service = llm_service
        self.repository = repository

    async def execute(self, image_base64: str) -> BankCard:
        """Extract card information from image."""
        card: BankCard = await self.llm_service.extract_from_image(image_base64)
        if not card.is_valid():
            card.confidence *= 0.6
        if card.confidence < 0.1:
            card.confidence = 0.1
        await self.repository.save(card)
        return card
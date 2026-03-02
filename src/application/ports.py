from domain import BankCard
from typing import Protocol


class LLMServiceProtocol(Protocol):
    """Port (Interface) - Dependency Inversion Principle."""
    async def extract_from_image(self, image_base64: str) -> BankCard: ...
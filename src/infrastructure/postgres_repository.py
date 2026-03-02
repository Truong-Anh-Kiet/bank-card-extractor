from uuid import uuid4
from sqlalchemy import select, Column, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from domain import BankCard, BankCardRepository
from .database import Base
from typing import List


class BankCardDB(Base):
    """SQLAlchemy model for the bank_cards table."""
    __tablename__ = "bank_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    bank_name = Column(String, nullable=False)
    payment_network = Column(String, nullable=False)
    card_number = Column(String, nullable=False)
    cardholder_name = Column(String, nullable=False)
    expiry_date = Column(String, nullable=False)
    card_type = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    extracted_at = Column(DateTime, default=func.now(), nullable=False)


class PostgresBankCardRepository(BankCardRepository):
    """Async Postgres Repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, card: BankCard) -> None:
        db_card = BankCardDB(
            bank_name=card.bank_name,
            payment_network=card.payment_network,
            card_number=card.card_number,
            cardholder_name=card.cardholder_name,
            expiry_date=card.expiry_date,
            card_type=card.card_type,
            confidence=card.confidence,
        )
        self.session.add(db_card)
        await self.session.commit()

    async def get_all(self) -> List[BankCard]:
        result = await self.session.execute(
            select(BankCardDB).order_by(BankCardDB.extracted_at.desc())
        )
        db_cards = result.scalars().all()

        return [
            BankCard(
                bank_name=db.bank_name,
                payment_network=db.payment_network,
                card_number=db.card_number,
                cardholder_name=db.cardholder_name,
                expiry_date=db.expiry_date,
                card_type=db.card_type,
                confidence=db.confidence,
            )
            for db in db_cards
        ]
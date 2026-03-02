import os
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from domain import BankCard
from application import BankCardRepository
from typing import List

Base = declarative_base()


class BankCardDB(Base):
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
    """Postgres implementation for storing and retrieving BankCard."""

    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in .env")
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    async def save(self, card: BankCard) -> None:
        session = self.Session()
        db_card = BankCardDB(
            bank_name=card.bank_name,
            payment_network=card.payment_network,
            card_number=card.card_number,
            cardholder_name=card.cardholder_name,
            expiry_date=card.expiry_date,
            card_type=card.card_type,
            confidence=card.confidence,
        )
        session.add(db_card)
        session.commit()
        session.close()

    async def get_all(self) -> List[BankCard]:
        session = self.Session()
        db_cards = session.query(BankCardDB)\
                         .order_by(BankCardDB.extracted_at.desc())\
                         .all()
        session.close()

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
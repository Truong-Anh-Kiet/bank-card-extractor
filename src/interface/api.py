from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from application.extract_bank_card_use_case import ExtractBankCardUseCase, GetAllBankCardsUseCase
from infrastructure import get_db
from domain import BankCard
import base64

from src.infrastructure import containers

router = APIRouter(prefix="/api/v1", tags=["bank-card"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_extract_use_case(session: SessionDep) -> ExtractBankCardUseCase:
    return containers.extract_use_case(session=session)


async def get_all_use_case(session: SessionDep) -> GetAllBankCardsUseCase:
    return containers.get_all_use_case(session=session)


@router.post("/extract", response_model=BankCard)
async def extract_card(
    file: UploadFile,
    use_case: ExtractBankCardUseCase = Depends(get_extract_use_case),
):
    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    card = await use_case.execute(image_base64)
    return card


@router.get("/cards", response_model=list[BankCard])
async def get_all_cards(
    use_case: GetAllBankCardsUseCase = Depends(get_all_use_case),
):
    """Lấy lịch sử tất cả bank cards đã extract"""
    return await use_case.execute()
from typing import List
from fastapi import APIRouter, UploadFile, Depends
from application import ExtractBankCardUseCase, GetAllBankCardsUseCase
from domain import BankCard
from infrastructure import LangGraphLLMService, PostgresBankCardRepository
import base64


router = APIRouter(prefix="/api/v1", tags=["bank-card"])

def get_use_case() -> ExtractBankCardUseCase:
    llm_service = LangGraphLLMService()
    repository = PostgresBankCardRepository()
    return ExtractBankCardUseCase(llm_service, repository)

def get_all_use_case() -> GetAllBankCardsUseCase:
    repository = PostgresBankCardRepository()
    return GetAllBankCardsUseCase(repository)

@router.post("/extract", response_model=BankCard)
async def extract_card(
    file: UploadFile,
    use_case: ExtractBankCardUseCase = Depends(get_use_case),
):
    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    card = await use_case.execute(image_base64)
    return card

@router.get("/cards", response_model=List[BankCard])
async def get_all_cards(
    use_case: GetAllBankCardsUseCase = Depends(get_all_use_case),
):
    """Get history of all extracted bank cards"""
    return await use_case.execute()
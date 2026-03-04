from fastapi import APIRouter, UploadFile, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from infrastructure import container, get_db, limiter
from application import ExtractBankCardUseCase, GetAllBankCardsUseCase
from domain import BankCard
import base64
import logging

logging.basicConfig(level=logging.ERROR)

router = APIRouter(prefix="/api/v1", tags=["bank-card"], redirect_slashes=False)

SessionDep = Annotated[AsyncSession, Depends(get_db)]

async def get_extract_use_case(session: SessionDep) -> ExtractBankCardUseCase:
    repository = container.repository(session=session)
    return container.extract_use_case(repository=repository)

async def get_all_use_case(session: SessionDep) -> GetAllBankCardsUseCase:
    repository = container.repository(session=session)
    return container.get_all_use_case(repository=repository)

@router.post("/extract", response_model=BankCard)
@limiter.limit("5/minute")
async def extract_card(
    request: Request, # noqa: ARG002
    file: UploadFile,
    use_case: ExtractBankCardUseCase = Depends(get_extract_use_case),
):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
        
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        card = await use_case.execute(image_base64)
        return card
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Error extracting card: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while extracting card information.")

@router.get("/cards", response_model=List[BankCard])
async def get_all_cards(
    use_case: GetAllBankCardsUseCase = Depends(get_all_use_case),
):
    """Get all extracted bank cards."""
    try:
        return await use_case.execute()
    except Exception as e:
        logging.error(f"Error fetching cards: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching cards.")
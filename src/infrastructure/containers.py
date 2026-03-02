from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from application import ExtractBankCardUseCase, GetAllBankCardsUseCase
from infrastructure import LangGraphLLMService, PostgresBankCardRepository

class Container(containers.DeclarativeContainer):
    """Dependency injection container for the application."""

    llm_service = providers.Singleton(LangGraphLLMService)

    repository = providers.Factory(
        PostgresBankCardRepository,
        session=providers.Dependency(instance_of=AsyncSession),
    )

    extract_use_case = providers.Factory(
        ExtractBankCardUseCase,
        llm_service=llm_service,
        repository=repository,
    )

    get_all_use_case = providers.Factory(
        GetAllBankCardsUseCase,
        repository=repository,
    )

container = Container()
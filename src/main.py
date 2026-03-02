from fastapi import FastAPI
from interface import router
import uvicorn
from dotenv import load_dotenv
import warnings
from infrastructure import lifespan

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r"Pydantic serializer warnings:\s*PydanticSerializationUnexpectedValue\(Expected `none`",
    module="pydantic.main"
)

load_dotenv()

app = FastAPI(
    title="Bank Card Extractor",
    description="Clean Architecture + LangGraph + Multimodal LLM",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

# uv run uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
# http://localhost:8000/docs
if __name__ == "__main__":
    uvicorn.run("main:app", app_dir="src", host="0.0.0.0", port=8000, reload=True)
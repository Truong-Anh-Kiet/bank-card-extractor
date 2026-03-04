from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from interface import router
import uvicorn
from dotenv import load_dotenv
import warnings
from infrastructure import lifespan, limiter

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="pydantic.main"
)

load_dotenv()

app = FastAPI(
    title="Bank Card Extractor",
    description="Clean Architecture + LangGraph + Multimodal LLM",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(router)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if (
        request.method == "POST"
        and request.url.path.rstrip("/") == "/api/v1/extract"
    ):
        content_length = int(request.headers.get("content-length", 0))
        if content_length > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=413,
                detail="File too large. Max 5MB allowed."
            )
    response = await call_next(request)
    return response

# http://localhost:8000/docs
# uv run uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        app_dir="src",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
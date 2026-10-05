from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.ai.provider import AIProvider, MockProvider, OpenAICompatibleProvider, ProviderError
from app.ai.schemas import AnalyzeRequest, AnalyzeResponse, TeachBackRequest, TeachBackResponse
from app.ai.prompts import PROMPT_VERSION, TEACH_BACK_VERSION
from app.ai.service import AIService
from app.config import Settings

logger = logging.getLogger("asclepius.api")


def create_app(settings: Settings | None = None, provider: AIProvider | None = None) -> FastAPI:
    config = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        async with httpx.AsyncClient(follow_redirects=False) as client:
            selected: AIProvider = provider if provider is not None else (
                MockProvider() if config.ai_provider == "mock"
                else OpenAICompatibleProvider(config, client)
            )
            application.state.ai_service = AIService(selected)
            yield

    application = FastAPI(
        title="Asclepius — Understand your care instructions",
        version="0.2.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[config.frontend_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.get("/health")
    async def health() -> dict[str, str | None]:
        return {"status": "ok", "provider": config.ai_provider, "model": config.ai_model if config.ai_provider == "openai" else None}

    @application.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
        request_id = uuid4()
        start = perf_counter()
        try:
            service: AIService = application.state.ai_service
            result = await service.analyze(request)
        except ProviderError as exc:
            logger.warning("analysis_failed request_id=%s code=%s", request_id, exc.code)
            raise HTTPException(
                status_code=exc.status_code,
                detail={"code": exc.code, "message": exc.message},
            ) from None
        return AnalyzeResponse(
            prompt_version=PROMPT_VERSION,
            request_id=request_id,
            provider=config.ai_provider,
            model=config.ai_model if config.ai_provider == "openai" else None,
            is_mock=config.ai_provider == "mock",
            origin=service.origin("care_plan", request.text),
            elapsed_ms=max(0, round((perf_counter() - start) * 1000)),
            result=result,
        )

    @application.post("/teach-back", response_model=TeachBackResponse)
    async def teach_back(request: TeachBackRequest) -> TeachBackResponse:
        request_id = uuid4()
        start = perf_counter()
        try:
            service: AIService = application.state.ai_service
            result = await service.teach_back(request)
        except ProviderError as exc:
            logger.warning("teach_back_failed request_id=%s code=%s", request_id, exc.code)
            raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from None
        return TeachBackResponse(
            prompt_version=TEACH_BACK_VERSION,
            request_id=request_id,
            provider=config.ai_provider,
            model=config.ai_model if config.ai_provider == "openai" else None,
            is_mock=config.ai_provider == "mock",
            origin=service.origin("teach_back", request.text),
            elapsed_ms=max(0, round((perf_counter() - start) * 1000)),
            result=result,
        )

    return application

import asyncio
import json
from typing import Any

import httpx
from pydantic import SecretStr
import pytest

from app.ai.provider import OpenAICompatibleProvider, ProviderError
from app.config import Settings


def config() -> Settings:
    return Settings(_env_file=None, ai_provider="openai", ai_api_key=SecretStr("test-only"), ai_model="test-model")


def invoke(handler: Any) -> str:
    async def run() -> str:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await OpenAICompatibleProvider(config(), client).generate("system", "user")
    return asyncio.run(run())


def test_request_contract() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.openai.com/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-only"
        body = json.loads(request.content)
        assert body["model"] == "test-model"
        assert body["max_tokens"] == 800
        assert body["response_format"] == {"type": "json_object"}
        assert body["messages"][0] == {"role": "system", "content": "system"}
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]})
    assert invoke(handler) == "{}"


@pytest.mark.parametrize("status,code,expected", [(429, "provider_rate_limit", 429), (401, "provider_failure", 502), (500, "provider_failure", 502)])
def test_http_failures(status: int, code: str, expected: int) -> None:
    with pytest.raises(ProviderError) as captured:
        invoke(lambda request: httpx.Response(status, text="private provider details"))
    assert captured.value.code == code
    assert captured.value.status_code == expected
    assert "private" not in str(captured.value)


@pytest.mark.parametrize("payload", [{}, {"choices": []}, {"choices": [{"message": {"content": None}}]}, {"choices": [{"message": {"content": " "}}]}, {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]}, {"choices": "wrong type"}])
def test_bad_envelopes(payload: Any) -> None:
    with pytest.raises(ProviderError) as captured:
        invoke(lambda request: httpx.Response(200, json=payload))
    assert captured.value.code == "invalid_response"


@pytest.mark.parametrize("content", ["not JSON", "x" * 100001], ids=["malformed", "oversized"])
def test_malformed_or_large_response(content: str) -> None:
    with pytest.raises(ProviderError):
        invoke(lambda request: httpx.Response(200, text=content))


@pytest.mark.parametrize("error,code,status", [(httpx.ReadTimeout, "provider_timeout", 504), (httpx.ConnectError, "provider_unavailable", 502)])
def test_transport_failures(error: type[httpx.RequestError], code: str, status: int) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise error("private transport detail", request=request)
    with pytest.raises(ProviderError) as captured:
        invoke(handler)
    assert captured.value.code == code
    assert captured.value.status_code == status
    assert "private" not in str(captured.value)

from __future__ import annotations

from typing import Any, Optional
from google import genai
from google.genai import types

from config import settings


class GeminiServiceError(RuntimeError):
    pass


_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    global _client

    if _client is not None:
        return _client

    if not settings.gemini_api_key:
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. Add it to your .env file."
        )

    try:
        _client = genai.Client(api_key=settings.gemini_api_key)
        return _client
    except Exception as exc:
        raise GeminiServiceError(f"Could not initialize Gemini client: {exc}") from exc


def generate_text(
    prompt: str,
    *,
    system_instruction: Optional[str] = None,
    temperature: float = 0.4,
    max_output_tokens: int = 2048,
) -> str:
    client = get_client()

    config_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }

    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
    except Exception as exc:
        raise GeminiServiceError(f"Gemini request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise GeminiServiceError("Gemini returned an empty response.")

    return text.strip()


def generate_json(
    prompt: str,
    response_schema: Any,
    *,
    system_instruction: Optional[str] = None,
    temperature: float = 0.3,
    max_output_tokens: int = 4096,
) -> str:
    client = get_client()

    config_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "response_mime_type": "application/json",
        "response_schema": response_schema,
    }

    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
    except Exception as exc:
        raise GeminiServiceError(f"Gemini JSON request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise GeminiServiceError("Gemini returned an empty JSON response.")

    return text.strip()

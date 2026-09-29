from __future__ import annotations

from typing import Optional

from config import settings
from gemini_service import GeminiServiceError, generate_text

_local_pipeline = None
_local_load_attempted = False


def _load_local_model():
    global _local_pipeline, _local_load_attempted

    if _local_load_attempted:
        return _local_pipeline

    _local_load_attempted = True

    try:
        from transformers import pipeline

        _local_pipeline = pipeline(
            "text2text-generation",
            model=settings.local_explanation_model,
            device=-1,
        )
    except Exception:
        _local_pipeline = None

    return _local_pipeline


def _local_explain(topic: str, level: str) -> Optional[str]:
    pipe = _load_local_model()
    if pipe is None:
        return None

    prompt = (
        f"Explain {topic} to a {level} learner. "
        "Use simple language, short paragraphs, and one practical example."
    )

    try:
        result = pipe(prompt, max_new_tokens=220, do_sample=False)
        return result[0]["generated_text"].strip()
    except Exception:
        return None


async def explain_topic(topic: str, level: str = "beginner") -> dict:
    provider = settings.explanation_provider.lower()

    if provider in {"auto", "local"}:
        local_result = _local_explain(topic, level)
        if local_result:
            return {
                "topic": topic,
                "level": level,
                "provider": "LaMini-Flan-T5-783M",
                "answer": local_result,
            }

        if provider == "local":
            return {
                "topic": topic,
                "level": level,
                "provider": "local",
                "answer": "The local explanation model could not be loaded. Check the model dependencies and try again.",
            }

    prompt = f"""
Explain the following educational topic for a {level} learner.

Topic: {topic}

Requirements:
- Start with a one-sentence definition.
- Explain the main idea in simple language.
- Give 2-4 key points.
- Give one everyday or academic example.
- Avoid unnecessary jargon.
- If a technical term is necessary, define it briefly.
""".strip()

    try:
        answer = generate_text(
            prompt,
            system_instruction=(
                "You are EduGenie, a patient educational tutor. "
                "Prioritize clarity, correctness, and age-appropriate explanations."
            ),
            temperature=0.3,
            max_output_tokens=1200,
        )
        return {
            "topic": topic,
            "level": level,
            "provider": "Gemini",
            "answer": answer,
        }
    except GeminiServiceError as exc:
        return {"error": str(exc)}

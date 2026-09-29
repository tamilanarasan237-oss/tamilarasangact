from gemini_service import GeminiServiceError, generate_text


async def summarize_text(text: str, max_words: int = 150) -> dict:
    prompt = f"""
Summarize the following educational text in no more than {max_words} words.

Requirements:
- Preserve the central ideas and important facts.
- Remove repetition and minor details.
- Use clear language.
- Do not add information that is absent from the source.

Text:
{text}
""".strip()

    try:
        summary = generate_text(
            prompt,
            system_instruction=(
                "You are EduGenie summarization tutor. Preserve meaning and avoid hallucinations."
            ),
            temperature=0.2,
            max_output_tokens=max(180, min(1600, max_words * 3)),
        )
        return {"summary": summary, "max_words": max_words}
    except GeminiServiceError as exc:
        return {"error": str(exc)}

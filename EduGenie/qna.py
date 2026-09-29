from gemini_service import GeminiServiceError, generate_text


async def answer_question(question: str) -> dict:
    prompt = f"""
Answer this academic/general-knowledge question:

{question}

Instructions:
- Give a direct answer first.
- Then explain the reasoning or context briefly.
- Use simple language.
- If the question is ambiguous, state the assumption you used.
- Do not invent sources, citations, statistics, or facts.
""".strip()

    try:
        answer = generate_text(
            prompt,
            system_instruction=(
                "You are EduGenie Q&A tutor. Be accurate, concise, and educational."
            ),
            temperature=0.2,
            max_output_tokens=1200,
        )
        return {"question": question, "answer": answer}
    except GeminiServiceError as exc:
        return {"error": str(exc)}

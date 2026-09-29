from gemini_service import GeminiServiceError, generate_text


async def get_learning_recommendations(
    topic: str,
    level: str = "beginner",
    duration_weeks: int = 8,
) -> dict:
    prompt = f"""
Create a structured learning path for:

Topic: {topic}
Learner level: {level}
Duration: {duration_weeks} weeks

Include:
1. A short learning goal.
2. A week-by-week progression from fundamentals toward advanced concepts appropriate to the duration.
3. For each week: concepts, a practical activity, and a simple checkpoint.
4. Recommended resource types (video, article, documentation, book, practice site).
5. A final mini-project or assessment.

Do not invent exact URLs. Name resource types or well-known resource categories instead.
""".strip()

    try:
        path = generate_text(
            prompt,
            system_instruction=(
                "You are EduGenie learning-path planner. "
                "Adapt the sequence to the learner's stated level and duration."
            ),
            temperature=0.4,
            max_output_tokens=3000,
        )
        return {
            "topic": topic,
            "level": level,
            "duration_weeks": duration_weeks,
            "learning_path": path,
        }
    except GeminiServiceError as exc:
        return {"error": str(exc)}

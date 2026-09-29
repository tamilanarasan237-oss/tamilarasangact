import json
from typing import List
from pydantic import BaseModel, Field

from gemini_service import GeminiServiceError, generate_json


class QuizItem(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str = ""


class QuizPayload(BaseModel):
    title: str
    questions: List[QuizItem]


def _schema() -> dict:
    return QuizPayload.model_json_schema()


def _clean_json_block(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    if text.startswith("json"):
        text = text[4:].lstrip()

    return text


async def generate_quiz(text: str, num_questions: int = 3) -> dict:
    prompt = f"""
Create a multiple-choice quiz from the educational passage below.

Passage:
{text}

Create exactly {num_questions} questions.
For every question:
- Provide exactly four options.
- Make only one option correct.
- Set correct_answer to the exact text of the correct option.
- Include a short explanation.
- Keep questions answerable from the passage whenever possible.
""".strip()

    try:
        raw = generate_json(
            prompt,
            _schema(),
            system_instruction=(
                "You generate valid structured educational quiz data. "
                "Never put Markdown outside the requested JSON structure."
            ),
            temperature=0.4,
            max_output_tokens=3500,
        )
        data = QuizPayload.model_validate(json.loads(_clean_json_block(raw)))

        if len(data.questions) != num_questions:
            return {
                "error": f"Model returned {len(data.questions)} questions; expected {num_questions}."
            }

        return data.model_dump()
    except (GeminiServiceError, ValueError, json.JSONDecodeError) as exc:
        return {"error": f"Quiz generation failed: {exc}"}

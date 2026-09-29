from typing import List, Literal
from pydantic import BaseModel, Field


class ExplainRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=10000)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class QARequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)


class QuizRequest(BaseModel):
    text: str = Field(min_length=1, max_length=30000)
    num_questions: int = Field(default=3, ge=1, le=10)


class SummaryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=30000)
    max_words: int = Field(default=150, ge=30, le=1000)


class LearningPathRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=10000)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    duration_weeks: int = Field(default=8, ge=1, le=52)


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str = ""


class QuizResponse(BaseModel):
    title: str
    questions: List[QuizQuestion]


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""

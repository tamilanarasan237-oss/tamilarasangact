from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from schemas import (
    ExplainRequest, QARequest, QuizRequest, SummaryRequest,
    LearningPathRequest, ErrorResponse
)
from explanation_module import explain_topic
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

app = FastAPI(
    title="EduGenie API",
    description="Google Gemini powered learning assistant",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "gemini_model": settings.gemini_model,
        },
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": bool(settings.gemini_api_key),
        "explanation_provider": settings.explanation_provider,
        "gemini_model": settings.gemini_model,
    }


@app.post("/qa")
async def qa(payload: QARequest):
    return await answer_question(payload.question)


@app.post("/explain")
async def explain(payload: ExplainRequest):
    return await explain_topic(payload.topic, payload.level)


@app.post("/quiz")
async def quiz(payload: QuizRequest):
    return await generate_quiz(payload.text, payload.num_questions)


@app.post("/summarize")
async def summarize(payload: SummaryRequest):
    return await summarize_text(payload.text, payload.max_words)


@app.post("/learn/recommendations")
async def recommendations(payload: LearningPathRequest):
    return await get_learning_recommendations(payload.topic, payload.level, payload.duration_weeks)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Keep API errors JSON-shaped so the frontend can display them cleanly.
    return ErrorResponse(error="Unexpected server error", detail=str(exc)).model_dump()

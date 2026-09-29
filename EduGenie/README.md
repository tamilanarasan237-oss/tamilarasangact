# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight educational assistant based on the supplied project documentation. The original document describes a FastAPI backend, HTML/CSS frontend, separate modules for Q&A, explanations, quizzes, summarization and learning recommendations, plus Google Gemini and a local LaMini-Flan-T5 explanation model.

This implementation keeps that modular architecture and makes the Gemini integration use the current `google-genai` SDK. The Gemini model is configurable through `.env`.

## Features

- Ask academic/general-knowledge questions
- Explain concepts for beginner/intermediate/advanced learners
- Generate 3, 5 or 10 MCQs with four options each
- Summarize educational text
- Generate a week-by-week learning path
- Responsive HTML/CSS/JavaScript frontend
- FastAPI REST endpoints
- Structured JSON validation for quizzes
- Local LaMini explanation provider with Gemini fallback
- Health endpoint and basic automated tests
- Optional Docker deployment

## Project structure

```text
EduGenie/
├── main.py
├── config.py
├── schemas.py
├── gemini_service.py
├── explanation_module.py
├── qna.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── .env.example
├── .gitignore
├── pytest.ini
├── Dockerfile
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── tests/
    └── test_api.py
```

## 1. Prerequisites

- Python 3.10 or newer
- VS Code
- A Google AI Studio Gemini API key for cloud features

The supplied project document specifies Python 3.10+, FastAPI, Jinja2, Uvicorn and a Google Gemini API key.

## 2. Open the project in VS Code

Open the `EduGenie` folder in VS Code.

Open VS Code Terminal:

```powershell
cd path\to\EduGenie
```

## 3. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The first installation can be large because the local LaMini explanation path uses PyTorch and Transformers.

## 5. Configure Gemini

Copy `.env.example` to `.env`.

Windows:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Open `.env` and replace:

```text
GEMINI_API_KEY=your_google_ai_studio_api_key_here
```

with your actual key.

Do not commit `.env` to Git.

## 6. Choose explanation mode

For the simplest setup, use:

```text
EXPLANATION_PROVIDER=gemini
```

This avoids downloading the local LaMini model and uses Gemini for every AI operation.

To follow the document's local explanation design:

```text
EXPLANATION_PROVIDER=auto
```

In `auto`, EduGenie tries `MBZUAI/LaMini-Flan-T5-783M` locally for `/explain`. If that model cannot be loaded, it falls back to Gemini.

To require local explanation only:

```text
EXPLANATION_PROVIDER=local
```

The local model is downloaded by Hugging Face the first time it is needed.

## 7. Run the application

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 8. Test the application

### Browser test

Try:

- Ask a Question: `Which is the largest ocean?`
- Explain a Topic: `Pythagoras theorem`
- Generate Quiz: paste a paragraph about photosynthesis
- Summarize Text: paste a long educational paragraph
- Recommend Learning Path: `SQL`

### Health test

Open:

```text
http://127.0.0.1:8000/health
```

### Automated tests

```bash
pytest
```

These tests do not call Gemini; they check the app, homepage and request validation.

## 9. API examples

### Q&A

```bash
curl -X POST http://127.0.0.1:8000/qa ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is photosynthesis?\"}"
```

macOS/Linux:

```bash
curl -X POST http://127.0.0.1:8000/qa \
  -H "Content-Type: application/json" \
  -d '{"question":"What is photosynthesis?"}'
```

### Explanation

```json
POST /explain

{
  "topic": "Pythagoras theorem",
  "level": "beginner"
}
```

### Quiz

```json
POST /quiz

{
  "text": "Photosynthesis is the process by which green plants convert light energy into chemical energy.",
  "num_questions": 3
}
```

### Summary

```json
POST /summarize

{
  "text": "Your educational passage here...",
  "max_words": 150
}
```

### Learning path

```json
POST /learn/recommendations

{
  "topic": "SQL",
  "level": "beginner",
  "duration_weeks": 8
}
```

## 10. Troubleshooting

### `GEMINI_API_KEY is not configured`

Check that:

1. The file is named `.env`.
2. It is in the same directory as `main.py`.
3. `GEMINI_API_KEY` has a valid key.
4. Restart Uvicorn after changing `.env`.

### Gemini model not available

Change `GEMINI_MODEL` in `.env` to a model available to your Google AI API account. Keep the model configurable rather than hard-coding an obsolete model name.

### Local LaMini model is slow

Set:

```text
EXPLANATION_PROVIDER=gemini
```

The local model is intentionally lazy-loaded only when `/explain` needs it.

### Port already in use

Run:

```bash
uvicorn main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

## 11. Docker

Build:

```bash
docker build -t edugenie .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env edugenie
```

Open:

```text
http://127.0.0.1:8000
```

For a small cloud deployment, keep the Gemini key in the hosting provider's secret/environment-variable manager rather than putting it into source code.

## Architecture

```text
Browser
   |
   | HTTP POST
   v
FastAPI (main.py)
   |
   +--> /qa ----------------------> qna.py --------------------+
   |                                                          |
   +--> /explain --> explanation_module.py --> LaMini/Gemini  |
   |                                                          |
   +--> /quiz --------------------> quiz_module.py -----------+
   |                                                          |
   +--> /summarize ---------------> summary_module.py --------+
   |                                                          |
   +--> /learn/recommendations ---> learning_path.py ---------+
                                                              |
                                                              v
                                                     gemini_service.py
                                                              |
                                                              v
                                                       Google Gemini API
```

## Implementation notes

The supplied documentation names Gemini 1.5 Pro. That model reference is historical; this project therefore exposes the Gemini model as `GEMINI_MODEL` and uses a current configurable model by default. The code uses Google's current `google-genai` Python SDK rather than the older `google-generativeai` package.

The quiz endpoint uses Gemini structured JSON output plus Pydantic validation. This follows the document's requirement for machine-readable quiz JSON while making malformed model output less likely to reach the frontend.

The frontend is intentionally plain HTML/CSS/JavaScript, matching the supplied architecture instead of introducing a heavier JavaScript framework.

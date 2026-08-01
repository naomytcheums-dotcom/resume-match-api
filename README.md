# Resume Match API

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)
![OpenAI SDK](https://img.shields.io/badge/OpenAI_SDK-412991?style=flat&logo=openai&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=white)

A small, focused REST API: upload a resume and a job description, get back a compatibility score, matching and missing skills, notable strengths, and an honest summary — an ATS-style scoring endpoint. Built as a standalone backend service — no frontend, no database.

## Endpoint

### `POST /api/match`

**Headers**
- `X-API-Key` — required only if `API_ACCESS_KEY` is set on the server

**Body** — `multipart/form-data`
- `resume` — the resume file, `.pdf`, `.docx`, or `.txt`
- `job_description` — plain text of the job posting

**Response**
```json
{
  "match_score": 85,
  "matching_skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"],
  "missing_skills": ["Kafka", "Message queue systems"],
  "strengths": ["Direct experience with the exact target tech stack..."],
  "summary": "Jane is a strong fit for this role, with direct overlap in..."
}
```

`match_score` is 0-100. Every field is grounded only in what's actually present in both documents — the model is instructed never to guess at skills the resume doesn't mention.

**Errors**
- `422` — missing `job_description`, unsupported resume file type, or a file with no extractable text
- `401` — missing or invalid `X-API-Key` (only if access control is enabled)
- `502` — the LLM request failed (quota, network, misconfigured key) — the response includes a clean, truncated reason

### `GET /api/health`

Returns `{"status": "ok"}`. Useful for uptime checks.

### `GET /docs`

Interactive Swagger UI — try the API directly from your browser.

## Example

```bash
curl -X POST https://your-deployment.onrender.com/api/match \
  -H "X-API-Key: your-key-if-set" \
  -F "resume=@resume.pdf" \
  -F "job_description=We are looking for a Senior Backend Engineer with Python and AWS experience..."
```

## Tech stack

FastAPI, Pydantic, pypdf (PDF text extraction), python-docx (DOCX text extraction), OpenAI-compatible LLM client (works with OpenAI, Google Gemini, Groq, or any OpenAI-compatible endpoint).

## Running locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in your own LLM key
uvicorn app.main:app --reload --port 8098
```

Then open `http://localhost:8098/docs` to try it interactively.

## Deploying

**Render:**
- New Web Service, root directory: repo root (no subfolder)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`, `API_ACCESS_KEY` (optional), `CORS_ORIGINS`

No frontend, no database — this is a pure backend API, deployable on its own.

## Status

This is an MVP built for portfolio purposes. It requires your own LLM API key — no credentials are shared or included. `API_ACCESS_KEY` is optional; leave it empty for an open demo, or set it to require callers to authenticate. Note: scanned/image-only PDFs (no text layer) can't be parsed — this uses text extraction, not OCR.

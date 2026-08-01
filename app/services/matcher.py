import json
import re

from app.config import settings
from app.services.llm_client import LLMNotConfiguredError, get_client

SYSTEM_PROMPT = """You compare a resume against a job description and score how well
they match, from the perspective of an experienced technical recruiter.

Respond with ONLY valid JSON, no markdown fences, in this exact shape:
{
  "match_score": 0-100,
  "matching_skills": ["skill present in both resume and job description"],
  "missing_skills": ["skill required by the job but not found in the resume"],
  "strengths": ["a specific strength of this candidate for this specific role"],
  "summary": "a short, honest paragraph explaining the score"
}

Rules:
- Base match_score only on what's actually in both documents — don't guess at
  skills the resume doesn't mention just because they're common in the field.
- matching_skills and missing_skills should list concrete skills/technologies/
  qualifications, not vague categories.
- Be honest and specific in the summary, including real gaps if they exist."""


class MatchError(RuntimeError):
    pass


def _strip_code_fence(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def _as_str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def match_resume_to_job(resume_text: str, job_description: str) -> dict:
    try:
        client = get_client()
    except LLMNotConfiguredError as exc:
        raise MatchError(str(exc)) from exc

    user_prompt = (
        f"RESUME:\n{resume_text[:12000]}\n\n"
        f"JOB DESCRIPTION:\n{job_description[:6000]}"
    )

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1536,
        )
    except Exception as exc:  # noqa: BLE001 — surfaced as a clean API error
        message = str(exc).split("\n")[0][:200]
        raise MatchError(f"Match scoring request failed: {message}") from exc

    content = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(_strip_code_fence(content))
    except json.JSONDecodeError:
        parsed = {}

    try:
        match_score = int(round(float(parsed.get("match_score", 0))))
    except (TypeError, ValueError):
        match_score = 0
    match_score = max(0, min(100, match_score))

    summary = str(parsed.get("summary", "")).strip()
    if not summary:
        summary = "No summary was returned by the model."

    return {
        "match_score": match_score,
        "matching_skills": _as_str_list(parsed.get("matching_skills")),
        "missing_skills": _as_str_list(parsed.get("missing_skills")),
        "strengths": _as_str_list(parsed.get("strengths")),
        "summary": summary,
    }

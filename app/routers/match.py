from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from app.auth import require_api_key
from app.schemas import MatchResponse
from app.services.matcher import MatchError, match_resume_to_job
from app.services.text_extractor import TextExtractionError, extract_text

router = APIRouter(prefix="/api", tags=["match"], dependencies=[Depends(require_api_key)])


@router.post("/match", response_model=MatchResponse)
async def match(resume: UploadFile, job_description: str = Form(...)):
    if not job_description.strip():
        raise HTTPException(422, "job_description is required.")

    data = await resume.read()

    try:
        resume_text = extract_text(data, resume.filename or "")
    except TextExtractionError as exc:
        raise HTTPException(422, str(exc)) from exc

    try:
        result = match_resume_to_job(resume_text, job_description)
    except MatchError as exc:
        raise HTTPException(502, str(exc)) from exc

    return MatchResponse(**result)

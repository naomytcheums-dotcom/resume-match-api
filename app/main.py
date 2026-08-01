from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import match

app = FastAPI(
    title="Resume Match API",
    description="AI-powered resume-to-job matching — upload a resume and a job description, get back a compatibility score and gap analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

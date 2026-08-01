import hmac

from fastapi import Header, HTTPException

from app.config import settings


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if not settings.api_access_key:
        return
    if not hmac.compare_digest(x_api_key, settings.api_access_key):
        raise HTTPException(401, "Invalid or missing X-API-Key header.")

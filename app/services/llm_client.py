from openai import OpenAI

from app.config import settings


class LLMNotConfiguredError(RuntimeError):
    pass


def get_client() -> OpenAI:
    if not settings.llm_api_key:
        raise LLMNotConfiguredError("LLM_API_KEY is not configured on the server.")
    kwargs = {"api_key": settings.llm_api_key}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return OpenAI(**kwargs)

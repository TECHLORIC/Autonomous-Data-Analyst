import asyncio
import json
import logging
import re
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Provider-independent interface for LLM operations."""

    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 4,
    ) -> str:
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt + "\nIMPORTANT: You must return ONLY valid JSON matching the exact schema requested.",
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

        for attempt in range(max_retries):
            response = await self.client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                if not content:
                    raise RuntimeError("LLM returned an empty response.")
                    
                # Strip markdown json blocks if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                return content.strip()

            # Handle Rate Limit (HTTP 429)
            if response.status_code == 429 and attempt < max_retries - 1:
                wait_seconds = 5.0
                try:
                    retry_after = response.headers.get("retry-after")
                    if retry_after:
                        wait_seconds = float(retry_after) + 0.5
                    else:
                        error_body = response.text
                        match = re.search(r"try again in (\d+(\.\d+)?)s", error_body)
                        if match:
                            wait_seconds = float(match.group(1)) + 1.0
                        else:
                            wait_seconds = 2.0 ** (attempt + 1)
                except Exception:
                    wait_seconds = 5.0

                logger.warning(
                    "Groq rate limit (429) encountered. Retrying in %.2fs (attempt %d/%d)...",
                    wait_seconds, attempt + 1, max_retries
                )
                await asyncio.sleep(wait_seconds)
                continue
                
            raise RuntimeError(f"Groq API error ({response.status_code}): {response.text}")
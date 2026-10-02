import json
import httpx
from app.core.config import settings

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

        response = await self.client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Groq API error: {response.text}")
            
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
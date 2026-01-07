import asyncio
import httpx
import json

from app.infrastructure.celery.app import celery_app
from app.core.config import settings


API_KEY = settings.LLM_API_KEY  
API_URL = settings.LLM_API_URL
MODEL_NAME = settings.LLM_MODEL_NAME

async def call_external_llm(prompt: str, model: str = MODEL_NAME) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"""You are a professional screenplay writer.

                            Convert the following story into a short movie script.
                            Use proper screenplay format with scenes and dialogues.

                            STORY:{prompt}"""
            }
        ],
        "reasoning": {"enabled": True}
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


@celery_app.task(bind=True)
def process_script_task(self, script_id: str, script_content: str):

    print(f"Processing script {script_id}...")
    try:
        result = asyncio.run(call_external_llm(script_content))
        print(f"Script {script_id} processed successfully")
        return {"script_id": script_id, "result": result}
    except Exception as e:
        print(f"Script {script_id} failed: {e}")
        return {"script_id": script_id, "error": str(e)}
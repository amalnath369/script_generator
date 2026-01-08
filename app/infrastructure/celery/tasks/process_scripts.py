import asyncio
import httpx
import json

from uuid import uuid4
from datetime import datetime

from app.infrastructure.celery.app import celery_app
from app.core.config import settings
from app.infrastructure.database.session import AsyncSessionLocal as async_session_maker
from app.infrastructure.repositories.generate_script_repo import IGeneratedScriptRepository
from app.infrastructure.database.uow import SqlAlchemyUnitOfWork
from app.domain.entities.enums import ScriptStatus



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


async def process_and_save_script(script_id: str, script_name: str, script_content: str, script_tags: list[str]):
    try:
        # Call LLM
        generated_content = await call_external_llm(script_content)
        
        # Save to database
        async with SqlAlchemyUnitOfWork() as uow:
            from app.domain.entities.generated_script import GeneratedScript
            
            generated_script = GeneratedScript(
                id=str(uuid4()),
                script_id=script_id,
                name=f"Generated: {script_name}",
                content=generated_content,
                tags=script_tags,
                status=ScriptStatus.COMPLETED,
                model_name=MODEL_NAME
            )
            
            await uow.generated_scripts.save(generated_script)
            
            # Update original script status
            script = await uow.scripts.get_by_id(script_id)
            if script:
                script.status = ScriptStatus.COMPLETED  # mutate entity
                await uow.scripts.update(script)        # pass entity
                await uow.commit()
            
        print(f"✅ Script {script_id} processed and saved successfully")
        return {"script_id": script_id, "status": "success"}
        
    except Exception as e:
        print(f"❌ Script {script_id} failed: {e}")
        
        # Update script status to FAILED
        try:
            async with SqlAlchemyUnitOfWork() as uow:
                script = await uow.scripts.get_by_id(script_id)
                if script:
                    script.status = ScriptStatus.FAILED  # mutate entity
                    await uow.scripts.update(script)  
                    await uow.commit()
        except Exception as update_error:
            print(f"Failed to update script status: {update_error}")
        
        return {"script_id": script_id, "status": "failed", "error": str(e)}



@celery_app.task(bind=True, name = "process_script_task")
def process_script_task(self, script_id: str, script_name: str, script_content: str, script_tags: list[str]):
    """Celery task to process script in background."""
    print(f"🚀 Starting processing for script {script_id}...")
    result = asyncio.run(process_and_save_script(script_id, script_name, script_content, script_tags))
    return result
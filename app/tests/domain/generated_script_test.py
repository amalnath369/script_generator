from datetime import datetime
from app.domain.entities.generated_script import GeneratedScript
from app.domain.entities.enums import ScriptStatus


def test_generated_script_creation_success():
    now = datetime.utcnow()

    generated = GeneratedScript(
        id="gen-1",
        script_id="script-1",
        name="Generated Script",
        content="Generated screenplay",
        tags=["ai", "screenplay"],
        status=ScriptStatus.COMPLETED,
        model_name="gpt-4",
        created_at=now,
        updated_at=now
    )

    assert generated.id == "gen-1"
    assert generated.script_id == "script-1"
    assert generated.model_name == "gpt-4"
    assert generated.status == ScriptStatus.COMPLETED
    assert generated.created_at == now

import pytest
from app.domain.entities.script import Script
from app.domain.entities.enums import ScriptStatus


def test_script_creation_success():
    script = Script(
        id="script-1",
        name="Test Script",
        content="This is a valid screenplay content",
        tags=["drama", "action"]
    )

    assert script.id == "script-1"
    assert script.name == "Test Script"
    assert script.status == ScriptStatus.PENDING


def test_script_creation_fails_without_id():
    with pytest.raises(ValueError, match="Script id cannot be empty"):
        Script(
            id="",
            name="Test Script",
            content="Some content",
            tags=[]
        )


def test_script_creation_fails_without_name():
    with pytest.raises(ValueError, match="Script name cannot be empty"):
        Script(
            id="script-1",
            name="",
            content="Some content",
            tags=[]
        )


def test_script_creation_fails_without_content():
    with pytest.raises(ValueError, match="Script content cannot be empty"):
        Script(
            id="script-1",
            name="Test Script",
            content="",
            tags=[]
        )


def test_script_content_line_limit_exceeded():
    content = "\n".join(["line"] * 1001)

    with pytest.raises(ValueError, match="cannot exceed 1000 lines"):
        Script(
            id="script-1",
            name="Test Script",
            content=content,
            tags=[]
        )


def test_script_update_status_creates_new_instance():
    script = Script(
        id="script-1",
        name="Test Script",
        content="Valid content",
        tags=[]
    )

    updated = script.update_status(ScriptStatus.COMPLETED)

    assert updated.status == ScriptStatus.COMPLETED
    assert updated.id == script.id
    assert updated is not script  # immutability check

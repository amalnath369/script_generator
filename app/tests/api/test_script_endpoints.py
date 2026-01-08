import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_script(async_test_client: AsyncClient):
    """Test POST /api/scripts - Create a new script"""
    payload = {
        "name": "Test Script",
        "content": "print('Hello World')",
        "tags": ["python", "test"]
    }
    
    response = await async_test_client.post("/api/scripts", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["content"] == payload["content"]
    assert data["tags"] == payload["tags"]
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_script_validation_error(async_test_client: AsyncClient):
    """Test POST /api/scripts with invalid data"""
    payload = {
        "name": "",  # Empty name should fail validation
        "content": "test"
    }
    
    response = await async_test_client.post("/api/scripts", json=payload)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_script(async_test_client: AsyncClient):
    """Test GET /api/scripts/{script_id} - Retrieve a script"""
    # First create a script
    create_payload = {
        "name": "Test Script",
        "content": "print('test')",
        "tags": ["test"]
    }
    create_response = await async_test_client.post("/api/scripts", json=create_payload)
    script_id = create_response.json()["id"]
    
    # Now retrieve it
    response = await async_test_client.get(f"/api/scripts/{script_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == script_id
    assert data["name"] == create_payload["name"]
    assert data["content"] == create_payload["content"]


@pytest.mark.asyncio
async def test_get_script_not_found(async_test_client: AsyncClient):
    """Test GET /api/scripts/{script_id} with non-existent ID"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    response = await async_test_client.get(f"/api/scripts/{fake_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_scripts_pagination(async_test_client: AsyncClient):
    """Test GET /api/scripts with pagination"""
    # Create 5 scripts
    for i in range(5):
        payload = {
            "name": f"Script {i}",
            "content": f"content {i}",
            "tags": ["test"]
        }
        await async_test_client.post("/api/scripts", json=payload)
    
    # Test first page
    response = await async_test_client.get("/api/scripts?skip=0&limit=3")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_more" in data
    assert len(data["items"]) == 3
    assert data["total"] >= 5
    assert data["skip"] == 0
    assert data["limit"] == 3
    assert data["has_more"] is True


@pytest.mark.asyncio
async def test_list_scripts_second_page(async_test_client: AsyncClient):
    """Test pagination - second page"""
    # Create 5 scripts
    for i in range(5):
        payload = {
            "name": f"Script {i}",
            "content": f"content {i}",
            "tags": []
        }
        await async_test_client.post("/api/scripts", json=payload)
    
    # Test second page
    response = await async_test_client.get("/api/scripts?skip=3&limit=3")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2  # Only 2 items left
    assert data["skip"] == 3
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_list_scripts_empty(async_test_client: AsyncClient):
    """Test GET /api/scripts when no scripts exist"""
    response = await async_test_client.get("/api/scripts?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_update_script_status(async_test_client: AsyncClient):
    """Test PUT /api/scripts/{script_id} - Update script"""
    # Create a script
    create_payload = {
        "name": "Test Script",
        "content": "print('test')",
        "tags": []
    }
    create_response = await async_test_client.post("/api/scripts", json=create_payload)
    script_id = create_response.json()["id"]
    
    # Update the script
    update_payload = {
        "status": "completed"
    }
    response = await async_test_client.put(
        f"/api/scripts/{script_id}",
        json=update_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == script_id
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_update_script_multiple_fields(async_test_client: AsyncClient):
    """Test updating multiple fields at once"""
    # Create a script
    create_payload = {
        "name": "Original Name",
        "content": "original content",
        "tags": ["old"]
    }
    create_response = await async_test_client.post("/api/scripts", json=create_payload)
    script_id = create_response.json()["id"]
    
    # Update multiple fields
    update_payload = {
        "name": "Updated Name",
        "content": "updated content",
        "tags": ["new", "updated"],
        "status": "completed"
    }
    response = await async_test_client.put(
        f"/api/scripts/{script_id}",
        json=update_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["content"] == "updated content"
    assert data["tags"] == ["new", "updated"]
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_update_script_not_found(async_test_client: AsyncClient):
    """Test updating non-existent script"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    update_payload = {"status": "completed"}
    
    response = await async_test_client.put(
        f"/api/scripts/{fake_id}",
        json=update_payload
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_script_empty_payload(async_test_client: AsyncClient):
    """Test updating with empty data"""
    # Create a script
    create_payload = {
        "name": "Test",
        "content": "test",
        "tags": []
    }
    create_response = await async_test_client.post("/api/scripts", json=create_payload)
    script_id = create_response.json()["id"]
    
    # Try to update with empty payload
    response = await async_test_client.put(
        f"/api/scripts/{script_id}",
        json={}
    )
    
    assert response.status_code == 400
    assert "no update data" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_script(async_test_client: AsyncClient):
    """Test DELETE /api/scripts/{script_id}"""
    # Create a script
    create_payload = {
        "name": "Script to Delete",
        "content": "delete me",
        "tags": []
    }
    create_response = await async_test_client.post("/api/scripts", json=create_payload)
    script_id = create_response.json()["id"]
    
    # Delete it
    response = await async_test_client.delete(f"/api/scripts/{script_id}")
    
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = await async_test_client.get(f"/api/scripts/{script_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_script_not_found(async_test_client: AsyncClient):
    """Test deleting non-existent script"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    response = await async_test_client.delete(f"/api/scripts/{fake_id}")
    
    assert response.status_code == 404


# app/tests/repositories/test_script_repository.py - Direct repository tests
import pytest
from app.core.unit_of_work import UnitOfWork


@pytest.mark.asyncio
async def test_repository_create(uow: UnitOfWork):
    """Test creating script via repository"""
    script_data = {
        "name": "Test Script",
        "content": "test content",
        "tags": ["test"],
        "status": "pending"
    }
    
    script = await uow.scripts.create(script_data)
    await uow.commit()
    
    assert script.name == script_data["name"]
    assert script.content == script_data["content"]
    assert script.id is not None


@pytest.mark.asyncio
async def test_repository_get_by_id(uow: UnitOfWork):
    """Test getting script by ID via repository"""
    # Create a script
    script_data = {
        "name": "Test",
        "content": "test",
        "tags": [],
        "status": "pending"
    }
    created_script = await uow.scripts.create(script_data)
    await uow.commit()
    
    # Retrieve it
    retrieved_script = await uow.scripts.get_by_id(created_script.id)
    
    assert retrieved_script is not None
    assert retrieved_script.id == created_script.id
    assert retrieved_script.name == created_script.name


@pytest.mark.asyncio
async def test_repository_update(uow: UnitOfWork):
    """Test updating script via repository"""
    # Create a script
    script_data = {
        "name": "Original",
        "content": "original",
        "tags": [],
        "status": "pending"
    }
    script = await uow.scripts.create(script_data)
    await uow.commit()
    
    # Update it
    update_data = {"status": "completed"}
    updated_script = await uow.scripts.update(script.id, update_data)
    await uow.commit()
    
    assert updated_script.status == "completed"
    assert updated_script.name == "Original"  # Unchanged fields stay same


@pytest.mark.asyncio
async def test_repository_delete(uow: UnitOfWork):
    """Test deleting script via repository"""
    # Create a script
    script_data = {
        "name": "To Delete",
        "content": "delete",
        "tags": [],
        "status": "pending"
    }
    script = await uow.scripts.create(script_data)
    await uow.commit()
    
    # Delete it
    deleted = await uow.scripts.delete(script.id)
    await uow.commit()
    
    assert deleted is True
    
    # Verify it's gone
    retrieved = await uow.scripts.get_by_id(script.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_repository_get_all_pagination(uow: UnitOfWork):
    """Test pagination in repository"""
    # Create 10 scripts
    for i in range(10):
        script_data = {
            "name": f"Script {i}",
            "content": f"content {i}",
            "tags": [],
            "status": "pending"
        }
        await uow.scripts.create(script_data)
    await uow.commit()
    
    # Get first page
    scripts, total = await uow.scripts.get_all(skip=0, limit=5)
    
    assert len(scripts) == 5
    assert total == 10
    
    # Get second page
    scripts_page2, total2 = await uow.scripts.get_all(skip=5, limit=5)
    
    assert len(scripts_page2) == 5
    assert total2 == 10


# pytest.ini - Configuration
"""
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
filterwarnings =
    ignore::DeprecationWarning
"""


# Run tests with:
# pytest -v app/tests/api/test_script_endpoints.py
# pytest -v app/tests/repositories/test_script_repository.py
# pytest -v app/tests/  # Run all tests
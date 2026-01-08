from fastapi import APIRouter, Depends, status, HTTPException, Request
from uuid import uuid4


from app.domain.uow.unit_of_work import UnitOfWork
from app.interfaces.v1.api.dependencies.dependencies import get_uow
from app.interfaces.v1.api.dependencies.pagination import PaginationParams
from app.interfaces.v1.api.dependencies.rate_limit import limiter
from app.interfaces.v1.schemas.script_schema import CreateScriptRequest,ScriptResponse

from app.application.use_cases.script.create_script  import CreateScriptUseCase
from app.application.use_cases.script.delete_scripts import DeleteScriptsUseCase
from app.application.use_cases.script.read_scripts import ReadScriptsUseCase
from app.application.use_cases.script.list_all import ListAllScriptsUseCase
from app.application.use_cases.script.update_script import UpdateScriptsUseCase

from app.application.exceptions.exception import (ScriptCreationError, ScriptNotFoundError,
                                ScriptValidationError, ScriptPersistenceError)




router = APIRouter(prefix="/scripts", tags=["Scripts"])


@router.post("/", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_script(request: Request, payload: CreateScriptRequest,uow: UnitOfWork = Depends(get_uow)):

    use_case = CreateScriptUseCase(uow)

    try:
        script = await use_case.execute(
        script_id=str(uuid4()),
        name=payload.name,
        content=payload.content,
        tags=payload.tags,
    )

        return ScriptResponse(
            id=script.id,
            name=script.name,
            content=script.content,
            tags=script.tags,
            status=script.status,
        )
    except ScriptValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    except ScriptCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except ScriptPersistenceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
    except  Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. error : {str(e)}",
        )
    

@router.get('/list_all', response_model=list[ScriptResponse], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def list_all_scripts(request: Request, pagination: PaginationParams = Depends(), uow: UnitOfWork = Depends(get_uow)):
    use_case = ListAllScriptsUseCase(uow)

    try:
        total, scripts = await use_case.execute(limit=pagination.limit, offset=pagination.offset)

        return [
            ScriptResponse(
                id=script.id,
                name=script.name,
                content=script.content,
                tags=script.tags,
                status=script.status,
            )
            for script in scripts
        ]

    except Exception as e:
        import traceback
        print("FULL ERROR:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    




@router.get("/{script_id}", response_model=ScriptResponse, status_code=status.HTTP_200_OK) 
async def read_script(script_id: str, uow: UnitOfWork = Depends(get_uow)):
    use_case = ReadScriptsUseCase(uow)

    try:
        script = await use_case.execute(script_id=script_id)

        return ScriptResponse(
            id=script.id,
            name=script.name,
            content=script.content,
            tags=script.tags,
            status=script.status,
        )

    except ScriptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. error : {str(e)}",
        )
    


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script(script_id: str, uow: UnitOfWork = Depends(get_uow)):
    use_case = DeleteScriptsUseCase(uow)

    try:
        await use_case.execute(script_id=script_id)

    except ScriptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. error : {str(e)}",
        )



@router.put("/{script_id}/status", status_code=status.HTTP_200_OK)
async def update_script_status(script_id: str, name=None, content=None, tags=None, uow: UnitOfWork = Depends(get_uow)):

    use_case = UpdateScriptsUseCase(uow)

    try:
        await use_case.execute(script_id=script_id, name=name, content=content, tags=tags)

    except ScriptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        import traceback
        print("FULL ERROR:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
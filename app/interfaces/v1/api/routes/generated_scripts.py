from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request


from app.domain.uow.unit_of_work import UnitOfWork
from app.interfaces.v1.api.dependencies.dependencies import get_uow
from app.interfaces.v1.api.dependencies.pagination import PaginationParams
from app.interfaces.v1.api.dependencies.rate_limit import limiter
from app.interfaces.v1.schemas.generate_script_schema import CreateGeneratedScriptRequest, GeneratedScriptResponse

from app.application.use_cases.generated_script.create_generated_script import CreateGeneratedScriptUseCase
from app.application.use_cases.generated_script.read_generated_script import ReadGeneratedScriptUseCase 
from app.application.use_cases.generated_script.list_generated_scripts import ListGeneratedScriptsByScriptUseCase
from app.application.use_cases.generated_script.read_generate_script_with_script_id import ReadGenerateScriptWithScriptIdUseCase
from app.application.use_cases.generated_script.delete_generate_script import DeleteGenerateScriptUseCase

from app.application.exceptions.exception import (GeneratedScriptValidationError, GeneratedScriptPersistenceError,
                                GeneratedScriptNotFoundError)


router = APIRouter(prefix="/generated-scripts", tags=["Generated Scripts"])


@router.get("/list_all", response_model=List[GeneratedScriptResponse], status_code=200)
@limiter.limit("10/minute")
async def list_all_generated_scripts(request: Request,pagination: PaginationParams = Depends(), uow: UnitOfWork = Depends(get_uow)):
    try:
        async with uow:
            total, generated_scripts = await uow.generated_scripts.list_all(limit=pagination.limit, offset=pagination.offset)

        return [
            GeneratedScriptResponse.model_validate(gen_script)
            for gen_script in generated_scripts
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@router.get("/{generated_script_id}", response_model=GeneratedScriptResponse, status_code=200)
@limiter.limit("5/minute")
async def get_generated_script(request: Request, generated_script_id: str, uow: UnitOfWork = Depends(get_uow)):
    use_case = ReadGeneratedScriptUseCase(uow)

    try:
        generated_script = await use_case.execute(generated_script_id=generated_script_id)
        return GeneratedScriptResponse.model_validate(generated_script)

    except GeneratedScriptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    


@router.get("/by-script/{script_id}", response_model = Optional[List[GeneratedScriptResponse]], status_code=200)
@limiter.limit("10/minute")
async def generated_scripts_by_script(request: Request, script_id: str, uow: UnitOfWork = Depends(get_uow)):
    use_case = ReadGenerateScriptWithScriptIdUseCase(uow)

    try:
        generated_scripts = await use_case.execute(script_id=script_id)
        
        return [
    GeneratedScriptResponse(
        script_id=s.script_id,
        name=s.name,
        content=s.content,
        tags=s.tags or [],
        status=s.status.value,   
        model_name=s.model_name,
        id=s.id,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )
    for s in generated_scripts
]

    except Exception as e:
        import traceback
        print("FULL ERROR:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    


@router.delete("/{generated_script_id}", status_code=204)
async def delete_generated_script(generated_script_id: str, uow: UnitOfWork = Depends(get_uow)):

    use_case = DeleteGenerateScriptUseCase(uow)

    try:
        await use_case.execute(generated_script_id=generated_script_id)
    except GeneratedScriptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
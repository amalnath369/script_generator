from abc import ABC, abstractmethod
from app.domain.repositories.script_repository import ScriptRepository
from app.domain.repositories.genrated_script_repository import GeneratedScriptRepository

class UnitOfWork(ABC):
    scripts: ScriptRepository
    generated_scripts: GeneratedScriptRepository
    

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass

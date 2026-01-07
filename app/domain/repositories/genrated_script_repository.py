from abc import ABC, abstractmethod
from app.domain.entities.generated_script import GeneratedScript    
from typing import Optional, List




class GeneratedScriptRepository(ABC):

    @abstractmethod
    async def save(self, script: "GeneratedScript") -> None:
        pass

    @abstractmethod
    async def get_by_id(self, script_id: str) -> Optional["GeneratedScript"]:
        pass
    
    @abstractmethod
    async def update(self, script_id: str, new_status: str) -> None:
        pass

    @abstractmethod
    async def delete(self, script_id: str) -> None:
        pass

    @abstractmethod
    async def list_all(self) -> List["GeneratedScript"]:
        pass
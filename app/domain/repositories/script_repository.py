from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.script import Script



class ScriptRepository(ABC):

    @abstractmethod
    async def save(self, script: "Script") -> None:
        pass

    @abstractmethod
    async def get_by_id(self, script_id: str) -> Optional["Script"]:
        pass
    
    @abstractmethod
    async def update(self, script: "Script") -> None:
        pass

    @abstractmethod
    async def delete(self, script_id: str) -> None:
        pass

    @abstractmethod
    async def list_all(self) -> List["Script"]:
        pass
from abc import ABC,abstractmethod
from typing import Any

class ISave(ABC):
    @abstractmethod
    async def save(self, data: list[dict[str, Any]]):pass
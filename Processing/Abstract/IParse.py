from abc import ABC,abstractmethod
from typing import Any

class IParse(ABC):
    @abstractmethod
    def parse(self,html:str) -> list[dict[str, Any]]: pass
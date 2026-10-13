from abc import ABC,abstractmethod

class ILinkQueue(ABC):
    @abstractmethod
    def enqueue(self,link:str, source:str, error:str):pass
    @abstractmethod
    def dequeue_pending(self)->list:pass
    @abstractmethod
    def mark_resolved(self,link): pass
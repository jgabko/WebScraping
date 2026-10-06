from abc import ABC,abstractmethod

class ILinkQueue(ABC):
    @abstractmethod
    def enqueue(link:str, source:str, error:str):pass
    @abstractmethod
    def dequeue_pending()->list:pass
    @abstractmethod
    def mark_resolved(link): pass
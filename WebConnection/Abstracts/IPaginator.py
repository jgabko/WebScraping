from abc import ABC,abstractmethod

class IPaginator(ABC):
    @abstractmethod
    def next_link(page_number:int,current_link:str)->str|None: pass
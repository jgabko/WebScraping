from abc import ABC,abstractmethod

class IPaginator(ABC):
    @abstractmethod
    def next_link(self,page_number,current_link)->str|None: pass
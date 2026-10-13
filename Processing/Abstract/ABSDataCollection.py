import abc
from abc import abstractmethod, abstractproperty
from typing import Any
from WebConnection.Abstracts import IBrowser,AbsFactoryPage
from Processing.Abstract.IParse import IParse
from WebConnection.Abstracts.IPaginator import IPaginator


class ABSDataCollection(ABC):
    def __init__(self,browser,pagefactory,parser,linkexp,paginator):
        self.browser= browser
        self.pagefactory = pagefactory
        self.parser= parser
        self.linkexp=linkexp
        self.paginator = paginator


    @abstractmethod
    def collectdata(self)->list[dict]:pass

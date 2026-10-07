import abc
from abc import abstractmethod, abstractproperty
from typing import any
from WebConnection.Abstracts import IBrowser, IParse,AbsFactoryPage

class ABSDataCollection(ABC):
    @abstractmethod
    def __init__(self,browser,pageFactory,parser,linkexp):
        self.browser= browser
        self.pageFactory = pageFactory
        self.parser= parser
        self.linkexp=linkexp


    @abstractmethod
    def collectdata(self)->dict:pass

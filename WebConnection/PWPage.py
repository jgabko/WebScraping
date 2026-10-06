from WebConnection.Abstracts.IPage import IPage
from WebConnection.Abstracts.IBrowser import IBrowser

class PWPage(IPage):
    def __init__(self,browser:IBrowser):
        self._Browser:IBrowser=browser
        self.page:IPage|None


    async def goto(link:str)->IPage:
        

    
    async def content(): pass

    
    async def closepage(): pass
from abc import abstractmethod, ABC
from sqlalchemy.ext.asyncio import AsyncSession

class TagRepo(ABC):
    def __init__(self, session:AsyncSession):
        self.session=session
    @abstractmethod
    async def save(self):
        pass
        
    @abstractmethod
    async def get_all_tags(self):
        pass
    @abstractmethod
    async def delete_tag(self, tag_id:int):
        pass
    @abstractmethod
    async def get_by_id(self , tag_id:int):
        pass
    @abstractmethod
    async def get_by_name(self,model):
        pass
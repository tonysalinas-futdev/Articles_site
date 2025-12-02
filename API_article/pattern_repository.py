from abc import abstractmethod, ABC
from sqlalchemy.ext.asyncio import AsyncSession


class ArticleRepo(ABC):
    def __init__(self, session:AsyncSession):
        self.session=session

    @abstractmethod
    async def get_all_tags(self):
        pass

    @abstractmethod
    async def get_by_id(self):
        pass

    @abstractmethod
    async def get_by_title(self):
        pass


    @abstractmethod
    async def get_all(self):
        pass
    
    @abstractmethod
    async def create_article(self):
        pass

    @abstractmethod
    async def search_by_filters(self):
        pass

    @abstractmethod
    async def create_tag(self):
        pass
from abc import abstractmethod, ABC
from sqlalchemy.ext.asyncio import AsyncSession


class ArticleRepo(ABC):

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
    async def save(self):
        pass

    @abstractmethod
    async def search_by_filters(self):
        pass

    @abstractmethod
    async def delete(article):
        pass




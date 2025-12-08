from sqlalchemy import select
from app.database.models import Tags
from app.repositorys.tag_repository import  TagRepo
from sqlalchemy.ext.asyncio import AsyncSession


    
class SqlAlchemyTagRepo(TagRepo):
    def __init__(self, session:AsyncSession):
        self.session=session
    async def get_by_name(self,name:str):
        stmt=select(Tags).where(Tags.name==name)
        result=await self.session.execute(stmt)
        tag=result.scalar_one_or_none()
        return tag
    

    async def get_all_tags(self):
        stmt=select(Tags)
        result=await self.session.execute(stmt)
        tags=result.scalars().all()
        
        return tags
    
    async def save(self, tag:Tags):
        
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def get_by_id(self,tag_id:int):
        stmt=select(Tags).where(Tags.id==tag_id)
        result=await self.session.execute(stmt)
        tag=result.scalar_one_or_none()
        return tag
    

    #Función para eliminar un tag
    async def delete_tag(self, tag:Tags):
        try:
            await self.session.delete(tag)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
from sqlalchemy.orm import selectinload
from sqlalchemy import select,and_
import schemas
from database.models import Article,Tags
from repositorys.article_repository import ArticleRepo
from sqlalchemy.ext.asyncio import AsyncSession

class SqlalchemyArticleRepo(ArticleRepo):
    def __init__(self, session:AsyncSession):
        self.session=session
    #Funcion para crear un artículo
    async def get_by_id(self,id:int):
        stmt=select(Article).options(selectinload(
            Article.pics,),
            selectinload(Article.tags)
            
            ).where(Article.id==id)

        result= await self.session.execute(stmt)
        article=result.scalar_one_or_none()

        return article

    #Función para obtener un artículo por su títutlo exacto
    async def get_by_title(self,title:str):
        stmt=select(Article).where(Article.title==title).order_by(Article.date)
        result=await self.session.execute(stmt)
        article=result.scalar_one_or_none()
        return article
    
    #Función para obtener todos los artículos , utilizando paginación por cursor
    async def get_all(self, cursor:int=0):
        stmt=select(Article).options(
            selectinload(Article.pics),
            selectinload(Article.tags)
        ).where(Article.id>cursor).limit(10)
        result=await self.session.execute(stmt)
        articles=result.scalars().all()
        
        next_cursor=None
        if articles:
            last_article=articles[-1] 
            next_cursor=last_article.id 
        
        has_more=len(articles)==10 
        model=schemas.GetAllPaginated(
            next_cursor=next_cursor,
            has_more=has_more,
            items=articles
        )
        return model
        

#Funcion para guardar un artículo

    async def save(self,article:Article):

        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def delete(self,article:Article):
        try:
            await self.session.delete(article)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
        
        
    #Función para buscar según filtros
    async def search_by_filters(self, model:schemas.SearchByFilters,cursor:int=0):
        #Lista donde guardaremos los filtros que nos llegue del cliente
        filters=[]

        #Verificamos los campos con valores
        if model.autor_id:
            filters.append(Article.autor_id==model.autor_id)
        
        if model.title:
            filters.append(Article.title.ilike(f"%{model.title}%"))

        if model.tags:
            for tag in model.tags:
                filters.append(Article.tags.any(Tags.name == tag))
            

        #Hacemos la consulta según los campos recibidos y devolvemos los resultados paginados
        stmt=select(Article).options(
            selectinload(Article.pics),
            selectinload(Article.tags)
        ).where(and_(
            *filters,
            Article.id>cursor

        )).limit(10)
        result=await self.session.execute(stmt)
        articles=result.scalars().all()
        next_cursor=None
        if articles:
            last_article=articles[-1]
            next_cursor=last_article.id
        has_more=len(articles)==10

        final_model=schemas.GetAllPaginated(
            next_cursor=next_cursor,
            has_more=has_more,
            items=articles
        )
        return final_model

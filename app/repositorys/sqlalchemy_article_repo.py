from sqlalchemy.orm import selectinload, load_only
from sqlalchemy import select,and_,func
import app.schemas as schemas
from app.database.models import Article,Tags,Writer,Like
from app.repositorys.article_repository import ArticleRepo
from sqlalchemy.ext.asyncio import AsyncSession

class SqlalchemyArticleRepo(ArticleRepo):
    def __init__(self, session:AsyncSession):
        self.session=session
    #Funcion para obtener un artículo
    async def get_by_id(self,id:int):
        stmt=select(Article).options(
            selectinload(Article.pics),
            selectinload(Article.tags).load_only(Tags.name),
            selectinload(Article.comments),
            selectinload(Article.likes),

            selectinload(Article.autor).load_only(Writer.firstname, Writer.lastname, Writer.bio, Writer.profile_pic)
            
            
            ).where(Article.id==id)

        result= await self.session.execute(stmt)
        article=result.scalar_one_or_none()
        
        return article

    #Función para obtener un artículo por su títutlo exacto
    async def get_by_title(self,title:str):
        stmt=select(Article).options(selectinload(Article.autor).load_only(Writer.firstname, Writer.lastname, Writer.bio)).where(Article.title==title).order_by(Article.date)
        result=await self.session.execute(stmt)
        article=result.scalar_one_or_none()
        return article
    
    #Función para obtener todos los artículos , utilizando paginación por cursor
    async def get_all(self, cursor:int=0):
        stmt=select(Article).options(
            selectinload(Article.pics),
            selectinload(Article.tags),
            selectinload(Article.comments),
            selectinload(Article.likes),

            selectinload(Article.autor).load_only(Writer.firstname, Writer.lastname, Writer.bio)
        ).where(Article.id>cursor).order_by( Article.id,Article.date).limit(10)
        result=await self.session.execute(stmt)
        articles=result.scalars().all()
        
        next_cursor=None
        if articles:
            last_article=articles[-1] 
            next_cursor=last_article.id if len(articles)==10 else None
        
        has_more=len(articles)==10 
        model=schemas.GetAllPaginated(
            next_cursor=next_cursor,
            has_more=has_more,
            items=articles
        )
        return model
        

#Funcion para guardar un artículo

    async def save(self,obj):

        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def commit_(self):
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"No se ha podido hacer commit, error :{str(e)}")
        


    async def delete(self,obj):
        try:
            await self.session.delete(obj)
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
            selectinload(Article.tags),
            selectinload(Article.comments),
            selectinload(Article.likes),

            selectinload(Article.autor).load_only(Writer.firstname, Writer.lastname, Writer.bio)
        ).where(and_(
            *filters,
            Article.id>cursor

        )).limit(10)
        result=await self.session.execute(stmt)
        articles=result.scalars().all()
        next_cursor=None
        if articles:
            last_article=articles[-1]
            if len(articles)==10:
                next_cursor=last_article.id 
            else:
                next_cursor=None
        has_more=len(articles)==10

        final_model=schemas.GetAllPaginated(
            next_cursor=next_cursor,
            has_more=has_more,
            items=articles
        )
        return final_model

    async def get_like(self, user_id:int, article_id:int):
        stmt=select(Like).where(and_(
            Like.article_id==article_id,
            Like.user_id==user_id
        ))

        result=await self.session.execute(stmt)
        like= result.scalar_one_or_none()
        return like
    
    async def get_favorites(self):
        stmt=select(Article).options(
            selectinload(Article.pics),
            selectinload(Article.tags)
        ).where(Article.in_favorites==True)
        result=await self.session.execute(stmt)
        articles=result.scalars().all()
        return articles
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func,and_
import schemas
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Article,Pics,Tags
from fastapi.responses import JSONResponse
from pattern_repository import ArticleRepo
from math import ceil

class SqlalchemyArticleRepo(ArticleRepo):
    async def get_all_tags(self):
        stmt=select(Tags)
        result=await self.session.execute(stmt)
        tags=result.scalars().all()
        
        return tags

    async def get_by_id(self,id:int):
        stmt=select(Article).options(selectinload(
            Article.pics,),
            selectinload(Article.tags)
            
            ).where(Article.id==id)

        result= await self.session.execute(stmt)
        article=result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="No se ha encontrado este artículo")
        return article

    
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
        


#Funcion para crear un artículo

    async def create_article(self,model:schemas.CreateArticle):
        
        article=Article(
            title=model.title,
            content=model.content,
            autor_id=model.autor_id,
            
            
        )

        if model.tags:
            tags_existing=await self.get_all_tags()
            tags_names=[tag.name for tag in tags_existing]

            for tag in model.tags:
                if tag not in tags_names:
                    raise HTTPException(status_code=409, detail="Hubo problemas con las etiquetas enviadas")
            for tg in tags_existing:
                if tg.name in model.tags:
                    article.tags.append(tg)
        

        if model.pics:
        
            for pic in model.pics:
                new_pic=Pics(link=pic)
                article.pics.append(new_pic)
        
        flag=await self.get_by_title(article.title)
        if flag:
            raise HTTPException(status_code=400, detail="Ya existe un artículo con ese título")
        
        try:
            self.session.add(article)
            await self.session.commit()
            return JSONResponse(content="Artíclo publicado exitosamente", status_code=201)
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"No se pudo crear el artículo, error: {str(e)}")
        

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
    
    async def create_tag(self, model:schemas.CreateTag):
        tag=Tags(
            name=model.name
        )
        self.session.add(tag)
        await self.session.commit()
        